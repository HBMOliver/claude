"""HTML for the admin panel. Every dynamic value goes through e() (HTML-escaped)."""
import calendar
import html
from datetime import date
from decimal import Decimal
from pathlib import PurePosixPath
from urllib.parse import quote

from .pipeline import DOC_TYPES, METHODS, SOURCE_LABELS
from .util import money, today, to_date

MONTHS = [calendar.month_name[i] for i in range(13)]
SHORT = [calendar.month_abbr[i] for i in range(13)]
METHOD_LABELS = {'transfer': 'Bank transfer', 'card': 'Card', 'cash': 'Cash', 'paypal': 'PayPal',
                 'direct_debit': 'Direct debit', 'cod': 'Cash on delivery', 'online': 'Online payment'}
TYPE_LABELS = {'invoice': 'Invoice', 'receipt': 'Receipt', 'credit_note': 'Credit note',
               'proforma': 'Proforma / payment request', 'unknown': 'Unknown'}
EVENT_LABELS = {'added': 'Added', 'moved': 'Renamed / moved', 'updated': 'Edited', 'reextracted': 'Read again',
                'bank_matched': 'Matched to a bank payment', 'bank_unmatched': 'Bank match removed',
                'downloaded': 'Downloaded', 'collected': 'Collected'}
MESSAGES = {
    'saved': 'Changes saved. The file name and folder were updated to match.',
    'paid': 'Marked as paid. The invoice moved into its payment month.',
    'unpaid': 'Marked as not paid. It now waits in the unpaid folder.',
    'reextracted': 'The file was read again with the current rules.',
    'ignored': 'Moved to other documents.',
    'restored': 'Moved back to the invoices.',
    'notdup': 'No longer treated as a duplicate.',
    'unlinked': 'Bank match removed.',
    'collecting': 'Collecting new invoices now. Refresh in a minute to see them.',
    'busy': 'A collection is already running.',
    'uploaded': 'Upload processed.',
    'linked': 'Payment confirmed from the bank statement.',
    'rejected': 'Suggestion dismissed.',
    'password': 'Password changed.',
    'supplier': 'Supplier saved. Its invoices were re-checked.',
    'loggedout': 'You are logged out.',
    'expired': 'Your session ended. Log in again.',
    'badcsrf': 'That form had expired, so nothing was changed. Try again.',
    'none': 'Nothing was selected.',
}


def e(v):
    return html.escape('' if v is None else str(v), quote=True)


def breakable(name):
    """A file name that may wrap after its _ separators."""
    return '_<wbr>'.join(e(part) for part in str(name).split('_'))


def stamp(inv, big=False, fresh=False):
    st = inv.get('status')
    if st == 'filed' and inv.get('paid'):
        cls, word = '', 'Paid'
    elif st == 'filed':
        cls, word = 'unpaid', 'Unpaid'
    elif st == 'review':
        cls, word = 'check', 'Check'
    elif st == 'duplicate':
        cls, word = 'other', 'Duplicate'
    else:
        cls, word = 'other', 'Other'
    extra = ''
    if big and st == 'filed':
        extra = f"<small>{e(inv.get('payment_date'))}{'' if inv.get('paid') else ' expected'}</small>"
    return (f'<span class="stamp {cls}{" big" if big else ""}{" fresh" if fresh else ""}">'
            f'{word}{extra}</span>')


def amount(inv):
    return e(money(inv.get('amount'), inv.get('currency')))


def totals(invs):
    out = {}
    for i in invs:
        if i.get('amount') not in (None, ''):
            out[i.get('currency') or ''] = out.get(i.get('currency') or '', Decimal(0)) + Decimal(i['amount'])
    return sorted(out.items())


def month_title(ym):
    y, m = ym.split('-')
    return f'{MONTHS[int(m)]} {y}'


