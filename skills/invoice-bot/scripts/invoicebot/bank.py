"""Bank statements: import a CSV export and match outgoing payments to invoices.

A match confirms the invoice's real payment date, so the invoice moves into the month it was paid in.
Works with the CSV exports of most banks (OTP, K&H, MBH, Erste, Raiffeisen, Revolut, Wise, ...):
encoding, delimiter and header row are detected, and the columns are recognised by name in Hungarian,
English and German. Only money going out is used.

Scoring (amount and currency must match; the payment must fall between 5 days before the invoice date
and 120 days after its due date):
    50  amount
    +40 the invoice number appears in the transfer's reference text
    +30 the supplier's name appears in the counterparty / reference (scaled by how much of it matches)
    +8  paid within 3 days of the due date
Matches scoring 75 or more are applied automatically; lower ones are offered as suggestions.
"""
import csv
import hashlib
import io
import re
from datetime import timedelta
from decimal import Decimal

from . import db as dbm
from . import pipeline as P
from . import suppliers as S
from .util import fold, find_dates, jdump, now_iso, parse_number, to_date

AUTO_SCORE = 75
MIN_SCORE = 50

_COLS = {
    'date': ['konyveles datuma', 'konyvelesi datum', 'konyveles napja', 'terheles datuma', 'tranzakcio datuma',
             'teljesites datuma', 'completed date', 'date completed', 'booking date', 'posting date',
             'transaction date', 'buchungstag', 'buchungsdatum', 'date', 'datum', 'value date', 'erteknap',
             'started date', 'valuta', 'wertstellung'],
    'amount': ['osszeg', 'amount', 'tranzakcio osszege', 'terheles osszege', 'betrag', 'umsatz',
               'amount in account currency', 'total amount'],
    'debit': ['terheles', 'debit', 'kiadas', 'kifizetes', 'soll', 'paid out', 'money out', 'withdrawal'],
    'credit': ['jovairas', 'credit', 'bevetel', 'haben', 'paid in', 'money in', 'deposit'],
    'currency': ['devizanem', 'penznem', 'deviza', 'currency', 'waehrung', 'wahrung', 'ccy'],
    'counterparty': ['partner neve', 'partner nev', 'partner', 'kedvezmenyezett neve', 'kedvezmenyezett',
                     'ellenoldali nev', 'ellenoldali szamlatulajdonos', 'ellenoldal neve', 'payee name', 'payee',
                     'beneficiary', 'beneficiary name', 'counterparty', 'counterparty name', 'merchant', 'name',
                     'recipient', 'empfanger', 'empfaenger', 'beguenstigter', 'auftraggeber empfanger'],
    'description': ['kozlemeny', 'megjegyzes', 'leiras', 'tranzakcio leirasa', 'description', 'details',
                    'payment reference', 'reference', 'narrative', 'memo', 'verwendungszweck', 'buchungstext',
                    'tranzakcio tipusa', 'tipus', 'type'],
    'state': ['state', 'status', 'allapot'],
}
_BAD_STATES = {'reverted', 'declined', 'failed', 'cancelled', 'canceled', 'pending', 'elutasitva', 'visszavonva'}


def _norm(s):
    return ' '.join(re.sub(r'[^0-9a-z]+', ' ', fold(s or '')).split())


