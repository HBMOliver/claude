"""Downloads: ZIP files of invoices (a month, a year or a selection) with a CSV summary, and the
_summary.csv kept in every archive folder."""
import csv
import io
import os
import re
import tempfile
import zipfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path, PurePosixPath

from . import db as dbm
from .pipeline import SOURCE_LABELS
from .util import now_iso

COLUMNS = [
    ('payment_date', 'Payment date'), ('supplier', 'Supplier'), ('invoice_number', 'Invoice number'),
    ('amount', 'Amount'), ('currency', 'Currency'), ('issue_date', 'Issue date'), ('due_date', 'Due date'),
    ('paid', 'Payment confirmed'), ('payment_source', 'How the payment date is known'),
    ('payment_method', 'Payment method'), ('doc_type', 'Document type'), ('supplier_tax_id', 'Supplier tax number'),
    ('status', 'Status'), ('file', 'File'), ('id', 'Ledger ID'),
]


def period_filter(period):
    """'2026' or '2026-09' -> (sql, params) on the payment date."""
    if not re.fullmatch(r'\d{4}(?:-\d{2})?', period or ''):
        raise ValueError('period must be YYYY or YYYY-MM')
    return 'payment_date LIKE ?', (period + '%',)


def select(bot, con, period=None, ids=None, include_unpaid=False):
    """Invoices for a download. A month/year means: paid in that period (plus, if asked or if the
    archive files unpaid invoices by expected date, the unpaid ones expected then)."""
    if ids:
        qs = ','.join('?' for _ in ids)
        return dbm.find_invoices(con, f'id IN ({qs})', tuple(int(i) for i in ids))
    sql, params = period_filter(period)
    estimate = bot.cfg['payment'].get('unconfirmed') == 'estimate'
    paid_clause = '' if include_unpaid or estimate else ' AND paid = 1'
    return dbm.find_invoices(con, f"status = 'filed' AND {sql}{paid_clause}", params)


def _fmt_amount(bot, v):
    if v in (None, ''):
        return ''
    s = f'{Decimal(v):.2f}'
    return s.replace('.', bot.cfg['csv'].get('decimal', '.'))


_FORMULA = re.compile(r'^[=+\-@\t\r]')
_PLAIN_NUMBER = re.compile(r'^-?\d[\d .,]*$')


def _cell(v):
    """Text read from invoices must never become a live spreadsheet formula ('=HYPERLINK(...)')."""
    s = '' if v is None else str(v)
    if _FORMULA.match(s) and not _PLAIN_NUMBER.match(s):
        return "'" + s
    return s


def csv_bytes(bot, invs):
    delim = bot.cfg['csv'].get('delimiter', ',')
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=delim, lineterminator='\r\n')
    w.writerow([label for _, label in COLUMNS])
    for inv in invs:
        row = []
        for key, _ in COLUMNS:
            if key == 'amount':
                row.append(_fmt_amount(bot, inv.get('amount')))
            elif key == 'paid':
                row.append('yes' if inv.get('paid') else 'no (expected)')
            elif key == 'payment_source':
                row.append(SOURCE_LABELS.get(inv.get('payment_source'), inv.get('payment_source') or ''))
            elif key == 'file':
                row.append(PurePosixPath(inv.get('file_path') or '').name)
            else:
                row.append(inv.get(key))
        w.writerow([_cell(c) for c in row])
    totals = {}
    for inv in invs:
        if inv.get('amount') not in (None, ''):
            totals[inv.get('currency') or ''] = totals.get(inv.get('currency') or '', Decimal(0)) + Decimal(inv['amount'])
    if totals:
        w.writerow([])
        for cur, tot in sorted(totals.items()):
            w.writerow(['Total', '', '', _fmt_amount(bot, tot), cur])
    return ('﻿' + buf.getvalue()).encode('utf-8')  # BOM: Excel opens it as UTF-8


def zip_to(bot, invs, out, title, period=None):
    """Write a ZIP with the invoice files and summary.csv. A month's ZIP holds the files directly, a
    year's ZIP one folder per month, a selection keeps the archive folders."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    missing, used = [], set()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for inv in invs:
            src = bot.archive / inv['file_path']
            if not src.is_file():
                missing.append(inv['file_path'])
                continue
            name = PurePosixPath(inv['file_path']).name
            if period and len(period) == 7:
                arc = f'{title}/{name}'
            elif period:
                arc = f"{title}/{(inv.get('payment_date') or '')[:7] or 'undated'}/{name}"
            else:
                arc = f"{title}/{inv['file_path']}"
            base, k = arc, 2
            while arc.lower() in used:
                stem, dot, ext = base.rpartition('.')
                arc = f'{stem}_{k}.{ext}'
                k += 1
            used.add(arc.lower())
            zf.write(src, arc)
        zf.writestr(f'{title}/summary.csv', csv_bytes(bot, invs))
        if missing:
            zf.writestr(f'{title}/MISSING_FILES.txt', '\n'.join(missing) + '\n')
    return out, missing


def export(bot, period=None, ids=None, include_unpaid=False, out=None):
    con = bot.db()
    try:
        invs = select(bot, con, period, ids, include_unpaid)
        title = f'invoices_{period}' if period else f'invoices_selection_{datetime.now():%Y%m%d-%H%M%S}'
        out = Path(out) if out else bot.exports / f'{title}.zip'
        path, missing = zip_to(bot, invs, out, title, period)
        return {'path': str(path), 'count': len(invs) - len(missing), 'missing': missing, 'title': title}
    finally:
        con.close()


def months(con):
    """[(yyyy-mm, count, {currency: total})] of paid, filed invoices, newest first."""
    out = {}
    for r in con.execute("SELECT substr(payment_date, 1, 7) AS m, currency, amount FROM invoices "
                         "WHERE status = 'filed' AND paid = 1 AND payment_date IS NOT NULL").fetchall():
        m = out.setdefault(r['m'], {'count': 0, 'totals': {}})
        m['count'] += 1
        if r['amount']:
            m['totals'][r['currency']] = m['totals'].get(r['currency'], Decimal(0)) + Decimal(r['amount'])
    return [(k, v['count'], v['totals']) for k, v in sorted(out.items(), reverse=True)]


def write_folder_summaries(bot, folders):
    """Refresh <folder>/_summary.csv for every archive folder that changed."""
    with bot.files_lock:
        con = bot.db()
        try:
            for folder in sorted(folders):
                if folder in ('', '.'):
                    continue
                try:
                    _write_summary(bot, con, folder)
                except OSError:  # a summary is a convenience: never fail the operation for it
                    bot.log.exception('could not write the summary of %s', folder)
        finally:
            con.close()


def _write_summary(bot, con, folder):
    d = bot.archive / folder
    invs = [i for i in dbm.find_invoices(con, 'file_path LIKE ?', (folder.rstrip('/') + '/%',))
            if str(PurePosixPath(i['file_path']).parent) == folder]
    target = d / '_summary.csv'
    if not invs:
        if target.exists():
            target.unlink()
        try:
            d.rmdir()
        except OSError:
            pass
        return
    d.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.summary-', suffix='.tmp', dir=d)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(csv_bytes(bot, invs))
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
