"""Ingest an invoice file, work out its effective fields, name it and file it; re-file after changes.

The effective value of every field is: what an admin set by hand (overrides) > what the extractor found.
The payment date is resolved in this order (first that applies wins):
    manual         an admin marked it paid on a date
    bank           a matching outgoing payment in an imported bank statement
    invoice        the document states the payment date ("Date paid", "Fizetés dátuma")
    supplier_rule  the supplier is set up as auto-charged (paid_on = issue_date / due_date / fulfilment_date)
    payment_method card / cash / PayPal / online payment: paid on the issue date
    paid_stamp     the document says it is paid ("PAID", "Fizetve", a receipt): paid on the issue date
    direct_debit   collected on the due date
    expected_*     not confirmed: the due date (or issue date + payment terms, or the issue date) is only
                   the expected payment date; with payment.unconfirmed = hold the invoice waits in the
                   unpaid folder until one of the above confirms it.
"""
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path, PurePosixPath

from . import db as dbm
from . import extract as X
from . import suppliers as S
from . import textract
from .util import (dec_str, jload, now_iso, parse_amount_input, parse_date, safe_component, sha256_bytes,
                   to_date, iso)

FIELDS = ('supplier', 'invoice_number', 'issue_date', 'fulfilment_date', 'due_date', 'payment_method',
          'amount', 'currency', 'doc_type')
DATE_FIELDS = ('issue_date', 'fulfilment_date', 'due_date', 'payment_date')
METHODS = ('transfer', 'card', 'cash', 'paypal', 'direct_debit', 'cod', 'online')
DOC_TYPES = ('invoice', 'receipt', 'credit_note', 'proforma', 'unknown')
CONFIRMED_SOURCES = ('manual', 'bank', 'invoice', 'supplier_rule', 'payment_method', 'paid_stamp', 'direct_debit')
SOURCE_LABELS = {
    'manual': 'marked paid by an admin', 'bank': 'matched in a bank statement',
    'invoice': 'payment date printed on the invoice', 'supplier_rule': "supplier's payment rule",
    'payment_method': 'paid by card/cash/online on the issue date', 'paid_stamp': 'marked as paid on the invoice',
    'direct_debit': 'direct debit on the due date', 'expected_due': 'expected: due date',
    'expected_terms': 'expected: issue date + payment terms', 'expected_issue': 'expected: issue date',
}


# ------------------------------------------------------------------ effective values
def resolve_payment(cfg, ex, ov, eff, bank_date=None, rule=None):
    """(payment_date ISO, source, confirmed)."""
    if ov.get('payment_date'):
        return ov['payment_date'], 'manual', True
    if bank_date:
        return bank_date, 'bank', True
    if not ov.get('unpaid'):
        if ex.get('paid_date'):
            return ex['paid_date'], 'invoice', True
        if rule in ('issue_date', 'due_date', 'fulfilment_date') and eff.get(rule):
            return eff[rule], 'supplier_rule', True
        method = eff.get('payment_method')
        pay = cfg['payment']
        when = eff.get('issue_date') or eff.get('fulfilment_date')
        if method in pay.get('immediate_methods', ()) and when:
            return when, 'payment_method', True
        if method == 'cod' and (eff.get('fulfilment_date') or when):
            return eff.get('fulfilment_date') or when, 'payment_method', True
        if ex.get('paid_stamp') and when:
            return when, 'paid_stamp', True
        if method == 'direct_debit' and pay.get('direct_debit_on_due_date', True) and eff.get('due_date'):
            return eff['due_date'], 'direct_debit', True
    if eff.get('due_date'):
        return eff['due_date'], 'expected_due', False
    if ex.get('terms_days') and eff.get('issue_date'):
        d = to_date(eff['issue_date']) + timedelta(days=int(ex['terms_days']))
        return d.isoformat(), 'expected_terms', False
    if eff.get('issue_date'):
        return eff['issue_date'], 'expected_issue', False
    if eff.get('fulfilment_date'):
        return eff['fulfilment_date'], 'expected_issue', False
    return None, None, False


