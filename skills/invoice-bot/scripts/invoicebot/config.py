"""The bot's home folder, its configuration (invoicebot.json) and the Bot context passed around.

Home layout (all names configurable except the first three):
    invoicebot.json   configuration
    invoicebot.db     the ledger (SQLite) - keep it on a local disk, not in a synced folder
    logs/             invoicebot.log
    inbox/            drop folder: anything put here is collected on the next run
    archive/          the organised invoices: <yyyy>/<yyyy>-<mm>/<date>_<Supplier>_<Number>.pdf
    exports/          ZIP and CSV files made for downloads
"""
import copy
import json
import logging
import logging.handlers
import os
from pathlib import Path

from . import db as dbm
from .util import FileLock

CONFIG_NAME = 'invoicebot.json'
DB_NAME = 'invoicebot.db'

DEFAULTS = {
    # Your own company, so it is never mistaken for the supplier (it is the buyer on every invoice).
    'company': {'name': '', 'aliases': [], 'tax_ids': [], 'email_domains': []},
    'archive_dir': 'archive',
    'inbox_dir': 'inbox',
    'exports_dir': 'exports',
    'default_currency': 'HUF',
    # Order for dates like 05/10/2026 when the document itself gives no hint: DMY (Europe) or MDY (US).
    'date_order': 'DMY',
    'naming': {
        # Fields: {date} (payment date, or the expected one for unpaid invoices), {supplier}, {number},
        # {issue_date}, {due_date}, {amount}, {currency}
        'pattern': '{date}_{supplier}_{number}',
        'ascii': True,           # transliterate accents in file names (Számlázz -> Szamlazz)
        'space': '-',            # what replaces spaces inside a field
        'max_supplier': 40,
        'max_number': 40,
    },
    'folders': {
        'layout': '{yyyy}/{yyyy}-{mm}',   # month folders by PAYMENT date
        'unpaid': '_unpaid',
        'review': '_review',
        'duplicates': '_duplicates',
        'other': '_other',
    },
    'payment': {
        # What to do with an invoice whose payment is not confirmed yet:
        #   hold     - keep it in the unpaid folder until it is paid (bank match, admin, rule)
        #   estimate - file it in the month of its due date and flag it as estimated
        'unconfirmed': 'hold',
        # Payment methods that mean the invoice was paid when it was issued.
        'immediate_methods': ['card', 'cash', 'paypal', 'online'],
        # Direct debit (csoportos beszedés) is taken on the due date.
        'direct_debit_on_due_date': True,
    },
    'collect': {
        'include_images': False,     # also take JPG/PNG attachments (needs OCR or manual entry)
        'max_attachment_mb': 25,
        'min_invoice_score': 2,      # how sure an e-mail attachment must look like an invoice to be kept
    },
    'imap': {
        'enabled': False,
        'host': '',
        'port': 993,
        'ssl': True,
        'username': '',
        'password_env': 'INVOICEBOT_IMAP_PASSWORD',
        'password_file': '',         # alternative: a file holding only the password (chmod 600)
        'folders': ['INBOX'],
        'lookback_days': 45,
        'search': '',                # extra IMAP SEARCH criteria, e.g. 'FROM "billing@example.com"'
        'gmail_query': '',           # Gmail only: e.g. 'has:attachment filename:pdf'
        'mark_seen': False,
        'gmail_label': '',           # Gmail only: label added to processed messages, e.g. 'Invoices/Processed'
        'only_from': [],
        'ignore_from': [],
    },
    'csv': {'delimiter': ',', 'decimal': '.'},
    'admin': {
        'host': '127.0.0.1',
        'port': 8765,
        'session_hours': 12,
        'secure_cookies': False,     # set true when the panel is served over HTTPS
        'collect_every_minutes': 0,  # >0: the admin server also runs collection on this interval
        'max_upload_mb': 50,
    },
    'month_summaries': True,         # write _summary.csv into each month folder
    'ocr': {'enabled': True, 'languages': 'hun+eng+deu'},
    'pdf_max_pages': 10,
}


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def default_home():
    env = os.environ.get('INVOICEBOT_HOME')
    return Path(env).expanduser() if env else Path.home() / 'InvoiceBot'


_CHOICES = {'payment.unconfirmed': ('hold', 'estimate'), 'date_order': ('DMY', 'MDY')}