def _decode(data):
    for enc in ('utf-8-sig', 'cp1250'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode('latin-1')


def _sniff_rows(text):
    sample = '\n'.join(text.splitlines()[:30])
    best = None
    for delim in (';', ',', '\t', '|'):
        rows = list(csv.reader(io.StringIO(sample), delimiter=delim))
        widths = [len(r) for r in rows if any(c.strip() for c in r)]
        if not widths:
            continue
        common = max(set(widths), key=widths.count)
        score = (common >= 3) * widths.count(common) * common
        if best is None or score > best[0]:
            best = (score, delim)
    delim = best[1] if best else ','
    return list(csv.reader(io.StringIO(text), delimiter=delim)), delim


def _map_header(row):
    cells = [_norm(c) for c in row]
    found = {}
    for key, names in _COLS.items():
        for name in names:  # priority order
            idx = next((i for i, c in enumerate(cells) if c == name and i not in found.values()), None)
            if idx is None and len(name) > 6:
                idx = next((i for i, c in enumerate(cells) if name in c and i not in found.values()), None)
            if idx is not None:
                found[key] = idx
                break
    return found


def read_statement(data, default_currency='HUF'):
    """Outgoing payments: [{'date','amount' (positive Decimal),'currency','counterparty','description'}]."""
    text = _decode(data)
    rows, delim = _sniff_rows(text)
    header_at, cols = None, None
    for i, row in enumerate(rows[:25]):
        m = _map_header(row)
        if 'date' in m and ('amount' in m or 'debit' in m):
            header_at, cols = i, m
            break
    if cols is None:
        raise ValueError('Could not find the header row: the statement needs a date column and an amount '
                         '(or debit) column.')
    body = [r for r in rows[header_at + 1:] if any(c.strip() for c in r)]

    def cell(row, k):
        i = cols.get(k)
        return row[i].strip() if i is not None and i < len(row) else ''

    # day-first or month-first: decided once for the whole file
    dmy = mdy = 0
    for row in body:
        for h in find_dates(fold(cell(row, 'date')))[:1]:
            dmy += set(h.cands) == {'DMY'}
            mdy += set(h.cands) == {'MDY'}
    order = 'MDY' if mdy > dmy else 'DMY'
    out = []
    for row in body:
        if cell(row, 'state') and _norm(cell(row, 'state')) in _BAD_STATES:
            continue
        dates = find_dates(fold(cell(row, 'date')))
        if not dates:
            continue
        d = dates[0].get(order)
        amount = None
        if 'debit' in cols and cell(row, 'debit'):
            v = _amount(cell(row, 'debit'))
            if v:
                amount = abs(v)
        elif 'amount' in cols and cell(row, 'amount'):
            v = _amount(cell(row, 'amount'))
            if v is not None and v < 0:
                amount = -v
        if not amount:
            continue
        cur = (cell(row, 'currency') or default_currency).upper()[:3]
        out.append({'date': d.isoformat(), 'amount': amount, 'currency': cur,
                    'counterparty': cell(row, 'counterparty'), 'description': cell(row, 'description')})
    return out


def _amount(s):
    s = s.strip().replace(' ', ' ')
    neg = s.startswith('-') or s.startswith('(') or s.endswith('-')
    v = parse_number(re.sub(r"[^\d.,\s']", ' ', s).strip()) if re.search(r'\d', s) else None
    if v is None:
        return None
    return -v if neg else v


def import_statement(bot, data, name='', account=None, actor='admin'):
    txns = read_statement(data, bot.cfg['default_currency'])
    batch = now_iso()
    added = dup = 0
    seen = {}
    con = bot.db()
    try:
        with con:
            for t in txns:
                key = '|'.join([account or '', t['date'], str(t['amount']), t['currency'], t['counterparty'],
                                t['description']])
                seen[key] = seen.get(key, 0) + 1
                h = hashlib.sha256(f'{key}|{seen[key]}'.encode('utf-8')).hexdigest()
                cur = con.execute('INSERT OR IGNORE INTO bank_txns(hash, account, date, amount, currency, counterparty, '
                                  'description, batch, imported_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                  (h, account, t['date'], str(t['amount']), t['currency'], t['counterparty'],
                                   t['description'], batch, now_iso()))
                if cur.rowcount:
                    added += 1
                else:
                    dup += 1
            dbm.log_event(con, 'bank_import', None, actor, {'file': name, 'payments': len(txns), 'new': added})
        result = match_all(bot, apply=True, actor=actor)
    finally:
        con.close()
    result.update({'payments_in_file': len(txns), 'new_payments': added, 'already_imported': dup})
    return result