def _issue(code, level, msg):
    return {'code': code, 'level': level, 'msg': msg}


def evaluate(cfg, ex, ov, eff, pay_date, text_method, duplicate_of=None):
    """(status, issues)."""
    issues = []
    if text_method == 'none':
        issues.append(_issue('no_text', 'error', 'No text could be read (a scan or photo). Type the fields in, '
                                                 'or install OCR (tesseract) and re-extract.'))
    elif text_method == 'encrypted':
        issues.append(_issue('encrypted', 'error', 'The PDF is password-protected: type the fields in.'))
    elif text_method == 'ocr':
        issues.append(_issue('ocr', 'warn', 'Read with OCR: check the fields.'))
    if not eff.get('supplier'):
        issues.append(_issue('missing_supplier', 'error', 'Supplier not found.'))
    if not eff.get('invoice_number'):
        issues.append(_issue('missing_number', 'error', 'Invoice number not found.'))
    if eff.get('amount') in (None, ''):
        issues.append(_issue('missing_amount', 'error', 'Total amount not found.'))
    if not pay_date:
        issues.append(_issue('missing_date', 'error', 'No invoice date found.'))
    if ex.get('own_company_is_seller') and 'supplier' not in ov:
        issues.append(_issue('own_invoice', 'error', 'This looks like an invoice issued BY your company '
                                                     '(a sales invoice), not one you received.'))
    conf = ex.get('confidence') or {}
    if 'supplier' not in ov and eff.get('supplier'):
        c = conf.get('supplier', 0)
        if c < 0.45:
            issues.append(_issue('uncertain_supplier', 'error', f'Supplier "{eff["supplier"]}" is a guess.'))
        elif c < 0.65:
            issues.append(_issue('check_supplier', 'warn', f'Check the supplier ("{eff["supplier"]}").'))
    for field, label in (('invoice_number', 'invoice number'), ('amount', 'amount')):
        if field not in ov and eff.get(field) not in (None, '') and conf.get(field, 1) < 0.6:
            issues.append(_issue(f'check_{field}', 'warn', f'Check the {label}.'))
    if 'issue_date' not in ov and eff.get('issue_date') and conf.get('issue_date', 1) < 0.5:
        issues.append(_issue('check_issue_date', 'warn', 'Check the invoice date.'))
    if ov.get('status') == 'ignored':
        return 'ignored', issues
    if duplicate_of:
        issues.insert(0, _issue('duplicate', 'info', f'Same supplier and invoice number as invoice #{duplicate_of}.'))
        return 'duplicate', issues
    if eff.get('doc_type') == 'proforma':
        issues.insert(0, _issue('proforma', 'info', 'A proforma / payment request (díjbekérő) or quote, not an '
                                                    'invoice. Kept under other documents.'))
        return 'ignored', issues
    if any(i['level'] == 'error' for i in issues):
        return 'review', issues
    return 'filed', issues


def supplier_rule(con, name):
    if not name:
        return None
    r = con.execute('SELECT paid_on FROM suppliers WHERE name = ?', (name,)).fetchone()
    return r['paid_on'] if r else None


def bank_date(con, txn_id):
    if not txn_id:
        return None
    r = con.execute('SELECT date FROM bank_txns WHERE id = ?', (txn_id,)).fetchone()
    return r['date'] if r else None


def _norm_number(n):
    return re.sub(r'[^0-9a-z]', '', (n or '').lower())


def find_duplicate(con, inv_id, supplier, number):
    if not supplier or not number:
        return None
    key = _norm_number(number)
    for r in con.execute("SELECT id, invoice_number FROM invoices WHERE supplier = ? AND status != 'duplicate' "
                         "AND id != ? ORDER BY id", (supplier, inv_id or -1)).fetchall():
        if _norm_number(r['invoice_number']) == key:
            return r['id']
    return None


