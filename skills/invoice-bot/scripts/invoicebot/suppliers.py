"""Supplier names: legal-form handling, the supplier registry and what the bot learns from corrections.

The registry maps the names, tax numbers and e-mail domains a supplier appears under to one canonical
name, so "Google Ireland Limited" and "Google Cloud EMEA Ltd" are both filed as "Google". Admin
corrections are remembered: fix a supplier once and the next invoice from them is named the same way.
A supplier can also carry a payment rule (paid_on) for suppliers that charge automatically.
"""
import json
import re
from email.utils import parseaddr
from pathlib import Path

from .util import fold, jdump, jload, now_iso

ASSETS = Path(__file__).resolve().parent / 'assets'

# ------------------------------------------------------------------ legal forms
_LEGAL_RX = [
    # Hungarian
    r'kft', r'k\.\s?f\.\s?t', r'bt', r'zrt', r'nyrt', r'kkt', r'rt', r'kht', r'e\.\s?v', r'ev',
    r'egyeni\s+vallalkozo', r'egyeni\s+ceg', r'nonprofit\s+kft', r'nonprofit\s+zrt',
    r'korlatolt\s+felelossegu\s+tarsasag', r'zartkoruen\s+mukodo\s+reszvenytarsasag',
    r'nyilvanosan\s+mukodo\s+reszvenytarsasag', r'beteti\s+tarsasag', r'kozkereseti\s+tarsasag',
    r'reszvenytarsasag', r'f\.\s?a', r'v\.\s?a', r'cs\.\s?a',
    # English
    r'ltd', r'limited', r'unlimited\s+company', r'llc', r'l\.\s?l\.\s?c', r'inc', r'incorporated',
    r'corp', r'corporation', r'co', r'company', r'plc', r'llp', r'pbc', r'uc', r'dac',
    # German, French, Benelux, Nordic, CEE, Asia-Pacific
    r'gmbh', r'ag', r'kg', r'ohg', r'ug', r'gbr', r'e\.\s?k', r'se', r'sa', r's\.\s?a', r'sarl',
    r's\.\s?a\.?\s?r\.\s?l', r'sas', r'srl', r's\.\s?r\.\s?l', r'spa', r's\.\s?p\.\s?a', r'sl', r's\.\s?l',
    r'bv', r'b\.\s?v', r'nv', r'n\.\s?v', r'ab', r'oy', r'oyj', r'as', r'a/s', r'aps', r's\.\s?r\.\s?o',
    r'sro', r'sp\.?\s?z\s?o\.?\s?o', r'd\.\s?o\.\s?o', r'doo', r'pty', r'pte', r'ou', r'uab', r'kk',
    r'sdn\s+bhd', r'bhd', r'&\s*co', r'and\s+co', r'und\s+co', r'&\s*co\.?\s*kg', r'gmbh\s*&\s*co\.?\s*kg',
    r'et\s+cie', r's\.\s?c\.\s?a', r'sca',
]
LEGAL_ALT = '(?:' + '|'.join(sorted(_LEGAL_RX, key=len, reverse=True)) + ')'
_TRAILING_LEGAL = re.compile(r'[\s,(]+' + LEGAL_ALT + r'\.?[\s.,)]*$')
LEGAL_END = re.compile(r'(?:^|[\s,(])' + LEGAL_ALT + r'\.?\)?\s*$')
_HU_LEGAL_END = re.compile(r'(?:^|[\s,(])(?:kft|bt|zrt|nyrt|kkt|e\.\s?v|ev|egyeni\s+vallalkozo|'
                           r'korlatolt\s+felelossegu\s+tarsasag|reszvenytarsasag|beteti\s+tarsasag)\.?\s*$')

