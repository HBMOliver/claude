"""The admin panel: a small, dependency-free web server.

    invoice_bot.py serve [--host 127.0.0.1] [--port 8765] [--collect-every 30]

Security: logins with scrypt-hashed passwords, random session tokens (HttpOnly, SameSite=Strict
cookies), a CSRF token on every form, login throttling per address, strict Content-Security-Policy,
files served only by ledger id from inside the archive, and an audit trail of every change and
download. It listens on 127.0.0.1 by default: to reach it from other computers put it behind an HTTPS
reverse proxy (or a VPN such as Tailscale) and set admin.secure_cookies = true.
"""
import email.parser
import email.policy
import hmac
import mimetypes
import os
import re
import secrets
import tempfile
import threading
import time
import traceback
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, quote, urlencode, urlsplit

from . import auth
from . import bank
from . import collect
from . import db as dbm
from . import export
from . import pipeline as P
from . import suppliers as S
from . import views as V
from .util import jload, today

ASSETS = Path(__file__).resolve().parent / 'assets'
STATIC = {'app.css': 'text/css; charset=utf-8', 'app.js': 'text/javascript; charset=utf-8',
          'fonts/YoungSerif-Regular.ttf': 'font/ttf', 'fonts/InstrumentSans-Regular.ttf': 'font/ttf',
          'fonts/InstrumentSans-Bold.ttf': 'font/ttf'}
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; "
       "frame-src 'self'; object-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'")
COOKIE = 'ib_session'
LOGIN_COOKIE = 'ib_login'
FILE_TYPES = {'.pdf': 'application/pdf', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
              '.tif': 'image/tiff', '.tiff': 'image/tiff'}


class HttpError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status, self.message = status, message


class Redirect(Exception):
    def __init__(self, location):
        super().__init__(location)
        self.location = location


class Throttle:
    """At most `limit` failed logins per address per window; then a lockout for the rest of it."""

    def __init__(self, limit=8, window=900):
        self.limit, self.window = limit, window
        self.fails = {}
        self.lock = threading.Lock()

    def blocked(self, ip):
        with self.lock:
            hits = [t for t in self.fails.get(ip, []) if time.time() - t < self.window]
            self.fails[ip] = hits
            return len(hits) >= self.limit

    def fail(self, ip):
        with self.lock:
            self.fails.setdefault(ip, []).append(time.time())

    def ok(self, ip):
        with self.lock:
            self.fails.pop(ip, None)


