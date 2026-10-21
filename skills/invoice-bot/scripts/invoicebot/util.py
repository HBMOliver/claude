"""Shared helpers: text folding, date and money parsing, safe file names, json and locks.

Everything that reads invoice text works on a "folded" copy of each line (lower case, no accents)
that has exactly the same length as the original, so a match found in the folded line can be cut
out of the original line at the same offsets.
"""
import datetime as dt
import hashlib
import json
import os
import re
import threading
import time
import unicodedata
from decimal import Decimal, InvalidOperation

# ------------------------------------------------------------------ text
_FOLD_CACHE = {}
_FOLD_SPECIAL = {'ß': 's', 'ø': 'o', 'Ø': 'o', 'ł': 'l', 'Ł': 'l', 'đ': 'd', 'Đ': 'd',
                 'æ': 'a', 'Æ': 'a', 'œ': 'o', 'Œ': 'o', 'þ': 't', 'Þ': 't', 'ı': 'i'}


def _fold_char(c):
    r = _FOLD_CACHE.get(c)
    if r is None:
        if c in _FOLD_SPECIAL:
            r = _FOLD_SPECIAL[c]
        else:
            base = ''.join(ch for ch in unicodedata.normalize('NFKD', c) if not unicodedata.combining(ch))
            r = base.lower()[:1] if base else c
            r = r or c
        _FOLD_CACHE[c] = r
    return r


def fold(s):
    """Lower case, accent-free copy of s with exactly the same length."""
    return ''.join(map(_fold_char, s))


_SPACES = dict.fromkeys(map(ord, '          '
                               '    　'), ' ')
_DASHES = dict.fromkeys(map(ord, '‐‑‒–—―−'), '-')
_INVISIBLE = dict.fromkeys(map(ord, '​‌‍⁠﻿­'), None)


def clean_text(text):
    """Normalise extracted PDF text: NFC, plain spaces and dashes, no invisible chars, tabs expanded."""
    text = unicodedata.normalize('NFC', text or '')
    text = text.translate(_SPACES).translate(_DASHES).translate(_INVISIBLE)
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\f', '\n')
    return '\n'.join(line.expandtabs(4).rstrip() for line in text.split('\n'))


_TRANSLIT = {'ß': 'ss', 'æ': 'ae', 'Æ': 'AE', 'œ': 'oe', 'Œ': 'OE', 'ø': 'o', 'Ø': 'O',
             'ł': 'l', 'Ł': 'L', 'đ': 'd', 'Đ': 'D', 'þ': 'th', 'Þ': 'Th', 'ı': 'i'}


def ascii_text(s):
    out = []
    for c in s:
        if ord(c) < 128:
            out.append(c)
        elif c in _TRANSLIT:
            out.append(_TRANSLIT[c])
        else:
            out.append(''.join(ch for ch in unicodedata.normalize('NFKD', c) if ord(ch) < 128))
    return ''.join(out)


def norm_key(s):
    """Comparison key: folded, alphanumerics only, single spaces."""
    return ' '.join(re.sub(r'[^0-9a-z]+', ' ', fold(s or '')).split())


# ------------------------------------------------------------------ dates
MONTHS = {
    # English
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3, 'april': 4, 'apr': 4,
    'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9,
    'sep': 9, 'sept': 9, 'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12,
    # Hungarian (folded)
    'januar': 1, 'februar': 2, 'febr': 2, 'marcius': 3, 'marc': 3, 'aprilis': 4, 'majus': 5,
    'maj': 5, 'junius': 6, 'julius': 7, 'augusztus': 8, 'szeptember': 9, 'szept': 9, 'oktober': 10,
    'okt': 10,
    # German (folded)
    'maerz': 3, 'marz': 3, 'mai': 5, 'juni': 6, 'juli': 7, 'dezember': 12, 'dez': 12,
}
_MON = '|'.join(sorted(MONTHS, key=len, reverse=True))

_DATE_RES = [
    # 2026-09-15, 2026.09.15., 2026. 09. 15., 2026/09/15
    ('ymd', re.compile(r'(?<![\d.])(\d{4})\s?([./-])\s?(\d{1,2})\s?\2\s?(\d{1,2})(?!\d)(?:\s?\.(?!\d))?')),
    # 15.09.2026, 15/09/2026, 09/15/2026
    ('num', re.compile(r'(?<![\d.])(\d{1,2})\s?([./-])\s?(\d{1,2})\s?\2\s?(\d{4})(?!\d)')),
    # 15.09.26 (weak: only used next to a label)
    ('num2', re.compile(r'(?<![\d./-])(\d{1,2})([./-])(\d{1,2})\2(\d{2})(?![\d./-])')),
    # 15 September 2026, 15. szeptember 2026, 15-Sep-2026, 15th of September 2026
    ('dmony', re.compile(r'(?<!\d)(\d{1,2})(?:st|nd|rd|th)?\.?[\s-]*(?:of\s+)?(' + _MON +
                         r')(?![a-z])\.?[\s,-]*(\d{4})(?!\d)')),
    # September 15, 2026 / Sep 15 2026
    ('mondy', re.compile(r'(?<![a-z])(' + _MON + r')(?![a-z])\.?\s*(\d{1,2})(?:st|nd|rd|th)?\.?,?\s*(\d{4})(?!\d)')),
    # 2026. szeptember 15.
    ('ymond', re.compile(r'(?<!\d)(\d{4})\.?\s*(' + _MON + r')(?![a-z])\.?\s*(\d{1,2})(?!\d)\.?')),
]