# Activity words Hungarian company names carry before the legal form
# ("Kovács és Társa Szolgáltató és Kereskedelmi Kft." is filed as "Kovács és Társa").
_HU_ACTIVITY = {
    'szolgaltato', 'kereskedelmi', 'tanacsado', 'termelo', 'gyarto', 'fejleszto', 'informatikai', 'ipari',
    'epitoipari', 'tavkozlesi', 'beruhazo', 'vagyonkezelo', 'ingatlanforgalmazo', 'ingatlankezelo',
    'ingatlanhasznosito', 'fuvarozo', 'szallitmanyozo', 'vendeglato', 'oktato', 'oktatasi', 'konyvelo',
    'konyvviteli', 'nyomdaipari', 'energiakereskedelmi', 'szervezo', 'kivitelezo', 'forgalmazo',
    'kozvetito', 'uzemelteto', 'ertekesito', 'nagykereskedelmi', 'kiskereskedelmi', 'gazdasagi',
    'szamviteli', 'muszaki', 'epito', 'femipari', 'elektronikai', 'termelo', 'kutato', 'fejlesztesi',
}
_CONNECTORS = {'es', 'and', 'und', '&', 'valamint'}
_GENERIC_FIRST = {'magyar', 'magyarorszagi', 'hungarian', 'hungary', 'budapesti', 'budapest', 'global', 'nemzetkozi',
                  'international', 'europai', 'european', 'kozep', 'central', 'uj', 'new', 'first', 'elso'}
_SMALL_WORDS = {'es', 'and', 'und', 'of', 'the', 'a', 'az', 'de', 'la', 'le', 'van', 'von', 'der', 'et', 'y'}

_MULTI = [  # token sequences folded into one legal-form token for comparisons
    (('korlatolt', 'felelossegu', 'tarsasag'), 'kft'), (('zartkoruen', 'mukodo', 'reszvenytarsasag'), 'zrt'),
    (('nyilvanosan', 'mukodo', 'reszvenytarsasag'), 'nyrt'), (('beteti', 'tarsasag'), 'bt'),
    (('kozkereseti', 'tarsasag'), 'kkt'), (('egyeni', 'vallalkozo'), 'ev'), (('unlimited', 'company'), 'uc'),
    (('s', 'a', 'r', 'l'), 'sarl'), (('sp', 'z', 'o', 'o'), 'spzoo'), (('l', 'l', 'c'), 'llc'),
    (('s', 'r', 'l'), 'srl'), (('s', 'r', 'o'), 'sro'), (('d', 'o', 'o'), 'doo'), (('s', 'p', 'a'), 'spa'),
    (('b', 'v'), 'bv'), (('n', 'v'), 'nv'), (('s', 'a'), 'sa'), (('e', 'v'), 'ev'), (('k', 'f', 't'), 'kft'),
]
_SINGLE = {'limited': 'ltd', 'incorporated': 'inc', 'corporation': 'corp', 'company': 'co'}
LEGAL_TOKENS = {'kft', 'bt', 'zrt', 'nyrt', 'kkt', 'rt', 'kht', 'ev', 'ltd', 'llc', 'inc', 'corp', 'co', 'plc',
                'llp', 'pbc', 'uc', 'dac', 'gmbh', 'ag', 'kg', 'ohg', 'ug', 'gbr', 'se', 'sa', 'sarl', 'sas',
                'srl', 'spa', 'sl', 'bv', 'nv', 'ab', 'oy', 'oyj', 'as', 'aps', 'sro', 'spzoo', 'doo', 'pty',
                'pte', 'ou', 'uab', 'kk', 'bhd', 'nonprofit', 'fa', 'va', 'csa'}


def name_key(s):
    """Comparison key for company names: folded, punctuation-free, legal forms in one spelling."""
    toks = re.sub(r'[^0-9a-z]+', ' ', fold(s or '')).split()
    out, i = [], 0
    while i < len(toks):
        for seq, rep in _MULTI:
            n = len(seq)
            if tuple(toks[i:i + n]) == seq:
                out.append(rep)
                i += n
                break
        else:
            out.append(_SINGLE.get(toks[i], toks[i]))
            i += 1
    return ' '.join(out)


def core_key(s):
    """name_key without legal forms: 'Figma, Inc.' and 'FIGMA' compare equal."""
    toks = [t for t in name_key(s).split() if t not in LEGAL_TOKENS]
    return ' '.join(toks)


def strip_legal(name):
    """Drop trailing legal forms (and Hungarian activity words before a Hungarian legal form)."""
    name = (name or '').strip().strip(',;:')
    hungarian = bool(_HU_LEGAL_END.search(fold(name)))
    for _ in range(4):
        m = _TRAILING_LEGAL.search(fold(name))
        if not m or m.start() == 0:
            break
        name = name[:m.start()].rstrip(' ,(')
    if hungarian:
        words = name.split()
        dropped = False
        while len(words) > 1:
            last = fold(words[-1]).strip('.,')
            if last in _HU_ACTIVITY:
                if len(words) == 2 and fold(words[0]).strip('.,') in _GENERIC_FIRST:
                    break
                words.pop()
                dropped = True
            elif dropped and last in _CONNECTORS and len(words) > 2:
                words.pop()
            else:
                break
        name = ' '.join(words)
    return name.strip(' ,;:-')