class App:
    def __init__(self, bot):
        self.bot = bot
        self.throttle = Throttle()
        self.collecting = threading.Lock()
        self.routes = [
            ('GET', r'/login', self.login_form, None),
            ('POST', r'/login', self.login, None),
            ('POST', r'/logout', self.logout, 'viewer'),
            ('GET', r'/', self.overview, 'viewer'),
            ('GET', r'/months/(\d{4}-\d{2})', self.month, 'viewer'),
            ('GET', r'/review', self.review, 'viewer'),
            ('GET', r'/unpaid', self.unpaid, 'viewer'),
            ('GET', r'/other', self.other, 'viewer'),
            ('GET', r'/search', self.search, 'viewer'),
            ('GET', r'/invoices/(\d+)', self.invoice, 'viewer'),
            ('GET', r'/invoices/(\d+)/file', self.invoice_file, 'viewer'),
            ('POST', r'/invoices/(\d+)', self.invoice_save, 'admin'),
            ('POST', r'/invoices/(\d+)/(paid|unpaid|reextract|ignore|restore|unlink|notdup)', self.invoice_action, 'admin'),
            ('GET', r'/download/(\d{4}(?:-\d{2})?)\.(zip|csv)', self.download_period, 'viewer'),
            ('POST', r'/download/selection', self.download_selection, 'viewer'),
            ('GET', r'/upload', self.upload_form, 'admin'),
            ('POST', r'/upload', self.upload, 'admin'),
            ('GET', r'/bank', self.bank_page, 'admin'),
            ('POST', r'/bank', self.bank_upload, 'admin'),
            ('POST', r'/bank/(link|reject)', self.bank_action, 'admin'),
            ('POST', r'/collect', self.collect_now, 'admin'),
            ('GET', r'/suppliers', self.suppliers, 'viewer'),
            ('POST', r'/suppliers', self.supplier_save, 'admin'),
            ('GET', r'/account', self.account, 'viewer'),
            ('POST', r'/account', self.account_save, 'viewer'),
            ('GET', r'/static/(.+)', self.static, None),
        ]
        self.routes = [(m, re.compile(p + r'\Z'), fn, role) for m, p, fn, role in self.routes]

    # ------------------------------------------------------------ plumbing
    def context(self, req, con):
        q = lambda sql: con.execute(sql).fetchone()[0]
        counts = {'review': q("SELECT count(*) FROM invoices WHERE status = 'review'"),
                  'unpaid': q("SELECT count(*) FROM invoices WHERE status = 'filed' AND paid = 0")}
        flash = None
        m = req.query.get('m')
        if m in V.MESSAGES:
            flash = ('error' if m in ('badcsrf', 'expired', 'none', 'busy') else '', V.MESSAGES[m])
        return {'user': req.user, 'csrf': req.csrf, 'counts': counts, 'flash': flash,
                'company': self.bot.company.get('name'), 'q': req.query.get('q', ''),
                'currency': self.bot.cfg['default_currency']}

    def dispatch(self, req):
        path = req.path
        allowed_method = False
        for method, rx, fn, role in self.routes:
            m = rx.match(path)
            if not m:
                continue
            if method != req.method:
                allowed_method = True
                continue
            if role:
                if not req.user:
                    if req.method == 'GET':
                        raise Redirect('/login' + ('?' + urlencode({'next': req.raw_path}) if path != '/' else ''))
                    raise Redirect('/login?m=expired')
                if role == 'admin' and req.user['role'] != 'admin':
                    raise HttpError(403, 'Your account can view and download, but not change invoices.')
                if req.method == 'POST' and not hmac.compare_digest(req.form_value('csrf'), req.csrf or ''):
                    raise Redirect(req.back('m=badcsrf'))
            return fn(req, *m.groups())
        if allowed_method:
            raise HttpError(405, 'Method not allowed.')
        raise HttpError(404, 'There is nothing at this address.')

    # ------------------------------------------------------------ auth
    def login_form(self, req):
        token = secrets.token_urlsafe(16)
        msg = V.MESSAGES.get(req.query.get('m', ''))
        nxt = req.query.get('next', '')
        return Response(V.login_page(token, msg, error=req.query.get('m') == 'expired',
                                     next_url=nxt if nxt.startswith('/') and not nxt.startswith('//') else ''),
                        cookies=[(LOGIN_COOKIE, token, 600)])

    def login(self, req):
        ip = req.client_ip
        token = req.cookies.get(LOGIN_COOKIE, '')
        if not token or not hmac.compare_digest(token, req.form_value('login_token')):
            return Response(V.login_page(secrets.token_urlsafe(16), 'That form had expired. Try again.', True), status=400)
        if self.throttle.blocked(ip):
            return Response(V.login_page(token, 'Too many failed attempts. Try again in 15 minutes.', True), status=429)
        con = self.bot.db()
        try:
            with con:
                user = auth.authenticate(con, req.form_value('username').strip(), req.form_value('password'))
                if not user:
                    self.throttle.fail(ip)
                    time.sleep(0.4)
                    self.bot.log.warning('failed login for %r from %s', req.form_value('username')[:64], ip)
                    return Response(V.login_page(token, 'User name or password is wrong.', True), status=401)
                self.throttle.ok(ip)
                sess = auth.new_session(con, user['username'], self.bot.cfg['admin'].get('session_hours', 12))
                dbm.log_event(con, 'login', None, user['username'], {'ip': ip})
        finally:
            con.close()
        nxt = req.form_value('next') or req.query.get('next') or '/'
        if not nxt.startswith('/') or nxt.startswith('//'):
            nxt = '/'
        hours = self.bot.cfg['admin'].get('session_hours', 12)
        return Response(status=303, headers={'Location': nxt}, cookies=[(COOKIE, sess, hours * 3600), (LOGIN_COOKIE, '', 0)])

    def logout(self, req):
        con = self.bot.db()
        try:
            with con:
                auth.end_session(con, req.cookies.get(COOKIE))
        finally:
            con.close()
        return Response(status=303, headers={'Location': '/login?m=loggedout'}, cookies=[(COOKIE, '', 0)])

    def account(self, req):
        return self.page(req, lambda ctx, con: V.account_page(ctx))

    def account_save(self, req):
        con = self.bot.db()
        try:
            new, again = req.form_value('new'), req.form_value('again')
            err = None
            if not auth.authenticate(con, req.user['username'], req.form_value('current')):
                err = 'The current password is wrong.'
            elif new != again:
                err = 'The new passwords do not match.'
            else:
                try:
                    with con:
                        auth.set_password(con, req.user['username'], new)
                        dbm.log_event(con, 'password_changed', None, req.user['username'])
                except ValueError as ex:
                    err = str(ex).capitalize() + '.'
            if err:
                return Response(V.account_page(self.context(req, con), err), status=400)
        finally:
            con.close()
        return Response(status=303, headers={'Location': '/login?m=password'}, cookies=[(COOKIE, '', 0)])

    # ------------------------------------------------------------ pages
    def page(self, req, render):
        con = self.bot.db()
        try:
            return Response(render(self.context(req, con), con))
        finally:
            con.close()

    def overview(self, req):
        def render(ctx, con):
            months = {}
            for ym, count, tots in export.months(con):
                months[ym] = {'count': count, 'totals': tots}
            unpaid = dbm.find_invoices(con, "status = 'filed' AND paid = 0")
            t = today().isoformat()
            data = {'months': months, 'review': ctx['counts']['review'], 'unpaid': len(unpaid),
                    'overdue': sum(1 for i in unpaid if i['due_date'] and i['due_date'] < t),
                    'recent': dbm.find_invoices(con, '1=1', order='id DESC', limit=12),
                    'last_run': dbm.meta_get(con, 'last_run'),
                    'other': con.execute("SELECT count(*) FROM invoices WHERE status IN ('duplicate', 'ignored')").fetchone()[0],
                    'suggestions': len([1 for sc, _, _ in bank.propose(self.bot, con) if sc < bank.AUTO_SCORE])
                    if req.user['role'] == 'admin' else 0}
            return V.overview(ctx, data)
        return self.page(req, render)

    def month(self, req, ym):
        def render(ctx, con):
            invs = dbm.find_invoices(con, "status = 'filed' AND paid = 1 AND payment_date LIKE ?", (ym + '%',))
            expected = dbm.find_invoices(con, "status = 'filed' AND paid = 0 AND payment_date LIKE ?", (ym + '%',))
            if self.bot.cfg['payment'].get('unconfirmed') == 'estimate':
                invs, expected = sorted(invs + expected, key=lambda i: (i['payment_date'], i['id'])), []
            return V.month_page(ctx, ym, invs, expected)
        return self.page(req, render)

    def review(self, req):
        def render(ctx, con):
            invs = dbm.find_invoices(con, "status = 'review'", order='id DESC')
            check = [i for i in dbm.find_invoices(con, "status = 'filed' AND verified = 0", order='id DESC')
                     if any(x['level'] == 'warn' for x in i['issues'] or [])]
            body = (f'<h1>To check</h1><p class="muted">Invoices the bot could not fully read stay here, under their '
                    f'original name, until the missing fields are filled in.</p>'
                    + V.ledger(invs, ctx, cols=('added', 'supplier', 'number', 'amount', 'issues', 'original'), foot=False,
                               empty='Nothing to check. Invoices the bot is unsure about will appear here.'))
            if check:
                body += ('<h2>Filed, but worth a look</h2><p class="muted">Filed with a value the bot was less sure of. '
                         'Open and save one to confirm it.</p>'
                         + V.ledger(check, ctx, cols=('paid_on', 'supplier', 'number', 'amount', 'issues'), foot=False))
            return V.layout(ctx, 'To check', body, '/review')
        return self.page(req, render)

    def unpaid(self, req):
        def render(ctx, con):
            invs = dbm.find_invoices(con, "status = 'filed' AND paid = 0", order='payment_date, id')
            return V.list_page(ctx, 'Waiting for payment',
                               'Received invoices with no confirmed payment, by due date. Once paid (marked here, matched '
                               'from a bank statement, or by a supplier rule) they move into their payment month.',
                               invs, ('due', 'supplier', 'number', 'amount', 'overdue', 'markpaid'), '/unpaid',
                               'Nothing is waiting for payment.')
        return self.page(req, render)

    def other(self, req):
        def render(ctx, con):
            invs = dbm.find_invoices(con, "status IN ('duplicate', 'ignored')", order='id DESC')
            return V.list_page(ctx, 'Other documents', 'Duplicates, proformas (díjbekérő), quotes and files marked as '
                               'not an invoice. Kept, but not part of the monthly archive.', invs,
                               ('added', 'supplier', 'number', 'amount', 'status', 'issues'), '/other',
                               'No other documents.', foot=False)
        return self.page(req, render)

    def search(self, req):
        q = req.query.get('q', '').strip()[:100]

        def render(ctx, con):
            invs = []
            if q:
                like = f'%{q}%'
                where = ('supplier LIKE ? OR supplier_raw LIKE ? OR invoice_number LIKE ? OR original_name LIKE ? '
                         'OR file_path LIKE ?')
                params = [like] * 5
                from .util import parse_amount_input, dec_str
                a = parse_amount_input(q) if re.search(r'\d', q) else None
                if a is not None:
                    where += ' OR amount = ? OR amount = ?'
                    params += [dec_str(a), dec_str(-a)]
                invs = dbm.find_invoices(con, where, params, order='payment_date DESC, id DESC', limit=200)
            return V.list_page(ctx, f'Search: {q}' if q else 'Search', f'{len(invs)} found.' if q else 'Type in the search box.',
                               invs, ('paid_on', 'supplier', 'number', 'amount', 'file'), '', 'No invoices match.', foot=False)
        return self.page(req, render)

    def _invoice(self, con, inv_id):
        inv = dbm.get_invoice(con, int(inv_id))
        if not inv:
            raise HttpError(404, f'There is no invoice #{inv_id}.')
        return inv

    def invoice(self, req, inv_id, error=None):
        def render(ctx, con):
            inv = self._invoice(con, inv_id)
            txn = con.execute('SELECT * FROM bank_txns WHERE id = ?', (inv['bank_txn_id'],)).fetchone() if inv['bank_txn_id'] else None
            return V.invoice_page(ctx, inv, dbm.events(con, inv['id'], 30), dict(txn) if txn else None, error,
                                  fresh=req.query.get('m') == 'paid')
        return self.page(req, render)

    def invoice_file(self, req, inv_id):
        con = self.bot.db()
        try:
            inv = self._invoice(con, inv_id)
            path = (self.bot.archive / inv['file_path']).resolve()
            if self.bot.archive.resolve() not in path.parents or not path.is_file():
                raise HttpError(404, 'The file is missing from the archive.')
            inline = req.query.get('inline') == '1'
            if not inline:
                with con:
                    dbm.log_event(con, 'downloaded', inv['id'], req.user['username'], {'file': inv['file_path']})
        finally:
            con.close()
        ctype = FILE_TYPES.get(path.suffix.lower(), 'application/octet-stream')
        return FileResponse(path, ctype, path.name, inline=inline)

    def invoice_save(self, req, inv_id):
        con = self.bot.db()
        try:
            inv = self._invoice(con, inv_id)
        finally:
            con.close()
        changes = {}
        for f in ('supplier', 'invoice_number', 'amount', 'currency', 'doc_type', 'issue_date', 'fulfilment_date',
                  'due_date', 'payment_method'):
            if f not in req.form:
                continue
            new = req.form_value(f).strip()
            cur = inv.get(f) or ''
            if f == 'amount' and new and cur:
                from .util import parse_amount_input, dec_str
                a = parse_amount_input(new)
                if a is not None and dec_str(a) == cur:
                    continue
            if new != cur:
                changes[f] = new or None
        if 'payment_date' in req.form:
            new = req.form_value('payment_date').strip()
            ov = inv.get('overrides') or {}
            cur = ov.get('payment_date') or (inv.get('payment_date') if inv.get('paid') else '')
            if new and new != cur:
                changes['payment_date'] = new
            elif not new and ov.get('payment_date'):
                changes['payment_date'] = None
        try:
            P.update(self.bot, int(inv_id), changes, actor=req.user['username'], verify=True)
        except (ValueError, KeyError) as ex:
            return self.invoice(req, inv_id, error=str(ex))
        raise Redirect(f'/invoices/{int(inv_id)}?m=saved')

    def invoice_action(self, req, inv_id, action):
        inv_id = int(inv_id)
        actor = req.user['username']
        if action == 'paid':
            P.mark_paid(self.bot, inv_id, req.form_value('date') or None, actor=actor)
        elif action == 'unpaid':
            P.mark_unpaid(self.bot, inv_id, actor=actor)
        elif action == 'reextract':
            P.reextract(self.bot, inv_id, actor=actor)
        elif action == 'ignore':
            P.update(self.bot, inv_id, {'status': 'ignored'}, actor=actor)
        elif action == 'restore':
            P.update(self.bot, inv_id, {'status': None}, actor=actor)
        elif action == 'notdup':
            P.update(self.bot, inv_id, {'not_duplicate': True}, actor=actor)
        elif action == 'unlink':
            with self.bot.files_lock:
                con = self.bot.db()
                try:
                    with con:
                        touched = bank.unlink(self.bot, con, inv_id, actor=actor)
                finally:
                    con.close()
            P._write_summaries(self.bot, touched)
        msg = {'paid': 'paid', 'unpaid': 'unpaid', 'reextract': 'reextracted', 'ignore': 'ignored', 'restore': 'restored',
               'notdup': 'notdup', 'unlink': 'unlinked'}[action]
        back = req.form_value('back')
        if back in ('/unpaid', '/review') and action == 'paid':
            raise Redirect(f'{back}?m=paid')
        raise Redirect(f'/invoices/{inv_id}?m={msg}')

    # ------------------------------------------------------------ downloads
    def download_period(self, req, period, kind):
        con = self.bot.db()
        try:
            with con:
                dbm.log_event(con, 'downloaded', None, req.user['username'], {'period': period, 'kind': kind})
            if kind == 'csv':
                invs = export.select(self.bot, con, period)
                return Response(export.csv_bytes(self.bot, invs), ctype='text/csv; charset=utf-8',
                                headers={'Content-Disposition': _disposition(f'invoices_{period}.csv')})
        finally:
            con.close()
        fd, tmp = tempfile.mkstemp(suffix='.zip', dir=self.bot.exports)
        os.close(fd)
        export.export(self.bot, period, out=tmp)
        return FileResponse(Path(tmp), 'application/zip', f'invoices_{period}.zip', delete=True)

    def download_selection(self, req):
        ids = [int(x) for x in req.form.get('ids', []) if x.isdigit()][:2000]
        if not ids:
            raise Redirect(req.back('m=none'))
        con = self.bot.db()
        try:
            with con:
                dbm.log_event(con, 'downloaded', None, req.user['username'], {'ids': ids})
        finally:
            con.close()
        fd, tmp = tempfile.mkstemp(suffix='.zip', dir=self.bot.exports)
        os.close(fd)
        res = export.export(self.bot, ids=ids, out=tmp)
        return FileResponse(Path(tmp), 'application/zip', res['title'] + '.zip', delete=True)

    # ------------------------------------------------------------ changes
    def upload_form(self, req):
        return self.page(req, lambda ctx, con: V.upload_page(ctx))

    def upload(self, req):
        rep = collect.Report()
        for field, fname, data in req.files:
            if field != 'files' or not data:
                continue
            name = PurePosixPath((fname or 'upload.pdf').replace('\\', '/')).name[:150]
            collect.process_blob(self.bot, data, name, 'upload', {'uploaded_by': req.user['username']}, rep,
                                 require_invoice=False)
        P._write_summaries(self.bot, rep.touched)
        return self.page(req, lambda ctx, con: V.upload_page(ctx, rep))

    def bank_page(self, req):
        def render(ctx, con):
            sugg = []
            for sc, inv, t in bank.propose(self.bot, con):
                if sc < bank.AUTO_SCORE:
                    sugg.append({'invoice_id': inv['id'], 'supplier': inv['supplier'], 'invoice_number': inv['invoice_number'],
                                 'amount': inv['amount'], 'currency': inv['currency'], 'txn_id': t['id'], 'paid_on': t['date'],
                                 'counterparty': t['counterparty'], 'reference': t['description'], 'score': round(sc)})
            recent = [{'invoice_id': r['invoice_id'], 'supplier': r['supplier'], 'invoice_number': r['invoice_number'],
                       'amount': r['amount'], 'currency': r['currency'], 'paid_on': r['date']}
                      for r in con.execute("SELECT t.date, t.invoice_id, i.supplier, i.invoice_number, i.amount, i.currency "
                                           "FROM bank_txns t JOIN invoices i ON i.id = t.invoice_id WHERE t.status = 'matched' "
                                           "ORDER BY t.id DESC LIMIT 15").fetchall()]
            return V.bank_page(ctx, getattr(req, 'bank_result', None), sugg, recent)
        return self.page(req, render)

    def bank_upload(self, req):
        f = next(((fn, data) for field, fn, data in req.files if field == 'statement' and data), None)
        if not f:
            raise Redirect('/bank?m=none')
        try:
            req.bank_result = bank.import_statement(self.bot, f[1], f[0] or 'statement.csv',
                                                    req.form_value('account').strip()[:60] or None,
                                                    actor=req.user['username'])
        except ValueError as ex:
            con = self.bot.db()
            try:
                ctx = self.context(req, con)
                ctx['flash'] = ('error', f'Could not read the statement: {ex}')
                return Response(V.bank_page(ctx), status=400)
            finally:
                con.close()
        return self.bank_page(req)

    def bank_action(self, req, action):
        inv_id, txn_id = int(req.form_value('invoice') or 0), int(req.form_value('txn') or 0)
        with self.bot.files_lock:
            con = self.bot.db()
            touched = set()
            try:
                with con:
                    if action == 'link':
                        touched = bank.link(self.bot, con, inv_id, txn_id, None, actor=req.user['username'])
                    else:
                        bank.reject(self.bot, con, inv_id, txn_id)
            finally:
                con.close()
        P._write_summaries(self.bot, touched)
        raise Redirect(f'/bank?m={"linked" if action == "link" else "rejected"}')

    def collect_now(self, req):
        if not self.collecting.acquire(blocking=False):
            raise Redirect('/?m=busy')

        def work():
            try:
                collect.run(self.bot, actor=req.user['username'])
            except Exception:
                self.bot.log.exception('collection failed')
            finally:
                self.collecting.release()
        threading.Thread(target=work, daemon=True).start()
        raise Redirect('/?m=collecting')

    def suppliers(self, req):
        def render(ctx, con):
            rows = []
            for r in con.execute('SELECT * FROM suppliers WHERE builtin = 0 OR paid_on IS NOT NULL OR name IN '
                                 '(SELECT DISTINCT supplier FROM invoices) ORDER BY name').fetchall():
                d = dict(r)
                for k in ('aliases', 'tax_ids', 'domains'):
                    d[k] = jload(d[k], [])
                rows.append(d)
            return V.suppliers_page(ctx, rows)
        return self.page(req, render)

    def supplier_save(self, req):
        name = req.form_value('name')
        rule = req.form_value('paid_on') or None
        if rule not in (None, 'issue_date', 'due_date', 'fulfilment_date'):
            raise HttpError(400, 'Unknown payment rule.')
        con = self.bot.db()
        try:
            with con:
                if not con.execute('SELECT 1 FROM suppliers WHERE name = ?', (name,)).fetchone():
                    raise HttpError(404, 'Unknown supplier.')
                S.upsert(con, name, paid_on=rule, set_paid_on=True)
                dbm.log_event(con, 'supplier_rule', None, req.user['username'], {'supplier': name, 'paid_on': rule})
        finally:
            con.close()
        P.refile_all(self.bot, 'supplier = ?', (name,))
        raise Redirect('/suppliers?m=supplier')

    def static(self, req, name):
        if name not in STATIC:
            raise HttpError(404, 'Not found.')
        return FileResponse(ASSETS / name, STATIC[name], None, inline=True, cache=True)