# ------------------------------------------------------------------ matching
def _candidates_sql():
    return ("SELECT * FROM invoices WHERE status = 'filed' AND amount IS NOT NULL AND "
            "(paid = 0 OR payment_source LIKE 'expected%')")


def _score(inv, txn, rejected=()):
    if (inv['id'], txn['id']) in rejected:
        return None
    if (txn['currency'] or '') != (inv['currency'] or ''):
        return None
    inv_amt = abs(Decimal(inv['amount']))
    tol = Decimal('1') if inv['currency'] == 'HUF' else Decimal('0.01')
    if abs(inv_amt - Decimal(txn['amount'])) > tol:
        return None
    td = to_date(txn['date'])
    issue = to_date(inv['issue_date']) or to_date(inv['fulfilment_date']) or to_date(inv['due_date'])
    due = to_date(inv['due_date']) or issue
    if issue and td < issue - timedelta(days=5):
        return None
    if due and td > due + timedelta(days=120):
        return None
    s = 50.0
    text = _norm(f"{txn.get('counterparty') or ''} {txn.get('description') or ''}")
    folded = fold(f"{txn.get('counterparty') or ''} {txn.get('description') or ''}")
    if _number_in(inv['invoice_number'], folded):
        s += 40
    sup = [t for t in S.core_key(inv['supplier'] or '').split() if len(t) >= 3 and t not in _GENERIC_WORDS]
    if sup:
        words = set(text.split())
        flat = text.replace(' ', '')
        hit = sum(1 for t in sup if t in words or (len(t) >= 6 and t in flat))
        s += 30 * hit / len(sup)
    if due:
        days = abs((td - due).days)
        if days <= 3:
            s += 8
        s -= min(days, 100) * 0.05  # prefer the payment closest to the due date
    return s


_GENERIC_WORDS = {'magyar', 'magyarorszag', 'magyarorszagi', 'hungary', 'hungaria', 'hungarian', 'online',
                  'services', 'service', 'szolgaltato', 'group', 'csoport', 'international', 'europe', 'emea',
                  'ireland', 'global', 'systems', 'solutions', 'digital', 'media', 'consulting', 'trade',
                  'holding', 'invest', 'studio', 'design', 'company', 'technologies', 'technology', 'labs'}


def _number_in(number, folded_text):
    """The invoice number appears in the text as a whole token (separators may differ)."""
    chunks = re.findall(r'[0-9a-z]+', fold(number or ''))
    if not chunks or len(''.join(chunks)) < 4:
        return False
    rx = r'(?<![0-9a-z])' + r'[\s/._#-]*'.join(map(re.escape, chunks)) + r'(?![0-9a-z])'
    return re.search(rx, folded_text) is not None


def _rejected(con):
    return {tuple(p) for p in dbm.meta_get(con, 'bank_rejected', [])}


def propose(bot, con):
    """Best one-to-one pairs (score, invoice row, txn row), highest score first."""
    invs = [dbm._decode(r) for r in con.execute(_candidates_sql()).fetchall()]
    txns = [dict(r) for r in con.execute("SELECT * FROM bank_txns WHERE status = 'unmatched'").fetchall()]
    rejected = _rejected(con)
    pairs = []
    for inv in invs:
        for t in txns:
            sc = _score(inv, t, rejected)
            if sc is not None and sc >= MIN_SCORE:
                pairs.append((sc, inv, t))
    pairs.sort(key=lambda p: (-p[0], p[1]['id']))
    used_i, used_t, out = set(), set(), []
    for sc, inv, t in pairs:
        if inv['id'] in used_i or t['id'] in used_t:
            continue
        # an amount-only match that fits several invoices is ambiguous: leave it for a person
        out.append((sc, inv, t))
        used_i.add(inv['id'])
        used_t.add(t['id'])
    return out