def _fix_case(name):
    letters = [c for c in name if c.isalpha()]
    if not letters or not all(c.isupper() for c in letters) or len(letters) <= 4:
        return name
    out = []
    for w in name.split():
        fw = fold(w).strip('.,')
        if fw in _SMALL_WORDS and out:
            out.append(w.lower())
        elif len(w.strip('.,')) <= 3 and w.isalpha():
            out.append(w)  # acronyms: MVM, OTP, HB
        else:
            out.append(w[:1] + w[1:].lower())
    return ' '.join(out)


def display_name(raw, hungarian=False):
    """The canonical form used in file names: 'KOVÁCS ÉS TÁRSA KFT.' -> 'Kovács és Társa'."""
    name = ' '.join((raw or '').split())
    if hungarian:  # fonts without ő/ű often come out as õ/û
        name = name.translate(str.maketrans('õûÕÛ', 'őűŐŰ'))
    name = strip_legal(name) or name
    name = _fix_case(name)
    return name.strip(' ,;:-"\'')


# ------------------------------------------------------------------ e-mail senders
PLATFORM_DOMAINS = {
    'stripe.com', 'paddle.com', 'paddle.net', 'chargebee.com', 'recurly.com', 'zuora.com', 'intuit.com',
    'quickbooks.com', 'xero.com', 'freshbooks.com', 'invoiced.com', 'szamlazz.hu', 'billingo.hu',
    'kulcs-soft.hu', 'nav.gov.hu', 'gmail.com', 'googlemail.com', 'outlook.com', 'hotmail.com', 'live.com',
    'yahoo.com', 'icloud.com', 'me.com', 'freemail.hu', 'citromail.hu', 't-online.hu', 'mailgun.org',
    'sendgrid.net', 'amazonses.com', 'mail.com', 'gmx.net', 'gmx.de', 'web.de', 'protonmail.com',
    'proton.me', 'zoho.com', 'zohomail.eu', 'waveapps.com', 'sumup.com', 'invoice2go.com', 'squareup.com',
    'mailchimpapp.net', 'mandrillapp.com', 'postmarkapp.com', 'sparkpostmail.com', 'docusign.net',
    'dijnet.hu', 'e-szamla.hu', 'netszamla.hu', 'szamlakozpont.hu',
}
_GENERIC_SENDER = re.compile(
    r'(?<![a-z])(no-?reply|do-?not-?reply|billing|invoices?|invoicing|receipts?|accounts?|accounting|support|'
    r'info|notifications?|notify|mailer|payments?|finance|team|the|szamla|szamlak|szamlazas|ugyfelszolgalat|'
    r'ertesito|ertesites|rechnung|rechnungen|buchhaltung|service|customer|care|hello|admin|system|automated|'
    r'online|via|from|on behalf of)(?![a-z])')
_SECOND_LEVEL = {'co.uk', 'org.uk', 'ac.uk', 'com.au', 'net.au', 'co.nz', 'co.jp', 'com.br', 'co.za', 'com.tr'}


def registered_domain(domain):
    parts = (domain or '').lower().strip('.').split('.')
    if len(parts) >= 3 and '.'.join(parts[-2:]) in _SECOND_LEVEL:
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:]) if len(parts) >= 2 else (domain or '').lower()


def sender_parts(sender):
    """'Figma <billing@figma.com>' -> ('Figma', 'billing@figma.com', 'figma.com')."""
    name, addr = parseaddr(sender or '')
    addr = addr.lower()
    domain = registered_domain(addr.split('@', 1)[1]) if '@' in addr else ''
    return name.strip().strip('"'), addr, domain


def sender_name_guess(display):
    """A supplier name from a sender display name, or '' when it is generic ('Billing Team')."""
    left = _GENERIC_SENDER.sub(' ', fold(display or ''))
    left = re.sub(r'[^0-9a-z]+', ' ', left).strip()
    if len(left) < 2:
        return ''
    # keep the original spelling of the words that survived
    keep = set(left.split())
    words = [w for w in re.split(r'\s+', display.strip()) if re.sub(r'[^0-9a-z]+', '', fold(w)) in keep]
    return ' '.join(words).strip(' -|,')