def layout(ctx, title, body, active=''):
    u = ctx['user']
    counts = ctx.get('counts', {})
    nav = [('/', 'Overview', ''), ('/review', 'To check', counts.get('review')),
           ('/unpaid', 'Waiting for payment', counts.get('unpaid')), ('/upload', 'Upload', ''),
           ('/bank', 'Bank statement', counts.get('suggestions')), ('/suppliers', 'Suppliers', '')]
    if u['role'] != 'admin':
        nav = [n for n in nav if n[0] not in ('/upload', '/bank')]
    links = []
    for href, label, n in nav:
        cur = ' aria-current="page"' if href == active else ''
        badge = ''
        if n:
            badge = f' <b class="count{" waiting" if href in ("/unpaid", "/bank") else ""}">{e(n)}</b>'
        links.append(f'<a href="{href}"{cur}>{e(label)}{badge}</a>')
    flash = ''
    if ctx.get('flash'):
        cls, text = ctx['flash']
        flash = f'<p class="flash {e(cls)}" role="status">{e(text)}</p>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | Invoice Bot</title><link rel="stylesheet" href="/static/app.css"><script src="/static/app.js" defer></script>
</head><body>
<header class="top">
<a class="brand" href="/">Invoice Bot<span>{e(ctx.get('company') or 'Invoices by payment month')}</span></a>
<nav aria-label="Main">{''.join(links)}</nav>
<form class="search" action="/search" role="search"><input type="search" name="q" aria-label="Search invoices"
 placeholder="Search invoices" title="Supplier, invoice number or amount" value="{e(ctx.get('q', ''))}"></form>
<div class="me"><span>{e(u['username'])}{' (view only)' if u['role'] != 'admin' else ''}</span>
<a href="/account">Account</a>
<form method="post" action="/logout" class="inline">{csrf(ctx)}<button class="link" type="submit">Log out</button></form></div>
</header>
<main>{flash}{body}</main>
</body></html>'''


def csrf(ctx):
    return f'<input type="hidden" name="csrf" value="{e(ctx.get("csrf"))}">'


def login_page(token, message=None, error=False, next_url=''):
    msg = f'<p class="flash{" error" if error else ""}" role="status">{e(message)}</p>' if message else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log in | Invoice Bot</title><link rel="stylesheet" href="/static/app.css"></head><body>
<form class="login" method="post" action="/login">
<h1>Invoice Bot</h1><p class="muted">Log in to see and download the invoices.</p>{msg}
<input type="hidden" name="login_token" value="{e(token)}"><input type="hidden" name="next" value="{e(next_url)}">
<label for="u">User name</label><input id="u" type="text" name="username" autocomplete="username" required autofocus>
<label for="p">Password</label><input id="p" type="password" name="password" autocomplete="current-password" required>
<button type="submit">Log in</button>
</form></body></html>'''