# ------------------------------------------------------------------ responses
class Response:
    def __init__(self, body=b'', status=200, ctype='text/html; charset=utf-8', headers=None, cookies=None):
        self.body = body.encode('utf-8') if isinstance(body, str) else body
        self.status, self.ctype = status, ctype
        self.headers = dict(headers or {})
        self.cookies = cookies or []


class FileResponse:
    def __init__(self, path, ctype, download_name, inline=False, delete=False, cache=False):
        self.path, self.ctype, self.name = Path(path), ctype, download_name
        self.inline, self.delete, self.cache = inline, delete, cache
        self.status = 200


def _disposition(name, inline=False):
    ascii_name = re.sub(r'[^A-Za-z0-9._-]+', '_', name) or 'file'
    kind = 'inline' if inline else 'attachment'
    return f"{kind}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(name)}"


class Request:
    def __init__(self, handler, method):
        self.handler = handler
        self.method = method
        parts = urlsplit(handler.path)
        self.raw_path = handler.path if handler.path.startswith('/') else '/'
        self.path = parts.path or '/'
        self.query = {k: v[-1] for k, v in parse_qs(parts.query, keep_blank_values=True).items()}
        jar = cookies.SimpleCookie()
        try:
            jar.load(handler.headers.get('Cookie', ''))
        except cookies.CookieError:
            pass
        self.cookies = {k: m.value for k, m in jar.items()}
        self.form, self.files = {}, []
        self.user, self.csrf = None, None
        xf = handler.headers.get('X-Forwarded-For') if handler.server.trust_proxy else None
        self.client_ip = (xf.split(',')[0].strip() if xf else handler.client_address[0])

    def form_value(self, key):
        v = self.form.get(key)
        return v[-1] if v else ''

    def back(self, extra):
        ref = urlsplit(self.handler.headers.get('Referer', '/'))
        path = ref.path if ref.path.startswith('/') and not ref.path.startswith('//') else '/'
        return path + '?' + extra

    def read_body(self, limit):
        n = int(self.handler.headers.get('Content-Length') or 0)
        if n > limit:
            raise HttpError(413, f'Too large: the limit is {limit // 1048576} MB.')
        data = self.handler.rfile.read(n) if n else b''
        ctype = self.handler.headers.get('Content-Type', '')
        if ctype.startswith('application/x-www-form-urlencoded'):
            self.form = parse_qs(data.decode('utf-8', 'replace'), keep_blank_values=True)
        elif ctype.startswith('multipart/form-data'):
            msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
                b'Content-Type: ' + ctype.encode('latin-1') + b'\r\nMIME-Version: 1.0\r\n\r\n' + data)
            if msg.is_multipart():
                for part in msg.iter_parts():
                    name = part.get_param('name', header='content-disposition')
                    if not name:
                        continue
                    fname = part.get_filename()
                    payload = part.get_payload(decode=True) or b''
                    if fname is not None:
                        self.files.append((name, fname, payload))
                    else:
                        self.form.setdefault(name, []).append(payload.decode('utf-8', 'replace'))