def _mkdate(y, m, d):
    try:
        if not 1990 <= y <= 2100:
            return None
        return dt.date(y, m, d)
    except ValueError:
        return None


class DateHit:
    """A date found in a line. cands maps an order ('*', 'DMY' or 'MDY') to the date it gives."""
    __slots__ = ('start', 'end', 'cands', 'kind')

    def __init__(self, start, end, cands, kind):
        self.start, self.end, self.cands, self.kind = start, end, cands, kind

    @property
    def ambiguous(self):
        return len(self.cands) > 1

    def get(self, order='DMY'):
        if '*' in self.cands:
            return self.cands['*']
        return self.cands.get(order) or next(iter(self.cands.values()))

    def __repr__(self):
        return f'DateHit({self.start}-{self.end} {self.cands} {self.kind})'


def find_dates(folded_line):
    """All dates in a (folded) line, without overlaps."""
    hits = []
    for kind, rx in _DATE_RES:
        for m in rx.finditer(folded_line):
            cands = {}
            if kind == 'ymd':
                d = _mkdate(int(m.group(1)), int(m.group(3)), int(m.group(4)))
                if d:
                    cands['*'] = d
            elif kind in ('num', 'num2'):
                a, b, y = int(m.group(1)), int(m.group(3)), int(m.group(4))
                if kind == 'num2':
                    y += 2000
                dmy, mdy = _mkdate(y, b, a), _mkdate(y, a, b)
                if dmy and mdy and dmy != mdy:
                    cands = {'DMY': dmy, 'MDY': mdy}
                elif dmy and mdy:
                    cands['*'] = dmy
                elif dmy:
                    cands['DMY'] = dmy
                elif mdy:
                    cands['MDY'] = mdy
            elif kind == 'dmony':
                d = _mkdate(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
                if d:
                    cands['*'] = d
            elif kind == 'mondy':
                d = _mkdate(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
                if d:
                    cands['*'] = d
            elif kind == 'ymond':
                d = _mkdate(int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))
                if d:
                    cands['*'] = d
            if cands:
                hits.append(DateHit(m.start(), m.end(), cands, kind))
    # keep the longest of overlapping hits
    hits.sort(key=lambda h: (h.start, -(h.end - h.start)))
    out = []
    for h in hits:
        if out and h.start < out[-1].end:
            if (h.end - h.start) > (out[-1].end - out[-1].start):
                out[-1] = h
            continue
        out.append(h)
    return out


def parse_date(s, order='DMY'):
    """Parse a date typed by a person (ISO preferred). Returns datetime.date or None."""
    s = (s or '').strip()
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s[:10])
    except ValueError:
        pass
    hits = find_dates(fold(clean_text(s)))
    return hits[0].get(order) if hits else None


def iso(d):
    return d.isoformat() if d else None


def to_date(s):
    if not s:
        return None
    if isinstance(s, dt.date):
        return s
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


# ------------------------------------------------------------------ money
CURRENCY_WORDS = {
    'ft': 'HUF', 'huf': 'HUF', 'forint': 'HUF', 'eur': 'EUR', 'euro': 'EUR', '€': 'EUR',
    'usd': 'USD', 'us$': 'USD', '$': 'USD', 'gbp': 'GBP', '£': 'GBP', 'chf': 'CHF', 'pln': 'PLN',
    'zl': 'PLN', 'czk': 'CZK', 'kc': 'CZK', 'ron': 'RON', 'lei': 'RON', 'sek': 'SEK', 'nok': 'NOK',
    'dkk': 'DKK', 'jpy': 'JPY', 'cad': 'CAD', 'ca$': 'CAD', 'c$': 'CAD', 'aud': 'AUD', 'a$': 'AUD',
    'au$': 'AUD', 'rsd': 'RSD', 'bgn': 'BGN', 'cny': 'CNY', 'inr': 'INR',
}
CURRENCY_CODES = sorted({v for v in CURRENCY_WORDS.values()})
_CUR_ALT = '|'.join(re.escape(k) for k in sorted(CURRENCY_WORDS, key=len, reverse=True))
_CUR_AFTER = re.compile(r'^\s{0,2}(?:,-|\.-)?\s{0,2}(' + _CUR_ALT + r')(?![a-z])\.?')
_CUR_BEFORE = re.compile(r'(?<![a-z])(' + _CUR_ALT + r')\s{0,2}$')
_CUR_ANY = re.compile(r'(?<![a-z])(huf|eur|usd|gbp|chf|pln|czk|ron|sek|nok|dkk|jpy|cad|aud|ft|forint|euro)(?![a-z])|[€$£]')