# ------------------------------------------------------------------ tables
def ledger(invs, ctx, cols=('paid_on', 'supplier', 'number', 'amount', 'how', 'file'), select=False, foot=True,
           empty='No invoices here yet.'):
    if not invs:
        return f'<div class="sheet"><p class="empty">{e(empty)}</p></div>'
    heads = {'paid_on': ('Paid on', ''), 'due': ('Due', ''), 'added': ('Added', ''), 'supplier': ('Supplier', ''),
             'number': ('Invoice no.', ''), 'amount': ('Amount', 'num'), 'how': ('How the payment date is known', ''),
             'file': ('File', ''), 'status': ('Status', ''), 'issues': ('What to check', ''),
             'markpaid': ('Mark as paid', ''), 'original': ('Original file', ''), 'overdue': ('', 'num')}
    th = ''.join(f'<th class="c-{k} {heads[k][1]}">{e(heads[k][0])}</th>' for k in cols)
    if select:
        th = '<th class="c-select"><input type="checkbox" data-select-all aria-label="Select all"></th>' + th
    rows = []
    t = today()
    for inv in invs:
        tds = []
        if select:
            tds.append(f'<td class="c-select"><input type="checkbox" name="ids" value="{inv["id"]}" aria-label="Select invoice {inv["id"]}"></td>')
        for k in cols:
            if k == 'paid_on':
                tds.append(f'<td class="c-paid_on">{e(inv.get("payment_date") or "-")} {stamp(inv)}</td>')
            elif k == 'due':
                tds.append(f'<td class="c-due num">{e(inv.get("due_date") or inv.get("payment_date") or "-")}</td>')
            elif k == 'added':
                tds.append(f'<td class="c-added num">{e((inv.get("created_at") or "")[:10])}</td>')
            elif k == 'supplier':
                tds.append(f'<td class="c-supplier"><a href="/invoices/{inv["id"]}">{e(inv.get("supplier") or "Unknown supplier")}</a></td>')
            elif k == 'number':
                tds.append(f'<td class="c-number">{e(inv.get("invoice_number") or "-")}</td>')
            elif k == 'amount':
                tds.append(f'<td class="c-amount num">{amount(inv)}</td>')
            elif k == 'how':
                tds.append(f'<td class="c-how">{e(SOURCE_LABELS.get(inv.get("payment_source"), "-"))}</td>')
            elif k == 'file':
                name = PurePosixPath(inv.get('file_path') or '').name
                tds.append(f'<td class="c-file"><a href="/invoices/{inv["id"]}/file" download>{breakable(name)}</a></td>')
            elif k == 'status':
                tds.append(f'<td class="c-status">{stamp(inv)}</td>')
            elif k == 'issues':
                msgs = [i['msg'] for i in inv.get('issues') or [] if i['level'] in ('error', 'warn')]
                tds.append(f'<td class="c-issues">{"<br>".join(e(m) for m in msgs) or "-"}</td>')
            elif k == 'original':
                tds.append(f'<td class="c-original">{breakable(inv.get("original_name") or "")}</td>')
            elif k == 'overdue':
                due = to_date(inv.get('due_date'))
                late = (t - due).days if due else 0
                tds.append(f'<td class="c-overdue num">{f"<span class=overdue>{late} days overdue</span>" if late > 0 else ""}</td>')
            elif k == 'markpaid':
                if ctx['user']['role'] == 'admin':
                    tds.append(f'<td class="c-markpaid"><form method="post" action="/invoices/{inv["id"]}/paid" class="actions tight">'
                               f'{csrf(ctx)}<input type="hidden" name="back" value="/unpaid"><input type="date" name="date" value="{e(t.isoformat())}" aria-label="Payment date">'
                               f'<button type="submit" class="quiet">Paid</button></form></td>')
                else:
                    tds.append('<td></td>')
        rows.append('<tr>' + ''.join(tds) + '</tr>')
    tfoot = ''
    if foot and 'amount' in cols:
        i = cols.index('amount')
        before, after = cols[:i], cols[i + 1:]
        lines = []
        for n, (cur, tot) in enumerate(totals(invs)):
            cells = ['<td class="c-select"></td>'] if select else []
            for j, k in enumerate(before):
                label = 'Total' if n == 0 and j == len(before) - 1 else ''
                cells.append(f'<td class="c-{k} label">{label}</td>')
            cells.append(f'<td class="c-amount num">{e(money(tot, cur))}</td>')
            cells += [f'<td class="c-{k}"></td>' for k in after]
            lines.append('<tr>' + ''.join(cells) + '</tr>')
        tfoot = '<tfoot>' + ''.join(lines) + '</tfoot>'
    return (f'<div class="sheet"><table class="ledger{" selectable" if select else ""}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody>{tfoot}</table></div>')