def validate_option(dotted, value):
    """Refuse settings that would break naming or filing."""
    if dotted in _CHOICES and value not in _CHOICES[dotted]:
        raise ValueError(f'{dotted} must be one of: {", ".join(_CHOICES[dotted])}')
    if dotted == 'naming.space' and (not isinstance(value, str) or any(c in value for c in '_/\\:*?"<>|')):
        raise ValueError('naming.space cannot contain "_" (it separates the name fields) or path characters')
    if dotted == 'naming.pattern':
        if not isinstance(value, str) or '/' in value or '\\' in value or '{date}' not in value and '{payment_date}' not in value:
            raise ValueError('naming.pattern must contain {date} and no folder separators')
    if dotted.startswith('folders.') and not isinstance(value, str):
        raise ValueError(f'{dotted} must be a folder name')
    if dotted.startswith('folders.') and isinstance(value, str):
        parts = value.replace('\\', '/').split('/')
        if value.startswith(('/', '~')) or '..' in parts or ':' in value or not value.strip('/'):
            raise ValueError(f'{dotted} must be a relative folder inside the archive')
        if dotted == 'folders.layout' and '{yyyy}' not in value:
            raise ValueError('folders.layout must contain {yyyy} (and usually {mm})')
    if dotted in ('naming.max_supplier', 'naming.max_number') and not (isinstance(value, int) and 8 <= value <= 120):
        raise ValueError(f'{dotted} must be a number between 8 and 120')


_CHECKED = ('naming.space', 'naming.pattern', 'naming.max_supplier', 'naming.max_number', 'folders.layout',
            'folders.unpaid', 'folders.review', 'folders.duplicates', 'folders.other', 'payment.unconfirmed',
            'date_order')


def validate_config(cfg, path='invoicebot.json'):
    """Refuse to start with settings that would misname files or put them outside the archive."""
    for dotted in _CHECKED:
        node = cfg
        for k in dotted.split('.'):
            node = node.get(k) if isinstance(node, dict) else None
        try:
            validate_option(dotted, node)
        except ValueError as e:
            raise ValueError(f'{path}: {e}') from None
    names = [cfg['folders'][k].strip('/').lower() for k in ('unpaid', 'review', 'duplicates', 'other')]
    if len(set(names)) != len(names):
        raise ValueError(f'{path}: the unpaid, review, duplicates and other folders must all be different')


class Bot:
    """Home paths + configuration + database + logging. One per process (or per test)."""

    def __init__(self, home=None, create=False):
        self.home = Path(home).expanduser().resolve() if home else default_home().resolve()
        self.config_path = self.home / CONFIG_NAME
        if not self.config_path.exists() and not create:
            raise FileNotFoundError(
                f'No invoice bot set up in {self.home}. Run: invoice_bot.py --home "{self.home}" init')
        self.home.mkdir(parents=True, exist_ok=True)
        user = {}
        if self.config_path.exists():
            with open(self.config_path, encoding='utf-8') as f:
                user = json.load(f)
        self.user_config = user
        self.cfg = deep_merge(DEFAULTS, user)
        validate_config(self.cfg, self.config_path)
        self.db_path = self.home / DB_NAME
        self.archive = self._dir(self.cfg['archive_dir'])
        self.inbox = self._dir(self.cfg['inbox_dir'])
        self.exports = self._dir(self.cfg['exports_dir'])
        self.logs = self.home / 'logs'
        for d in (self.archive, self.inbox, self.exports, self.logs):
            d.mkdir(parents=True, exist_ok=True)
        self.log = self._logger()
        self.files_lock = FileLock(self.home / '.files.lock', timeout=60)
        self.run_lock = FileLock(self.home / '.run.lock', timeout=0)
        dbm.init(self.db_path)

    def _dir(self, p):
        p = Path(os.path.expandvars(str(p))).expanduser()
        return (p if p.is_absolute() else self.home / p).resolve()

    def _logger(self):
        log = logging.getLogger(f'invoicebot.{self.home}')
        if not log.handlers:
            log.setLevel(logging.INFO)
            h = logging.handlers.RotatingFileHandler(self.logs / 'invoicebot.log', maxBytes=1_000_000,
                                                     backupCount=5, encoding='utf-8')
            h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            log.addHandler(h)
            log.propagate = False
        return log

    def db(self):
        return dbm.connect(self.db_path)

    def save_config(self):
        validate_config(deep_merge(DEFAULTS, self.user_config), self.config_path)
        tmp = self.config_path.with_suffix('.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(self.user_config, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp, self.config_path)
        self.cfg = deep_merge(DEFAULTS, self.user_config)

    def set_option(self, dotted, value):
        validate_option(dotted, value)
        node = self.user_config
        keys = dotted.split('.')
        for k in keys[:-1]:
            node = node.setdefault(k, {})
            if not isinstance(node, dict):
                raise ValueError(f'{dotted}: {k} is not a section')
        node[keys[-1]] = value
        self.save_config()

    @property
    def company(self):
        return self.cfg['company']