_AMOUNT_RE = re.compile(r"""
    (?<![\w.,/-])
    (?P<neg>-\s?)?
    (?P<num>
        \d{1,3}(?P<sep>[ .,'])\d{3}(?:(?P=sep)\d{3})*(?:[.,]\d{1,2})?
      | \d+(?:[.,]\d{1,2})?
    )
    (?:,-{1,2}|\.-)?
    (?![\w]|[.,]\d|\s?%|/\d|:\d)
""", re.X)

# things that look like numbers but are never amounts
_MASK_RES = [
    re.compile(r'(?<![\d-])\d{8}-\d-\d{2}(?![\d-])'),              # Hungarian tax number
    re.compile(r'(?<![\d-])\d{8}-\d{8}(?:-\d{8})?(?![\d-])'),     # Hungarian bank account
    re.compile(r'(?<![a-z])[a-z]{2}\d{2}(?:\s?[0-9a-z]{4}){3,7}(?:\s?[0-9a-z]{1,3})?(?![0-9a-z])'),  # IBAN
    re.compile(r'\+\d[\d /().-]{7,}\d'),                            # phone numbers
    re.compile(r'(?<![\d.,])\d{1,2}:\d{2}(?::\d{2})?(?![\d])'),     # clock times
]


def parse_number(raw):
    """'1.234,56' / '1,234.56' / '127 000' / '12 700,-' -> Decimal (sign not included)."""
    s = raw.strip().rstrip('-').rstrip(',').rstrip('.')
    s = s.replace("'", ' ').replace('’', ' ')
    last_dot, last_comma = s.rfind('.'), s.rfind(',')
    dec = None
    if last_dot >= 0 and last_comma >= 0:
        dec = '.' if last_dot > last_comma else ','
    elif last_dot >= 0 or last_comma >= 0:
        sep = '.' if last_dot >= 0 else ','
        pos = max(last_dot, last_comma)
        tail = s[pos + 1:]
        head = s[:pos].replace(' ', '')
        if s.count(sep) == 1 and (len(tail) in (1, 2) or head == '0' or (len(tail) == 3 and ' ' in s)):
            dec = sep
    if dec:
        pos = s.rfind(dec)
        int_part, frac = s[:pos], s[pos + 1:]
    else:
        int_part, frac = s, ''
    digits = re.sub(r'\D', '', int_part)
    if not digits:
        return None
    try:
        return Decimal(digits + ('.' + frac if frac else ''))
    except InvalidOperation:
        return None


_MAX_AMOUNT = Decimal('1e13')


class AmountHit:
    __slots__ = ('start', 'end', 'value', 'currency', 'raw')

    def __init__(self, start, end, value, currency, raw):
        self.start, self.end, self.value, self.currency, self.raw = start, end, value, currency, raw

    def __repr__(self):
        return f'AmountHit({self.value} {self.currency} @{self.start})'


def mask_spans(s, spans, ch=' '):
    if not spans:
        return s
    chars = list(s)
    for a, b in spans:
        for i in range(a, min(b, len(chars))):
            chars[i] = ch
    return ''.join(chars)


def find_amounts(folded_line, date_hits=None):
    """Money amounts in a folded line (dates, tax numbers, accounts, phones and times are masked out)."""
    spans = [(h.start, h.end) for h in (date_hits if date_hits is not None else find_dates(folded_line))]
    for rx in _MASK_RES:
        spans += [(m.start(), m.end()) for m in rx.finditer(folded_line)]
    line = mask_spans(folded_line, spans)
    out = []
    for m in _AMOUNT_RE.finditer(line):
        val = parse_number(m.group('num'))
        if val is None or val >= _MAX_AMOUNT:
            continue  # nothing real is this large: a reference number, not money
        neg = bool(m.group('neg'))
        before, after = line[max(0, m.start() - 6):m.start()], line[m.end():m.end() + 9]
        if not neg and before.rstrip().endswith('(') and after.lstrip().startswith(')'):
            neg = True
        cur = None
        ma = _CUR_AFTER.match(after)
        mb = _CUR_BEFORE.search(before.rstrip('-( '))
        if ma:
            cur = CURRENCY_WORDS.get(ma.group(1))
        elif mb:
            cur = CURRENCY_WORDS.get(mb.group(1))
        if neg:
            val = -val
        out.append(AmountHit(m.start('neg') if m.group('neg') else m.start('num'), m.end(), val, cur, m.group(0)))
    return out