# ------------------------------------------------------------------ pages
def overview(ctx, data):
    t = today()
    ym = f'{t:%Y-%m}'
    cur = data['months'].get(ym)
    if cur:
        main = ctx.get('currency')
        order = sorted(cur['totals'].items(), key=lambda kv: (kv[0] != main, kv[0]))
        figs = ''.join(f'<li class="fig">{e(money(v, k))}</li>' for k, v in order)
        lede = (f'<ol class="month-total">{figs}</ol><p class="muted">paid in {e(MONTHS[t.month])} so far, '
                f'{cur["count"]} invoice{"s" if cur["count"] != 1 else ""}. '
                f'<a href="/months/{ym}">See the month</a></p>')
    else:
        lede = f'<ol class="month-total"><li class="fig">0</li></ol><p class="muted">Nothing paid in {e(MONTHS[t.month])} yet.</p>'
    todo = []
    if data['review']:
        todo.append(f'<li><span><a href="/review">{data["review"]} invoice{"s need" if data["review"] != 1 else " needs"} '
                    f'checking</a>: something on {"them" if data["review"] != 1 else "it"} could not be read.</span></li>')
    if data['unpaid']:
        od = f', {data["overdue"]} overdue' if data['overdue'] else ''
        todo.append(f'<li><span><a href="/unpaid">{data["unpaid"]} waiting for payment</a>{e(od)}.</span></li>')
    if data.get('other'):
        todo.append(f'<li><span><a href="/other">{data["other"]} other document{"s" if data["other"] != 1 else ""}</a>: '
                    f'duplicates, proformas and files that are not invoices.</span></li>')
    if data['suggestions']:
        todo.append(f'<li><span><a href="/bank">{data["suggestions"]} possible bank match'
                    f'{"es" if data["suggestions"] != 1 else ""}</a> to confirm.</span></li>')
    last = data.get('last_run')
    if last:
        c = last['counts']
        when = last['finished'][:16].replace('T', ' ')
        lr = f'Last collection {e(when)} UTC: {c["new"]} new{", " + str(len(last["errors"])) + " errors" if last["errors"] else ""}.'
    else:
        lr = 'No collection has run yet.'
    button = ''
    if ctx['user']['role'] == 'admin':
        button = f'<form method="post" action="/collect" class="inline">{csrf(ctx)}<button type="submit" class="quiet">Collect now</button></form>'
    todo.append(f'<li><span class="muted">{lr}</span>{button}</li>')
    if not data['review'] and not data['unpaid']:
        todo.insert(0, '<li><span>Nothing to check and nothing waiting for payment.</span></li>')
    body = f'''<section class="lede"><div><h1>{e(MONTHS[t.month])} {t.year}</h1>{lede}</div>
<ul class="todo">{''.join(todo)}</ul></section>
<h2>Archive by payment month</h2>{cabinet(data['months'], t)}
<h2>Recently added</h2>{ledger(data['recent'], ctx, cols=('added', 'supplier', 'number', 'amount', 'status', 'file'), foot=False,
                                empty='No invoices yet. Drop PDFs into the inbox folder, upload them here, or connect a mailbox.')}'''
    return layout(ctx, 'Overview', body, '/')


def cabinet(months, t):
    years = sorted({int(k[:4]) for k in months} | {t.year}, reverse=True)
    rows = []
    for y in years:
        cells = [f'<div class="y">{y}</div>']
        for m in range(1, 13):
            key = f'{y}-{m:02d}'
            info = months.get(key)
            now = ' now' if (y, m) == (t.year, t.month) else ''
            if info:
                main = max(info['totals'].items(), key=lambda kv: kv[1]) if info['totals'] else None
                tot = e(money(main[1], main[0])) if main else ''
                cells.append(f'<a class="m{now}" href="/months/{key}" aria-label="{e(MONTHS[m])} {y}: {info["count"]} invoices">'
                             f'<b>{SHORT[m]}</b><span>{info["count"]} paid</span><span>{tot}</span></a>')
            else:
                cells.append(f'<div class="m none{now}"><b>{SHORT[m]}</b></div>')
        has = any(k.startswith(str(y)) for k in months)
        cells.append(f'<div class="zip">{f"<a href=/download/{y}.zip>Year as ZIP</a>" if has else ""}</div>')
        rows.append('<div class="year">' + ''.join(cells) + '</div>')
    return '<div class="cabinet">' + ''.join(rows) + '</div>'