def domain_name_guess(domain):
    label = (domain or '').split('.')[0]
    if len(label) < 3:
        return ''
    return label.capitalize()


# ------------------------------------------------------------------ tax numbers
_HU_TAX = re.compile(r'(?<![\d-])(\d{8})-(\d)-(\d{2})(?![\d-])')
_EU_VAT = re.compile(r'(?<![A-Z0-9])(AT|BE|BG|CY|CZ|DE|DK|EE|EL|ES|FI|FR|HR|HU|IE|IT|LT|LU|LV|MT|NL|PL|PT|RO|SE|'
                     r'SI|SK|XI|GB|CHE)[ -]?(U?\d[0-9A-Z]{6,12})(?![A-Z0-9])')
_VAT_LABEL = re.compile(r'(adoszam|adoazonosito|kozossegi|vat|tax\s*(?:id|no|number|reg)|ust|umsatzsteuer|'
                        r'steuer|tva|iva|uid|btw|nip|dic|cif|nif|abn|gst|mwst)')


def tax_core(t):
    t = re.sub(r'[\s.-]', '', (t or '').upper())
    m = re.fullmatch(r'(\d{8})\d{3}', t)
    if m:
        return m.group(1)
    if t.startswith('HU') and t[2:].isdigit():
        return t[2:10]
    if t.isdigit() and len(t) >= 8:
        return t[:8]
    return t


def find_tax_ids(lines, flines):
    """[(line, col, display, core)] for Hungarian tax numbers and labelled EU VAT numbers."""
    out = []
    for i, line in enumerate(lines):
        for m in _HU_TAX.finditer(line):
            out.append((i, m.start(), m.group(0), m.group(1)))
        up = line.upper()
        for m in _EU_VAT.finditer(up):
            if _VAT_LABEL.search(flines[i][max(0, m.start() - 45):m.start()]):
                val = m.group(1) + m.group(2)
                out.append((i, m.start(), val, tax_core(val)))
    return out


# ------------------------------------------------------------------ registry
def _clean_list(v):
    return [x for x in (v or []) if isinstance(x, str) and x.strip()]


def _doc_alias_ok(key):
    """Only distinctive aliases are searched for in invoice text (two words, or one long word)."""
    toks = key.split()
    return len(toks) >= 2 and len(key) >= 6 or (len(toks) == 1 and len(key) >= 8)


class Registry:
    def __init__(self, con):
        self.rows = []
        for r in con.execute('SELECT * FROM suppliers ORDER BY id').fetchall():
            d = dict(r)
            d['aliases'] = _clean_list(jload(d['aliases'], []))
            d['tax_ids'] = _clean_list(jload(d['tax_ids'], []))
            d['domains'] = _clean_list(jload(d['domains'], []))
            d['_alias_keys'] = sorted({name_key(a) for a in d['aliases'] if name_key(a)}, key=len, reverse=True)
            d['_core_keys'] = {core_key(a) for a in d['aliases'] + [d['name']] if core_key(a)}
            d['_tax'] = {tax_core(t) for t in d['tax_ids']}
            self.rows.append(d)

    def get(self, name):
        for r in self.rows:
            if r['name'] == name:
                return r
        return None

    def by_tax(self, cores):
        cores = set(cores)
        for r in self.rows:
            if r['_tax'] & cores:
                return r
        return None

    def by_domain(self, domain):
        if not domain:
            return None
        for r in self.rows:
            if domain in r['domains']:
                return r
        return None

    def by_name(self, name):
        """Exact match on the name without legal form, against canonical names and aliases."""
        k = core_key(name)
        if not k:
            return None
        for r in self.rows:
            if k in r['_core_keys']:
                return r
        return None

    def find_in_lines(self, line_keys):
        """[(row, line_index, alias_key)] for every distinctive alias found in the text."""
        hits = []
        padded = [' ' + k + ' ' for k in line_keys]
        for r in self.rows:
            for ak in r['_alias_keys']:
                if not _doc_alias_ok(ak):
                    continue
                needle = ' ' + ak + ' '
                for i, pk in enumerate(padded):
                    if needle in pk:
                        hits.append((r, i, ak))
                        break
        return hits