class Handler(BaseHTTPRequestHandler):
    server_version = 'InvoiceBot'
    sys_version = ''
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        self.server.app.bot.log.info('web %s %s', self.address_string(), fmt % args)

    def do_GET(self):
        self.handle_request('GET')

    def do_HEAD(self):
        self.handle_request('GET', head=True)

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method, head=False):
        app = self.server.app
        req = Request(self, method)
        resp = None
        try:
            if not self._host_ok():
                raise HttpError(400, 'Unexpected Host header.')
            if method == 'POST':
                if not self._same_origin():
                    raise HttpError(403, 'Cross-site form submission refused.')
                limit = app.bot.cfg['admin'].get('max_upload_mb', 50) * 1048576
                req.read_body(limit if req.path in ('/upload', '/bank') else 2 * 1048576)
            con = app.bot.db()
            try:
                req.user, req.csrf = auth.session_user(con, req.cookies.get(COOKIE))
            finally:
                con.close()
            resp = app.dispatch(req)
        except Redirect as r:
            resp = Response(status=303, headers={'Location': r.location})
        except HttpError as he:
            if he.status == 413:
                self.close_connection = True  # the unread body cannot be skipped safely
            resp = self._error(app, req, he.status, he.message)
        except Exception:
            app.bot.log.error('web error on %s %s\n%s', method, req.path, traceback.format_exc())
            resp = self._error(app, req, 500, 'Something went wrong. The details are in logs/invoicebot.log.')
        self._send(resp, head)

    def _error(self, app, req, status, message):
        ctx = None
        if req.user:
            con = app.bot.db()
            try:
                ctx = app.context(req, con)
            finally:
                con.close()
        return Response(V.error_page(ctx, status, message), status=status)

    def _host_ok(self):
        allowed = self.server.allowed_hosts
        if not allowed:
            return True
        host = (self.headers.get('Host') or '').lower()
        name = host.rsplit(':', 1)[0] if not host.startswith('[') else host.split(']')[0] + ']'
        return name in allowed

    def _same_origin(self):
        origin = self.headers.get('Origin')
        if not origin or origin == 'null':
            return origin != 'null'
        host = self.headers.get('Host', '')
        if self.server.trust_proxy and self.headers.get('X-Forwarded-Host'):
            host = self.headers['X-Forwarded-Host'].split(',')[0].strip()
        return urlsplit(origin).netloc.lower() == host.lower()

    def _security_headers(self, html_page):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        if html_page:
            self.send_header('Content-Security-Policy', CSP)

    def _cookie_headers(self, resp):
        secure = '; Secure' if self.server.app.bot.cfg['admin'].get('secure_cookies') else ''
        for name, value, max_age in getattr(resp, 'cookies', []):
            self.send_header('Set-Cookie', f'{name}={value}; Path=/; Max-Age={int(max_age)}; HttpOnly; SameSite=Strict{secure}')

    def _send(self, resp, head=False):
        try:
            if isinstance(resp, FileResponse):
                size = resp.path.stat().st_size
                self.send_response(200)
                self.send_header('Content-Type', resp.ctype)
                self.send_header('Content-Length', str(size))
                if resp.name:
                    self.send_header('Content-Disposition', _disposition(resp.name, resp.inline))
                self.send_header('Cache-Control', 'public, max-age=86400' if resp.cache else 'no-store')
                self._security_headers(False)
                self.end_headers()
                if not head:
                    with open(resp.path, 'rb') as f:
                        while True:
                            chunk = f.read(256 * 1024)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                if resp.delete:
                    try:
                        resp.path.unlink()
                    except OSError:
                        pass
                return
            self.send_response(resp.status)
            self.send_header('Content-Type', resp.ctype)
            self.send_header('Content-Length', str(len(resp.body)))
            self.send_header('Cache-Control', 'no-store')
            for k, v in resp.headers.items():
                self.send_header(k, v)
            self._cookie_headers(resp)
            self._security_headers(resp.ctype.startswith('text/html'))
            self.end_headers()
            if not head:
                self.wfile.write(resp.body)
        except (BrokenPipeError, ConnectionResetError):
            pass