def month_page(ctx, ym, invs, unpaid_expected):
    y, m = int(ym[:4]), int(ym[5:])
    prev = date(y - 1, 12, 1) if m == 1 else date(y, m - 1, 1)
    nxt = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    title = month_title(ym)
    extra = ''
    if unpaid_expected:
        extra = (f'<h2>Expected this month, not paid yet</h2>{ledger(unpaid_expected, ctx, cols=("due", "supplier", "number", "amount", "overdue", "markpaid"))}')
    body = f'''<h1>{e(title)}</h1>
<p class="muted">Invoices paid in {e(title)}, by payment date. <a href="/months/{prev:%Y-%m}">{e(MONTHS[prev.month])}</a> |
<a href="/months/{nxt:%Y-%m}">{e(MONTHS[nxt.month])}</a></p>
<div class="actions"><a class="button" href="/download/{e(ym)}.zip">Download {e(MONTHS[m])} (ZIP)</a>
<a class="button quiet" href="/download/{e(ym)}.csv">Summary (CSV)</a></div>
<form method="post" action="/download/selection">{csrf(ctx)}
{ledger(invs, ctx, select=True, empty="No invoices were paid in this month.")}
{'<div class="actions"><button type="submit" class="quiet">Download selected (ZIP)</button></div>' if invs else ''}
</form>{extra}'''
    return layout(ctx, title, body)


def list_page(ctx, title, intro, invs, cols, active, empty, foot=True):
    body = f'<h1>{e(title)}</h1><p class="muted">{e(intro)}</p>{ledger(invs, ctx, cols=cols, foot=foot, empty=empty)}'
    return layout(ctx, title, body, active)