def best_match_for_invoice(bot, con, inv):
    txns = [dict(r) for r in con.execute("SELECT * FROM bank_txns WHERE status = 'unmatched'").fetchall()]
    rejected = _rejected(con)
    best = None
    for t in txns:
        sc = _score(inv, t, rejected)
        if sc is not None and sc >= MIN_SCORE and (best is None or sc > best['score']):
            best = {'txn': t, 'score': sc, 'auto': sc >= AUTO_SCORE}
    return best


def link(bot, con, inv_id, txn_id, score=None, actor='admin'):
    """Confirm: invoice inv_id was paid by bank payment txn_id (caller commits)."""
    t = con.execute('SELECT * FROM bank_txns WHERE id = ?', (txn_id,)).fetchone()
    if t is None:
        raise KeyError(f'no bank payment #{txn_id}')
    if t['invoice_id'] and t['invoice_id'] != inv_id and t['status'] == 'matched':
        raise ValueError(f'bank payment #{txn_id} is already matched to invoice #{t["invoice_id"]}')
    inv = dbm.get_invoice(con, inv_id)
    if inv.get('bank_txn_id') and inv['bank_txn_id'] != txn_id:
        con.execute("UPDATE bank_txns SET invoice_id = NULL, status = 'unmatched', score = NULL WHERE id = ?",
                    (inv['bank_txn_id'],))
    con.execute("UPDATE bank_txns SET invoice_id = ?, status = 'matched', score = ? WHERE id = ?",
                (inv_id, score, txn_id))
    ov = dict(inv.get('overrides') or {})
    if ov.pop('unpaid', None):
        dbm.update_invoice(con, inv_id, {'overrides': ov})
    dbm.update_invoice(con, inv_id, {'bank_txn_id': txn_id})
    touched = set()
    inv = P.recompute_and_file(bot, con, inv_id, touched)
    dbm.log_event(con, 'bank_matched', inv_id, actor, {'txn': txn_id, 'date': t['date'], 'amount': t['amount'],
                                                      'score': score})
    return touched


def unlink(bot, con, inv_id, actor='admin', reject=True):
    inv = dbm.get_invoice(con, inv_id)
    txn = inv.get('bank_txn_id')
    if not txn:
        return set()
    con.execute("UPDATE bank_txns SET invoice_id = NULL, status = 'unmatched', score = NULL WHERE id = ?", (txn,))
    dbm.update_invoice(con, inv_id, {'bank_txn_id': None})
    if reject:
        rej = dbm.meta_get(con, 'bank_rejected', [])
        rej.append([inv_id, txn])
        dbm.meta_set(con, 'bank_rejected', rej)
    touched = set()
    P.recompute_and_file(bot, con, inv_id, touched)
    dbm.log_event(con, 'bank_unmatched', inv_id, actor, {'txn': txn})
    return touched


def reject(bot, con, inv_id, txn_id):
    rej = dbm.meta_get(con, 'bank_rejected', [])
    rej.append([inv_id, txn_id])
    dbm.meta_set(con, 'bank_rejected', rej)


def match_all(bot, apply=True, actor='bot'):
    """Apply confident matches; return {'matched': [...], 'suggestions': [...]}."""
    matched, suggestions = [], []
    touched = set()
    with bot.files_lock:
        con = bot.db()
        try:
            with con:
                for sc, inv, t in propose(bot, con):
                    item = {'invoice_id': inv['id'], 'supplier': inv['supplier'], 'invoice_number': inv['invoice_number'],
                            'amount': inv['amount'], 'currency': inv['currency'], 'txn_id': t['id'],
                            'paid_on': t['date'], 'counterparty': t['counterparty'], 'reference': t['description'],
                            'score': round(sc)}
                    if apply and sc >= AUTO_SCORE:
                        touched |= link(bot, con, inv['id'], t['id'], sc, actor=actor)
                        matched.append(item)
                    else:
                        suggestions.append(item)
        finally:
            con.close()
    P._write_summaries(bot, touched)
    return {'matched': matched, 'suggestions': suggestions}