def compute(bot, con, inv):
    """Effective columns for an invoice row (dict with extracted/overrides/bank_txn_id/...)."""
    ex, ov = inv.get('extracted') or {}, inv.get('overrides') or {}
    eff = {f: ov.get(f, ex.get(f)) for f in FIELDS}
    rule = supplier_rule(con, eff['supplier'])
    pay_date, source, paid = resolve_payment(bot.cfg, ex, ov, eff, bank_date(con, inv.get('bank_txn_id')), rule)
    dup = None
    if ov.get('status') != 'ignored' and not ov.get('not_duplicate'):
        dup = find_duplicate(con, inv.get('id'), eff['supplier'], eff['invoice_number'])
        if dup and inv.get('id') and dup > inv['id']:
            dup = None  # the older record is the original
    status, issues = evaluate(bot.cfg, ex, ov, eff, pay_date, inv.get('text_method'), dup)
    conf = dict(ex.get('confidence') or {})
    for f in ov:
        if f in conf:
            conf[f] = 1.0
    out = dict(eff)
    out.update({
        'supplier_raw': ex.get('supplier_raw'),
        'supplier_tax_id': ex.get('supplier_tax_id'),
        'payment_date': pay_date,
        'payment_source': source,
        'paid': 1 if paid else 0,
        'status': status,
        'duplicate_of': dup,
        'issues': issues,
        'confidence': conf,
    })
    return out


# ------------------------------------------------------------------ names and folders
def file_name(bot, inv, ext):
    n = bot.cfg['naming']
    asc, sp = n.get('ascii', True), n.get('space', '-')
    fields = {
        'date': inv.get('payment_date') or '',
        'payment_date': inv.get('payment_date') or '',
        'issue_date': inv.get('issue_date') or '',
        'due_date': inv.get('due_date') or '',
        'supplier': safe_component(inv.get('supplier'), n.get('max_supplier', 40), asc, sp) or 'Unknown',
        'number': safe_component(inv.get('invoice_number'), n.get('max_number', 40), asc, sp) or 'no-number',
        'amount': (inv.get('amount') or '').replace('.00', ''),
        'currency': inv.get('currency') or '',
    }
    try:
        stem = n.get('pattern', '{date}_{supplier}_{number}').format(**fields)
    except (KeyError, IndexError, ValueError):
        stem = '{date}_{supplier}_{number}'.format(**fields)
    stem = re.sub(r'[\\/:*?"<>|]+', '-', stem)
    stem = re.sub(r'_+', '_', stem).strip('_ .')
    return stem + ext


def folder_for(bot, inv):
    F = bot.cfg['folders']
    status = inv['status']
    if status == 'review':
        return F['review']
    if status == 'duplicate':
        return F['duplicates']
    if status == 'ignored':
        return F['other']
    if not inv.get('paid') and bot.cfg['payment'].get('unconfirmed', 'hold') == 'hold':
        return F['unpaid']
    y, m, d = inv['payment_date'].split('-')
    return F['layout'].format(yyyy=y, mm=m, dd=d, yy=y[2:])


def _ext(inv):
    ext = PurePosixPath(inv.get('file_path') or inv.get('original_name') or '').suffix.lower()
    return ext if ext in ('.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff') else '.pdf'


def target_path(bot, con, inv):
    folder = folder_for(bot, inv)
    ext = _ext(inv)
    if inv['status'] in ('review', 'duplicate', 'ignored'):
        stem = PurePosixPath(inv.get('original_name') or 'invoice').stem
        name = f"{inv['id']}_{safe_component(stem, 60) or 'invoice'}{ext}"
    else:
        name = file_name(bot, inv, ext)
    rel = f'{folder}/{name}'
    root = bot.archive.resolve()
    if root not in (bot.archive / rel).resolve().parents:
        raise ValueError(f'the folder settings put invoice #{inv["id"]} outside the archive ({rel})')
    base, k = rel[:-len(ext)], 2
    current = (inv.get('file_path') or '').lower()
    while True:
        taken = con.execute('SELECT 1 FROM invoices WHERE lower(file_path) = lower(?) AND id != ?',
                            (rel, inv['id'])).fetchone()
        exists_other = (bot.archive / rel).exists() and rel.lower() != current
        if not taken and not exists_other:
            return rel
        rel = f'{base}_{k}{ext}'
        k += 1