def invoice_page(ctx, inv, events, bank_txn, error=None, fresh=False):
    admin = ctx['user']['role'] == 'admin'
    ex = inv.get('extracted') or {}
    ov = inv.get('overrides') or {}
    is_image = PurePosixPath(inv['file_path']).suffix.lower() in ('.jpg', '.jpeg', '.png')
    src = f'/invoices/{inv["id"]}/file?inline=1'
    preview = (f'<img src="{src}" alt="Invoice image">' if is_image else
               f'<iframe src="{src}" title="Invoice PDF"></iframe>')
    issues = ''.join(f'<li class="{e(i["level"])}">{e(i["msg"])}</li>' for i in inv.get('issues') or []
                     if not (inv.get('verified') and i['level'] == 'warn'))
    err = f'<p class="flash error" role="alert">{e(error)}</p>' if error else ''

    def field(name, label, value, kind='text', options=None, hint=None, wide=False):
        mark = ' <span class="manual">set by hand</span>' if name in ov else ''
        dis = '' if admin else ' disabled'
        if options:
            opts = ''.join(f'<option value="{e(v)}"{" selected" if v == (value or "") else ""}>{e(lab)}</option>'
                           for v, lab in options)
            inp = f'<select id="f_{name}" name="{name}"{dis}>{opts}</select>'
        else:
            inp = f'<input id="f_{name}" type="{kind}" name="{name}" value="{e(value)}"{dis}>'
        h = f'<div class="hint">{e(hint)}</div>' if hint else ''
        return f'<div class="{"wide" if wide else ""}"><label for="f_{name}">{e(label)}{mark}</label>{inp}{h}</div>'

    printed = ex.get('supplier_raw')
    sup_hint = f'Printed as: {printed}' if printed and printed != inv.get('supplier') else None
    pay_hint = SOURCE_LABELS.get(inv.get('payment_source'), '')
    if not inv.get('paid') and inv.get('payment_date'):
        pay_hint = f'Not confirmed. Expected {inv["payment_date"]} ({pay_hint}).'
    form = ''.join([
        field('supplier', 'Supplier', inv.get('supplier'), wide=True, hint=sup_hint),
        field('invoice_number', 'Invoice number', inv.get('invoice_number')),
        field('amount', 'Total amount', inv.get('amount')),
        field('currency', 'Currency', inv.get('currency')),
        field('doc_type', 'Document type', inv.get('doc_type'), options=[(t, TYPE_LABELS[t]) for t in DOC_TYPES]),
        field('issue_date', 'Invoice date', inv.get('issue_date'), 'date'),
        field('fulfilment_date', 'Delivery date', inv.get('fulfilment_date'), 'date'),
        field('due_date', 'Due date', inv.get('due_date'), 'date'),
        field('payment_method', 'Payment method', inv.get('payment_method'),
              options=[('', 'Not stated')] + [(m, METHOD_LABELS[m]) for m in METHODS]),
        field('payment_date', 'Paid on', ov.get('payment_date') or (inv.get('payment_date') if inv.get('paid') else ''),
              'date', wide=True, hint=pay_hint),
    ])
    save = f'<div class="actions"><button type="submit">Save changes</button></div>' if admin else ''
    acts = []
    if admin:
        def act(path, label, cls='quiet', confirm=None, extra=''):
            c = f' data-confirm="{e(confirm)}"' if confirm else ''
            return (f'<form method="post" action="/invoices/{inv["id"]}/{path}" class="inline">{csrf(ctx)}{extra}'
                    f'<button type="submit" class="{cls}"{c}>{e(label)}</button></form>')
        if inv['status'] == 'filed' and not inv.get('paid'):
            acts.append(act('paid', 'Mark as paid today'))
        if inv.get('paid'):
            acts.append(act('unpaid', 'Mark as not paid'))
        if inv.get('bank_txn_id'):
            acts.append(act('unlink', 'Remove bank match'))
        acts.append(act('reextract', 'Read the file again'))
        if inv['status'] == 'duplicate':
            acts.append(act('notdup', 'Not a duplicate'))
        if inv['status'] == 'ignored' and ov.get('status') == 'ignored':
            acts.append(act('restore', 'Move back to invoices'))
        elif inv['status'] != 'ignored':
            acts.append(act('ignore', 'Not an invoice', 'danger', 'Move this file to other documents?'))
    bank = ''
    if bank_txn:
        bank = (f'<div class="panel"><h2>Bank payment</h2><p>{e(bank_txn["date"])}: {e(money(bank_txn["amount"], bank_txn["currency"]))} '
                f'to {e(bank_txn["counterparty"] or "?")}<br><span class="muted">{e(bank_txn["description"])}</span></p></div>')
    hist = ''.join(f'<li>{e(ev["at"][:16].replace("T", " "))} <b>{e(EVENT_LABELS.get(ev["action"], ev["action"]))}</b> by {e(ev["actor"])}'
                   f'{_event_detail(ev)}</li>' for ev in events)
    text = inv.get('text') or ''
    body = f'''<div class="invoice"><div class="preview">{preview}</div><div>
<div class="title-row"><div><h1>{e(inv.get('supplier') or 'Unknown supplier')}</h1>
<p class="path">{e(inv.get('invoice_number') or 'no invoice number')} | {amount(inv)}<br>{e(inv['file_path'])}
<br><a href="/invoices/{inv['id']}/file" download>Download</a></p></div>{stamp(inv, big=True, fresh=fresh)}</div>
{err}<ul class="issues">{issues}</ul>
<form method="post" action="/invoices/{inv['id']}" class="panel">{csrf(ctx)}<div class="fields">{form}</div>{save}</form>
{f'<div class="actions">{"".join(acts)}</div>' if acts else ''}{bank}
<div class="panel"><h2>History</h2><ol class="history">{hist or '<li>No changes yet.</li>'}</ol></div>
<details class="panel"><summary>Text read from the file ({e(inv.get('text_method'))})</summary><pre class="text">{e(text)}</pre></details>
<p class="muted">Received {e((inv.get('received_at') or '')[:16].replace('T', ' '))} UTC from {e(inv.get('source'))}:
{e(inv.get('original_name'))}{_sender(inv)}</p>
</div></div>'''
    return layout(ctx, inv.get('supplier') or f'Invoice {inv["id"]}', body)


def _sender(inv):
    sd = inv.get('source_detail') or {}
    if sd.get('sender'):
        return f'<br>E-mail from {e(sd["sender"])}: {e(sd.get("subject"))}'
    return ''