def seed_builtin(con):
    """Load the well-known suppliers once (they can be edited or removed afterwards)."""
    from . import db as dbm
    if dbm.meta_get(con, 'builtin_suppliers_seeded'):
        return 0
    with open(ASSETS / 'known_suppliers.json', encoding='utf-8') as f:
        known = json.load(f)
    n = 0
    for s in known:
        if con.execute('SELECT 1 FROM suppliers WHERE name = ?', (s['name'],)).fetchone():
            continue
        con.execute('INSERT INTO suppliers(name, aliases, tax_ids, domains, paid_on, builtin, created_at, updated_at) '
                    'VALUES (?, ?, ?, ?, ?, 1, ?, ?)',
                    (s['name'], jdump(s.get('aliases', [])), jdump(s.get('tax_ids', [])), jdump(s.get('domains', [])),
                     s.get('paid_on'), now_iso(), now_iso()))
        n += 1
    dbm.meta_set(con, 'builtin_suppliers_seeded', True)
    return n


def upsert(con, name, aliases=(), tax_ids=(), domains=(), paid_on=None, set_paid_on=False):
    """Create the supplier or add the given aliases / tax numbers / domains to it."""
    name = name.strip()
    row = con.execute('SELECT * FROM suppliers WHERE name = ?', (name,)).fetchone()
    if row is None:
        con.execute('INSERT INTO suppliers(name, aliases, tax_ids, domains, paid_on, builtin, created_at, updated_at) '
                    'VALUES (?, ?, ?, ?, ?, 0, ?, ?)',
                    (name, jdump(sorted(set(_clean_list(aliases)))), jdump(sorted(set(_clean_list(tax_ids)))),
                     jdump(sorted(set(_clean_list(domains)))), paid_on, now_iso(), now_iso()))
        return
    al = set(_clean_list(jload(row['aliases'], []))) | set(_clean_list(aliases))
    tx = set(_clean_list(jload(row['tax_ids'], []))) | set(_clean_list(tax_ids))
    dm = set(_clean_list(jload(row['domains'], []))) | set(_clean_list(domains))
    po = paid_on if set_paid_on else row['paid_on']
    con.execute('UPDATE suppliers SET aliases = ?, tax_ids = ?, domains = ?, paid_on = ?, updated_at = ? WHERE id = ?',
                (jdump(sorted(al)), jdump(sorted(tx)), jdump(sorted(dm)), po, now_iso(), row['id']))


GENERIC_TOKENS = {
    'magyar', 'magyarorszag', 'magyarorszagi', 'hungary', 'hungaria', 'hungarian', 'budapest', 'budapesti',
    'online', 'services', 'service', 'group', 'csoport', 'international', 'nemzetkozi', 'europe', 'european',
    'emea', 'ireland', 'global', 'systems', 'solutions', 'digital', 'media', 'consulting', 'trade', 'trading',
    'holding', 'invest', 'studio', 'design', 'company', 'technologies', 'technology', 'labs', 'and', 'the', 'es',
    'und', 'of', 'ingatlan', 'kozpont', 'center', 'centre',
} | _HU_ACTIVITY


def related_names(a, b):
    """Do two names plausibly name the same company? ('Kovács és Társa Kft.' / 'Kovács & Társa': yes;
    'Gamma Ingatlan Zrt.' / 'Delta Facility': no.) Generic words like 'Magyar' or 'Services' do not count."""
    ta = [t for t in core_key(a).split() if len(t) >= 3 and t not in GENERIC_TOKENS]
    tb = [t for t in core_key(b).split() if len(t) >= 3 and t not in GENERIC_TOKENS]
    for x in ta:
        for y in tb:
            if x == y or (min(len(x), len(y)) >= 4 and (x.startswith(y) or y.startswith(x))):
                return True
    flat_a, flat_b = ''.join(ta), ''.join(tb)
    return len(flat_a) >= 4 and len(flat_b) >= 4 and (flat_a in flat_b or flat_b in flat_a)


def learn(con, name, raw_name=None, tax_ids=(), domain=None, own_cores=()):
    """Remember what an admin's correction tells us about a supplier."""
    aliases = []
    if raw_name and name_key(raw_name) and name_key(raw_name) != name_key(name):
        aliases.append(raw_name.strip())
    taxes = [t for t in tax_ids if tax_core(t) not in set(own_cores)]
    domains = [domain] if domain and domain not in PLATFORM_DOMAINS else []
    upsert(con, name, aliases=aliases, tax_ids=taxes, domains=domains)