def currency_mentions(folded_text):
    counts = {}
    for m in _CUR_ANY.finditer(folded_text):
        tok = m.group(1) or m.group(0)
        code = CURRENCY_WORDS.get(tok)
        if code:
            counts[code] = counts.get(code, 0) + 1
    return counts


def money(value, currency=None, decimals=None):
    """Human display: 127 000 HUF, 1 234.50 EUR."""
    if value is None or value == '':
        return ''
    d = Decimal(str(value))
    if decimals is None:
        decimals = 0 if currency in ('HUF', 'JPY') and d == d.to_integral_value() else 2
    s = f'{abs(d):,.{decimals}f}'.replace(',', ' ')
    return ('-' if d < 0 else '') + s + (f' {currency}' if currency else '')


def dec_str(value):
    """Canonical storage form: '127000.00'."""
    if value is None or value == '':
        return None
    try:
        return f'{Decimal(str(value)).quantize(Decimal("0.01"))}'
    except InvalidOperation:
        return None


def parse_amount_input(s):
    """Amount typed by a person: '127 000', '1.234,56', '-50', '45 EUR'."""
    s = (s or '').strip()
    neg = s.startswith('-') or (s.startswith('(') and s.endswith(')'))
    core = re.sub(r"[^\d.,\s']", ' ', s).strip()
    if not core:
        return None
    v = parse_number(' '.join(core.split()))
    if v is None:
        return None
    return -v if neg else v


# ------------------------------------------------------------------ file names
_WIN_RESERVED = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}


def safe_component(s, max_len=40, ascii_only=True, space='-'):
    """One file-name field: no separators, no underscores (they split the fields), no reserved names."""
    s = (s or '').strip()
    if ascii_only:
        s = ascii_text(s)
    s = re.sub(r'[\\/:*?"<>|\x00-\x1f_#]+', '-', s)
    s = re.sub(r'\s+', space, s)
    if ascii_only:
        s = re.sub(r'[^A-Za-z0-9.&+\-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-. ')
    if len(s) > max_len:
        cut = s[:max_len]
        if '-' in cut[max_len // 2:]:
            cut = cut[:cut.rfind('-')]
        s = cut.strip('-. ')
    if s.upper() in _WIN_RESERVED:
        s += '-'
    return s


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------------ json / time
def jdump(obj):
    return json.dumps(obj, ensure_ascii=False, default=str)


def jload(s, default=None):
    if not s:
        return default
    try:
        return json.loads(s)
    except (TypeError, ValueError):
        return default


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today():
    """Overridable in tests via INVOICEBOT_TODAY=YYYY-MM-DD."""
    t = os.environ.get('INVOICEBOT_TODAY')
    if t:
        return dt.date.fromisoformat(t)
    return dt.date.today()


# ------------------------------------------------------------------ locks
class _LockState:
    def __init__(self):
        self.rlock = threading.RLock()
        self.fh = None
        self.depth = 0


_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


class FileLock:
    """Exclusive lock shared by the threads of this process and by other processes
    (a cron run and the admin server never move files at the same time)."""

    def __init__(self, path, timeout=30.0):
        self.path, self.timeout = os.path.abspath(str(path)), timeout
        with _LOCKS_GUARD:
            self._st = _LOCKS.setdefault(self.path, _LockState())

    def acquire(self, blocking=True):
        st = self._st
        got = st.rlock.acquire(timeout=self.timeout) if blocking else st.rlock.acquire(False)
        if not got:
            return False
        if st.depth:
            st.depth += 1
            return True
        deadline = time.monotonic() + (self.timeout if blocking else 0)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        fh = open(self.path, 'a+')
        while True:
            try:
                _lock_fh(fh)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    fh.close()
                    st.rlock.release()
                    return False
                time.sleep(0.2)
        st.fh, st.depth = fh, 1
        return True

    def release(self):
        st = self._st
        st.depth -= 1
        if st.depth == 0 and st.fh:
            try:
                _unlock_fh(st.fh)
            finally:
                st.fh.close()
                st.fh = None
        st.rlock.release()

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f'another invoice bot process is busy ({self.path})')
        return self

    def __exit__(self, *exc):
        self.release()


try:
    import fcntl

    def _lock_fh(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_fh(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
except ImportError:  # Windows
    import msvcrt

    def _lock_fh(fh):
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock_fh(fh):
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