def make_server(bot, host='127.0.0.1', port=8765):
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    srv.app = App(bot)
    srv.trust_proxy = bool(bot.cfg['admin'].get('trust_proxy'))
    allowed = [h.lower() for h in bot.cfg['admin'].get('allowed_hosts') or []]
    if not allowed and host in ('127.0.0.1', 'localhost', '::1'):
        allowed = ['127.0.0.1', 'localhost', '[::1]']  # blocks DNS-rebinding against the local panel
    srv.allowed_hosts = set(allowed)
    return srv


def serve(bot, host='127.0.0.1', port=8765, collect_every=0):
    srv = make_server(bot, host, port)
    if collect_every and collect_every > 0:
        def loop():
            while True:
                try:
                    rep = collect.run(bot, actor='scheduler')
                    if rep:
                        bot.log.info('scheduled collection: %s', rep.counts())
                except Exception:
                    bot.log.exception('scheduled collection failed')
                time.sleep(collect_every * 60)
        threading.Thread(target=loop, daemon=True, name='collector').start()
    url = f'http://{"127.0.0.1" if host in ("0.0.0.0", "") else host}:{port}'
    print(f'Invoice Bot admin panel: {url}   (Ctrl+C to stop)'
          + (f'\nCollecting new invoices every {collect_every} minutes.' if collect_every else ''))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