def _event_detail(ev):
    d = ev.get('detail')
    if not isinstance(d, dict):
        return ''
    if ev['action'] == 'moved':
        return f': {e(d.get("from"))} to {e(d.get("to"))}'
    if ev['action'] == 'updated':
        ch = d.get('changed') or {}
        parts = [f'{k}: {v[0]} to {v[1]}' for k, v in ch.items()]
        return ': ' + e('; '.join(parts)) if parts else ''
    if ev['action'] == 'bank_matched':
        return f': paid {e(d.get("date"))}'
    if ev['action'] == 'downloaded':
        return ''
    if ev['action'] == 'added':
        return f': {e(d.get("name"))} from {e(d.get("source"))}'
    return ''


def upload_page(ctx, report=None):
    res = ''
    if report is not None:
        items = ''.join(f'<li>{e(it.get("name") or it.get("original_name"))}: '
                        f'{_result_text(it)}</li>' for it in report.items) or '<li>No files were processed.</li>'
        errs = ''.join(f'<li class="error">{e(x["where"])}: {e(x["error"])}</li>' for x in report.errors)
        res = f'<div class="panel"><h2>Result</h2><ul class="issues">{errs}</ul><ul>{items}</ul></div>'
    body = f'''<h1>Upload invoices</h1>
<p class="muted">PDFs, photos, saved e-mails (.eml) or ZIP files. Each invoice is read, renamed and filed by payment date.</p>
{res}<form method="post" action="/upload" enctype="multipart/form-data" class="panel">{csrf(ctx)}
<label for="files">Files</label><input id="files" type="file" name="files" multiple required
 accept=".pdf,.jpg,.jpeg,.png,.tif,.tiff,.eml,.zip">
<div class="actions"><button type="submit">Upload and file</button></div></form>'''
    return layout(ctx, 'Upload', body, '/upload')


def _result_text(it):
    if it['result'] == 'new':
        where = e(it.get('file_path'))
        return f'<a href="/invoices/{it["id"]}">{e(it.get("supplier") or "invoice")}</a> filed as {where} {stamp(it)}'
    if it['result'] == 'duplicate_file':
        return f'already in the archive (<a href="/invoices/{it["id"]}">#{it["id"]}</a>)'
    return e(f"skipped: {it.get('reason')}")


def bank_page(ctx, result=None, suggestions=(), recent=()):
    res = ''
    if result:
        res = (f'<div class="panel"><h2>Imported</h2><p>{result.get("payments_in_file", 0)} outgoing payments in the file, '
               f'{result.get("new_payments", 0)} new. {len(result.get("matched", []))} invoices confirmed as paid.</p>'
               f'<ul>{"".join(_match_li(m) for m in result.get("matched", []))}</ul></div>')
    sug = ''
    if suggestions:
        rows = []
        for m in suggestions:
            rows.append(f'''<tr><td><a href="/invoices/{m['invoice_id']}">{e(m['supplier'])}</a><br><span class="muted">{e(m['invoice_number'])}</span></td>
<td class="num">{e(money(m['amount'], m['currency']))}</td><td class="num">{e(m['paid_on'])}</td>
<td>{e(m['counterparty'] or '?')}<br><span class="muted">{e(m['reference'])}</span></td><td class="num">{m['score']}</td>
<td><form method="post" action="/bank/link" class="inline">{csrf(ctx)}<input type="hidden" name="invoice" value="{m['invoice_id']}">
<input type="hidden" name="txn" value="{m['txn_id']}"><button type="submit">Confirm</button></form>
<form method="post" action="/bank/reject" class="inline">{csrf(ctx)}<input type="hidden" name="invoice" value="{m['invoice_id']}">
<input type="hidden" name="txn" value="{m['txn_id']}"><button type="submit" class="quiet">Not this one</button></form></td></tr>''')
        sug = ('<h2>Possible matches to confirm</h2><p class="muted">The amount matches, but the reference does not clearly '
               'name the invoice.</p><div class="sheet"><table class="ledger"><thead><tr><th>Invoice</th><th class="num">Amount</th>'
               '<th>Paid on</th><th>Bank payment</th><th class="num">Score</th><th></th></tr></thead><tbody>'
               + ''.join(rows) + '</tbody></table></div>')
    rec = ''
    if recent:
        rec = '<h2>Recently confirmed from the bank</h2><ul>' + ''.join(_match_li(m) for m in recent) + '</ul>'
    body = f'''<h1>Bank statement</h1>
<p class="muted">Upload your bank's CSV export. Outgoing payments are matched to unpaid invoices, which then move into
the month they were paid in.</p>{res}
<form method="post" action="/bank" enctype="multipart/form-data" class="panel">{csrf(ctx)}<div class="fields">
<div class="wide"><label for="stmt">Statement (CSV)</label><input id="stmt" type="file" name="statement" accept=".csv,.txt" required></div>
<div class="wide"><label for="acct">Account name (optional)</label><input id="acct" type="text" name="account" placeholder="e.g. OTP HUF"></div>
</div><div class="actions"><button type="submit">Import and match</button></div></form>{sug}{rec}'''
    return layout(ctx, 'Bank statement', body, '/bank')