def _prune_empty(bot, d):
    root = bot.archive.resolve()
    d = Path(d).resolve()
    while d != root and root in d.parents:
        try:
            d.rmdir()
        except OSError:
            break
        d = d.parent


class Journal:
    """File moves made inside a ledger transaction. If the transaction fails or does not commit, every
    move is undone in reverse order, so the ledger and the archive never disagree."""

    def __init__(self, bot):
        self.bot = bot
        self.moves = []

    def move(self, src, dst):
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        self.moves.append((Path(src), Path(dst)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            for src, _ in self.moves:
                _prune_empty(self.bot, src.parent)
            return False
        for src, dst in reversed(self.moves):
            try:
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
                _prune_empty(self.bot, dst.parent)
            except OSError:
                self.bot.log.exception('could not undo the move %s -> %s', src, dst)
        return False


@contextmanager
def transaction(bot, con):
    """`with transaction(bot, con) as journal:` one ledger transaction; file moves made through the
    journal are undone if it raises or the commit fails."""
    with Journal(bot) as journal:
        with con:
            yield journal


def move_into_place(bot, con, inv, journal, touched=None):
    """Rename/move the archived file to where the invoice's current state says it belongs."""
    new_rel = target_path(bot, con, inv)
    old_rel = inv.get('file_path') or ''
    if new_rel == old_rel:
        return old_rel
    src = bot.archive / old_rel
    if not old_rel or not src.is_file():
        # never point the ledger at a file that is not there; `verify --fix` finds it by its content
        bot.log.warning('invoice #%s: file %r is missing, not moved', inv['id'], old_rel)
        return old_rel
    journal.move(src, bot.archive / new_rel)
    if touched is not None:
        touched.update({str(PurePosixPath(old_rel).parent), str(PurePosixPath(new_rel).parent)})
    dbm.update_invoice(con, inv['id'], {'file_path': new_rel})
    dbm.log_event(con, 'moved', inv['id'], 'bot', {'from': old_rel, 'to': new_rel})
    inv['file_path'] = new_rel
    return new_rel


def recompute_and_file(bot, con, inv_id, journal, touched=None):
    inv = dbm.get_invoice(con, inv_id)
    eff = compute(bot, con, inv)
    changed = {k: v for k, v in eff.items() if inv.get(k) != v}
    if changed:
        dbm.update_invoice(con, inv_id, changed)
        inv.update(changed)
    move_into_place(bot, con, inv, journal, touched)
    return inv


# ------------------------------------------------------------------ ingest
def ingest(bot, data, name, source, meta=None, actor='bot', require_invoice=False, touched=None):
    """Store one PDF/image as a new invoice. Returns a result dict for reports."""
    kind = textract.sniff(data, name)
    if kind not in ('pdf', 'image'):
        return {'result': 'skipped', 'name': name, 'reason': 'not a PDF or image'}
    if kind == 'image' and source == 'imap' and not bot.cfg['collect'].get('include_images'):
        return {'result': 'skipped', 'name': name, 'reason': 'image attachment (collect.include_images is off)'}
    sha = sha256_bytes(data)
    ext = '.pdf'
    if kind == 'image':
        ext = {b'\xff\xd8': '.jpg', b'\x89P': '.png'}.get(data[:2], '.tif')
    con = bot.db()
    try:
        row = con.execute('SELECT id FROM invoices WHERE sha256 = ?', (sha,)).fetchone()
        if row:
            return {'result': 'duplicate_file', 'name': name, 'id': row['id']}
        tmpdir = bot.home / 'tmp'
        tmpdir.mkdir(exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=ext, dir=tmpdir)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
            # reading the file (pdftotext, OCR) can be slow: done before taking the files lock
            text, method = textract.extract_text(tmp, kind, bot.cfg)
            ex = X.extract(text, meta, bot.company, S.Registry(con), bot.cfg['default_currency'],
                           bot.cfg['date_order'])
            if require_invoice and (ex['invoice_score'] < bot.cfg['collect'].get('min_invoice_score', 2)
                                    or ex['doc_type'] == 'unknown' and ex['invoice_score'] < 3):
                return {'result': 'skipped', 'name': name, 'reason': 'does not look like an invoice',
                        'score': ex['invoice_score']}
            with bot.files_lock:
                row = con.execute('SELECT id FROM invoices WHERE sha256 = ?', (sha,)).fetchone()
                if row:
                    return {'result': 'duplicate_file', 'name': name, 'id': row['id']}
                now = now_iso()
                with transaction(bot, con) as journal:
                    inv_id = dbm.insert_invoice(con, {
                        'sha256': sha, 'file_path': '', 'original_name': name, 'source': source,
                        'source_detail': meta or {}, 'received_at': now, 'status': 'review',
                        'extracted': ex, 'overrides': {}, 'text': text, 'text_method': method,
                        'created_at': now, 'updated_at': now})
                    inv = dbm.get_invoice(con, inv_id)
                    eff = compute(bot, con, inv)
                    dbm.update_invoice(con, inv_id, eff)
                    inv.update(eff)
                    rel = target_path(bot, con, inv)
                    journal.move(tmp, bot.archive / rel)
                    dbm.update_invoice(con, inv_id, {'file_path': rel})
                    dbm.log_event(con, 'added', inv_id, actor, {'source': source, 'name': name, 'file': rel,
                                                               'status': inv['status']})
                    _auto_bank_match(bot, con, inv_id, journal, touched)
                inv = dbm.get_invoice(con, inv_id)
            if touched is not None:
                touched.add(str(PurePosixPath(inv['file_path']).parent))
            return {'result': 'new', **summary(inv)}
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    finally:
        con.close()


def _auto_bank_match(bot, con, inv_id, journal, touched=None):
    """A payment imported earlier may already confirm this new invoice."""
    from . import bank
    inv = dbm.get_invoice(con, inv_id)
    if inv['status'] != 'filed' or inv['paid'] and inv['payment_source'] in ('manual', 'bank'):
        return
    m = bank.best_match_for_invoice(bot, con, inv)
    if m and m['auto']:
        bank.link(bot, con, inv_id, m['txn']['id'], m['score'], journal, actor='bot', touched=touched)


def summary(inv):
    return {k: inv.get(k) for k in ('id', 'status', 'paid', 'file_path', 'supplier', 'invoice_number', 'amount',
                                    'currency', 'issue_date', 'due_date', 'payment_date', 'payment_source',
                                    'original_name')} | {'issues': [i['msg'] for i in inv.get('issues') or []
                                                                    if i['level'] != 'info']}


# ------------------------------------------------------------------ changes
def clean_changes(changes):
    """Validate admin input. Empty string / None means: drop the override (back to what was extracted)."""
    out = {}
    for k, v in changes.items():
        if isinstance(v, str):
            v = v.strip()
        if v in (None, ''):
            out[k] = None
            continue
        if k in ('issue_date', 'fulfilment_date', 'due_date', 'payment_date'):
            d = parse_date(v)
            if not d:
                raise ValueError(f'{k}: not a date: {v!r} (use YYYY-MM-DD)')
            out[k] = d.isoformat()
        elif k == 'amount':
            a = parse_amount_input(str(v))
            if a is None or dec_str(a) is None or abs(a) >= 10 ** 13:
                raise ValueError(f'amount: not a number: {v!r}')
            out[k] = dec_str(a)
        elif k == 'currency':
            v = str(v).upper()
            if not re.fullmatch(r'[A-Z]{3}', v):
                raise ValueError(f'currency: use a 3-letter code like HUF, EUR, USD (got {v!r})')
            out[k] = v
        elif k == 'payment_method':
            if v not in METHODS:
                raise ValueError(f'payment_method: one of {", ".join(METHODS)}')
            out[k] = v
        elif k == 'doc_type':
            if v not in DOC_TYPES:
                raise ValueError(f'doc_type: one of {", ".join(DOC_TYPES)}')
            out[k] = v
        elif k in ('supplier', 'invoice_number'):
            v = ' '.join(str(v).split())
            if len(v) > 120:
                raise ValueError(f'{k}: too long')
            out[k] = v
        elif k in ('status', 'unpaid', 'not_duplicate', 'note'):
            out[k] = v
        else:
            raise ValueError(f'unknown field {k}')
    return out


def update(bot, inv_id, changes, actor='admin', verify=False, learn=True):
    """Apply admin changes (see clean_changes), re-resolve payment, rename/move the file."""
    changes = clean_changes(changes)
    touched = set()
    with bot.files_lock:
        con = bot.db()
        try:
            with transaction(bot, con) as journal:
                inv = dbm.get_invoice(con, inv_id)
                if inv is None:
                    raise KeyError(f'no invoice #{inv_id}')
                ov = dict(inv['overrides'] or {})
                before = {k: inv.get(k) for k in FIELDS + ('payment_date', 'paid', 'status')}
                for k, v in changes.items():
                    if v is None:
                        ov.pop(k, None)
                    else:
                        ov[k] = v
                if changes.get('payment_date'):
                    ov.pop('unpaid', None)
                if changes.get('unpaid'):
                    ov.pop('payment_date', None)
                    ov['unpaid'] = True
                    if inv.get('bank_txn_id'):
                        # the admin says this payment was not for this invoice: never match them again
                        con.execute("UPDATE bank_txns SET invoice_id = NULL, status = 'unmatched', score = NULL "
                                    'WHERE id = ?', (inv['bank_txn_id'],))
                        rejected = dbm.meta_get(con, 'bank_rejected', [])
                        rejected.append([inv_id, inv['bank_txn_id']])
                        dbm.meta_set(con, 'bank_rejected', rejected)
                        dbm.update_invoice(con, inv_id, {'bank_txn_id': None})
                fields = {'overrides': ov}
                if verify:
                    fields['verified'] = 1
                dbm.update_invoice(con, inv_id, fields)
                inv = recompute_and_file(bot, con, inv_id, journal, touched)
                after = {k: inv.get(k) for k in before}
                diff = {k: [before[k], after[k]] for k in before if before[k] != after[k]}
                dbm.log_event(con, 'updated', inv_id, actor, {'set': changes, 'changed': diff})
                if learn and changes.get('supplier'):
                    _learn_supplier(bot, con, inv, changes['supplier'])
            _write_summaries(bot, touched)
            return dbm.get_invoice(con, inv_id)
        finally:
            con.close()


def _learn_supplier(bot, con, inv, name):
    """Remember what a supplier correction teaches, but only when it is a better name for the company
    that was read: correcting a misread company must not make it an alias of another one."""
    ex = inv.get('extracted') or {}
    own = X.Own(bot.company)
    raw = ex.get('supplier_raw')
    domain = ex.get('sender_domain')
    domain = domain if domain and domain not in own.domains and S.related_names(domain.split('.')[0], name) else None
    if raw and S.related_names(raw, name):
        S.learn(con, name, raw_name=raw, tax_ids=[ex['supplier_tax_id']] if ex.get('supplier_tax_id') else [],
                domain=ex.get('sender_domain') if ex.get('sender_domain') not in own.domains else None,
                own_cores=own.tax)
    else:
        S.learn(con, name, domain=domain, own_cores=own.tax)


def mark_paid(bot, inv_id, date=None, actor='admin'):
    from .util import today
    return update(bot, inv_id, {'payment_date': date or today().isoformat()}, actor=actor)


def mark_unpaid(bot, inv_id, actor='admin'):
    return update(bot, inv_id, {'payment_date': None, 'unpaid': True}, actor=actor)


def reextract(bot, inv_id, actor='admin'):
    """Read the file again with the current rules and suppliers (admin overrides are kept)."""
    con = bot.db()
    try:
        inv = dbm.get_invoice(con, inv_id)
        if inv is None:
            raise KeyError(f'no invoice #{inv_id}')
        path = bot.archive / inv['file_path']
        kind = textract.sniff(path.read_bytes()[:2048], path.name) or 'pdf'
        text, method = textract.extract_text(path, kind, bot.cfg)
        ex = X.extract(text, inv['source_detail'], bot.company, S.Registry(con),
                       bot.cfg['default_currency'], bot.cfg['date_order'])
        touched = set()
        with bot.files_lock:
            with transaction(bot, con) as journal:
                dbm.update_invoice(con, inv_id, {'extracted': ex, 'text': text, 'text_method': method})
                inv = recompute_and_file(bot, con, inv_id, journal, touched)
                dbm.log_event(con, 'reextracted', inv_id, actor, {'status': inv['status']})
        _write_summaries(bot, touched)
        return inv
    finally:
        con.close()


def refile_all(bot, where='1=1', params=()):
    """Recompute and move every matching invoice (after config or supplier-rule changes), one
    transaction per invoice so a failure leaves every other invoice consistent.
    Returns (re-filed count, [error messages])."""
    touched, errors, done = set(), [], 0
    with bot.files_lock:
        con = bot.db()
        try:
            ids = [r['id'] for r in con.execute(f'SELECT id FROM invoices WHERE {where} ORDER BY id', params)]
            for i in ids:
                try:
                    with transaction(bot, con) as journal:
                        recompute_and_file(bot, con, i, journal, touched)
                    done += 1
                except Exception as e:  # e.g. a PDF held open by another program on Windows
                    bot.log.exception('re-filing invoice #%s failed', i)
                    errors.append(f'invoice #{i}: {e}')
        finally:
            con.close()
    _write_summaries(bot, touched)
    return done, errors


def find_problems(bot):
    """[(kind, invoice id, path)]: 'missing' = in the ledger but not in the archive,
    'stray' = in the archive but not in the ledger."""
    con = bot.db()
    try:
        rows = con.execute('SELECT id, file_path FROM invoices ORDER BY id').fetchall()
    finally:
        con.close()
    out, known = [], set()
    for r in rows:
        p = bot.archive / (r['file_path'] or '')
        if r['file_path'] and p.is_file():
            known.add(str(p.resolve()))
        else:
            out.append(('missing', r['id'], r['file_path']))
    for p in sorted(bot.archive.rglob('*')):
        if p.is_file() and not p.name.startswith(('.', '_summary')) and str(p.resolve()) not in known:
            out.append(('stray', None, p.relative_to(bot.archive).as_posix()))
    return out


def repair(bot):
    """Make the ledger and the archive agree: re-attach files that were moved by hand or left behind
    by a crash (recognised by their content), then re-file every invoice. Returns (adopted, re-filed,
    errors)."""
    adopted = 0
    with bot.files_lock:
        problems = find_problems(bot)
        missing = [p[1] for p in problems if p[0] == 'missing']
        strays = [bot.archive / p[2] for p in problems if p[0] == 'stray']
        if missing and strays:
            by_sha = {}
            for f in strays:
                try:
                    by_sha.setdefault(sha256_bytes(f.read_bytes()), f)
                except OSError:
                    continue
            con = bot.db()
            try:
                for inv_id in missing:
                    sha = con.execute('SELECT sha256 FROM invoices WHERE id = ?', (inv_id,)).fetchone()['sha256']
                    f = by_sha.pop(sha, None)
                    if f is None:
                        continue
                    rel = f.relative_to(bot.archive).as_posix()
                    with con:
                        dbm.update_invoice(con, inv_id, {'file_path': rel})
                        dbm.log_event(con, 'adopted', inv_id, 'bot', {'file': rel})
                    adopted += 1
            finally:
                con.close()
        done, errors = refile_all(bot)
    return adopted, done, errors


def _write_summaries(bot, folders):
    if not folders or not bot.cfg.get('month_summaries', True):
        return
    from . import export
    export.write_folder_summaries(bot, folders)