def _match_li(m):
    return (f'<li><a href="/invoices/{m["invoice_id"]}">{e(m["supplier"])} {e(m["invoice_number"])}</a>: '
            f'{e(money(m["amount"], m["currency"]))} paid {e(m["paid_on"])}</li>')


def suppliers_page(ctx, rows):
    admin = ctx['user']['role'] == 'admin'
    opts = [('', 'Not automatic'), ('issue_date', 'Paid on the invoice date'), ('due_date', 'Paid on the due date'),
            ('fulfilment_date', 'Paid on the delivery date')]
    trs = []
    for r in rows:
        sel = ''.join(f'<option value="{v}"{" selected" if (r["paid_on"] or "") == v else ""}>{e(l)}</option>' for v, l in opts)
        form = (f'<form method="post" action="/suppliers" class="actions tight">{csrf(ctx)}'
                f'<input type="hidden" name="name" value="{e(r["name"])}"><select name="paid_on" aria-label="Payment rule">{sel}</select>'
                f'<button type="submit" class="quiet">Save</button></form>') if admin else e(dict(opts).get(r['paid_on'] or '', ''))
        trs.append(f'<tr><td>{e(r["name"])}</td><td>{e(", ".join(r["aliases"]))}</td><td>{e(", ".join(r["tax_ids"]))}</td>'
                   f'<td>{e(", ".join(r["domains"]))}</td><td>{form}</td></tr>')
    body = f'''<h1>Suppliers</h1>
<p class="muted">How the bot recognises suppliers and names their files. Corrections you make on an invoice are added here.
For suppliers that charge your card automatically, set a payment rule: their invoices then count as paid without a bank match.</p>
<div class="sheet"><table class="ledger"><thead><tr><th>Name in file names</th><th>Names on invoices</th><th>Tax numbers</th>
<th>E-mail domains</th><th>Payment rule</th></tr></thead><tbody>{"".join(trs) or '<tr><td colspan=5 class=empty>No suppliers yet.</td></tr>'}</tbody></table></div>'''
    return layout(ctx, 'Suppliers', body, '/suppliers')


def account_page(ctx, error=None):
    err = f'<p class="flash error" role="alert">{e(error)}</p>' if error else ''
    body = f'''<h1>Account</h1><p class="muted">Signed in as {e(ctx['user']['username'])} ({e(ctx['user']['role'])}).</p>{err}
<form method="post" action="/account" class="panel narrow">{csrf(ctx)}
<label for="cur">Current password</label><input id="cur" type="password" name="current" autocomplete="current-password" required class="full">
<label for="new">New password (10 characters or more)</label><input id="new" type="password" name="new" autocomplete="new-password" required class="full">
<label for="again">New password again</label><input id="again" type="password" name="again" autocomplete="new-password" required class="full">
<button type="submit">Change password</button></form>'''
    return layout(ctx, 'Account', body)


def error_page(ctx, status, message):
    body = f'<h1>{e(status)}</h1><p>{e(message)}</p><p><a href="/">Back to the overview</a></p>'
    if ctx and ctx.get('user'):
        return layout(ctx, str(status), body)
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(status)}</title>' \
           f'<link rel="stylesheet" href="/static/app.css"></head><body><main>{body}</main></body></html>'
