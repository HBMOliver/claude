"""The admin panel over real HTTP: login, roles, CSRF, edits, uploads, downloads, guards."""
import http.client
import http.cookiejar
import io
import re
import socket
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

from helpers import BotTestCase
from invoicebot import auth, collect, samples, web
from invoicebot.web import Throttle, safe_local_path
from test_pipeline import TRANSFER_INVOICE, drop


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


class Client:
    def __init__(self, base):
        self.base = base
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), NoRedirect)

    def req(self, path, data=None, headers=None, files=None):
        headers = dict(headers or {})
        body = None
        if files is not None:
            boundary = uuid.uuid4().hex
            parts = []
            for k, v in (data or {}).items():
                parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
            for field, (fname, content) in files:
                parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{fname}"\r\n'
                             f'Content-Type: application/octet-stream\r\n\r\n'.encode() + content + b'\r\n')
            body = b''.join(parts) + f'--{boundary}--\r\n'.encode()
            headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        elif data is not None:
            body = urllib.parse.urlencode(data, doseq=True).encode()
        r = urllib.request.Request(self.base + path, data=body, headers=headers)
        try:
            resp = self.op.open(r, timeout=20)
            return resp.status, resp.headers, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read()

    def login(self, user, pw):
        st, h, body = self.req('/login')
        tok = re.search(rb'name="login_token" value="([^"]+)"', body).group(1).decode()
        return self.req('/login', {'login_token': tok, 'username': user, 'password': pw})

    def csrf(self, path='/'):
        st, h, body = self.req(path)
        return re.search(rb'name="csrf" value="([^"]+)"', body).group(1).decode()


class TestWeb(BotTestCase):
    def setUp(self):
        super().setUp()
        for name, data in samples.demo_files():
            drop(self.bot, name, data)
        drop(self.bot, 'tr.pdf', TRANSFER_INVOICE)
        collect.run(self.bot, imap=False)
        con = self.con()
        try:
            with con:
                auth.add_user(con, 'admin', 'correct-horse-battery')
                auth.add_user(con, 'konyvelo', 'accountant-pass-1', role='viewer')
        finally:
            con.close()
        self.srv = web.make_server(self.bot, '127.0.0.1', 0)
        self.base = f'http://127.0.0.1:{self.srv.server_address[1]}'
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.th.start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        super().tearDown()

    def admin(self):
        c = Client(self.base)
        st, h, _ = c.login('admin', 'correct-horse-battery')
        self.assertEqual((st, h['Location']), (303, '/'))
        return c

    def find_id(self, name_part):
        con = self.con()
        try:
            return con.execute('SELECT id FROM invoices WHERE original_name LIKE ?', (f'%{name_part}%',)).fetchone()['id']
        finally:
            con.close()

    def test_pages_render(self):
        c = self.admin()
        for p in ['/', '/months/2026-09', '/review', '/unpaid', '/other', '/search?q=Kov', '/search?q=127%20000',
                  f'/invoices/{self.find_id("fotomuhely")}', '/suppliers', '/bank', '/upload', '/account']:
            st, h, body = c.req(p)
            self.assertEqual(st, 200, p)
            self.assertIn("default-src 'self'", h['Content-Security-Policy'])
            self.assertEqual(h['Cache-Control'], 'no-store')
            self.assertNotIn(b'style="', body, p)  # CSP forbids inline styles
        st, h, body = c.req('/search?q=127%20000')
        self.assertIn(b'Kov', body)

    def test_login_required_and_wrong_password(self):
        c = Client(self.base)
        st, h, _ = c.req('/months/2026-09')
        self.assertEqual((st, h['Location']), (303, '/login?next=%2Fmonths%2F2026-09'))
        st, h, _ = c.login('admin', 'nope-nope-nope')
        self.assertEqual(st, 401)
        st, h, _ = c.login('nobody', 'nope-nope-nope')
        self.assertEqual(st, 401)

    def test_login_throttle(self):
        c = Client(self.base)
        for _ in range(8):
            c.login('admin', 'wrong-password-x')
        st, h, _ = c.login('admin', 'correct-horse-battery')
        self.assertEqual(st, 429)

    def test_login_needs_its_form_token(self):
        c = Client(self.base)
        st, h, _ = c.req('/login', {'login_token': 'forged', 'username': 'admin', 'password': 'correct-horse-battery'})
        self.assertEqual(st, 400)

    def test_csrf_and_cross_origin(self):
        c = self.admin()
        inv = self.find_id('tr.pdf')
        st, h, _ = c.req(f'/invoices/{inv}/paid', {'date': '2026-10-30'})
        self.assertIn('badcsrf', h['Location'])
        self.assertEqual(self.inv(inv)['paid'], 0)
        tok = c.csrf()
        st, h, _ = c.req(f'/invoices/{inv}/paid', {'csrf': tok, 'date': '2026-10-30'},
                         headers={'Origin': 'http://evil.example'})
        self.assertEqual(st, 403)
        st, h, _ = c.req(f'/invoices/{inv}/paid', {'csrf': tok, 'date': '2026-10-30', 'back': '/unpaid'})
        self.assertEqual(h['Location'], '/unpaid?m=paid')
        self.assertEqual(self.inv(inv)['file_path'], '2026/2026-10/2026-10-30_Tervezo-Studio_TR-2026-7.pdf')

    def test_edit_invoice(self):
        c = self.admin()
        inv = self.find_id('brightline')
        tok = c.csrf(f'/invoices/{inv}')
        st, h, body = c.req(f'/invoices/{inv}', {'csrf': tok, 'invoice_number': 'BL-77', 'due_date': 'not a date'})
        self.assertEqual(st, 400)
        self.assertIn(b'not a date', body)
        st, h, _ = c.req(f'/invoices/{inv}', {'csrf': tok, 'invoice_number': 'BL-77', 'supplier': 'Brightline',
                                              'payment_method': 'card'})
        self.assertEqual(h['Location'], f'/invoices/{inv}?m=saved')
        row = self.inv(inv)
        self.assertEqual((row['status'], row['paid']), ('filed', 1))
        self.assertTrue(row['file_path'].endswith('_Brightline_BL-77.pdf'))
        self.assertEqual(row['verified'], 1)

    def test_viewer_is_read_only(self):
        c = Client(self.base)
        c.login('konyvelo', 'accountant-pass-1')
        st, _, body = c.req('/months/2026-09')
        self.assertEqual(st, 200)
        self.assertNotIn(b'href="/upload"', body)
        tok = c.csrf()
        inv = self.find_id('tr.pdf')
        st, _, _ = c.req(f'/invoices/{inv}/paid', {'csrf': tok})
        self.assertEqual(st, 403)
        st, _, _ = c.req('/upload')
        self.assertEqual(st, 403)
        st, h, body = c.req('/download/2026-09.zip')
        self.assertEqual(st, 200)
        self.assertEqual(h['Content-Type'], 'application/zip')
        tok = c.csrf('/months/2026-09')
        st, h, body = c.req('/download/selection', {'csrf': tok, 'ids': [str(self.find_id('fotomuhely'))]})
        self.assertEqual(st, 200)
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            self.assertTrue(any(n.endswith('_Foto-Muhely_FM-2026-0042.pdf') for n in z.namelist()))

    def test_downloads(self):
        c = self.admin()
        inv = self.find_id('fotomuhely')
        st, h, body = c.req(f'/invoices/{inv}/file')
        self.assertEqual((st, h['Content-Type']), (200, 'application/pdf'))
        self.assertIn('attachment; filename="2026-09-20_Foto-Muhely_FM-2026-0042.pdf"', h['Content-Disposition'])
        self.assertTrue(body.startswith(b'%PDF'))
        st, h, body = c.req(f'/invoices/{inv}/file?inline=1')
        self.assertTrue(h['Content-Disposition'].startswith('inline'))
        st, h, body = c.req('/download/2026-09.csv')
        self.assertEqual(st, 200)
        self.assertIn('Fot'.encode(), body)
        st, h, body = c.req('/download/2026.zip')
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            self.assertIn('invoices_2026/summary.csv', z.namelist())
        self.assertEqual(list(self.bot.exports.glob('*.zip')), [])  # temporary ZIPs are removed
        con = self.con()
        try:
            n = con.execute("SELECT count(*) FROM events WHERE action = 'downloaded' AND actor = 'admin'").fetchone()[0]
        finally:
            con.close()
        self.assertEqual(n, 3)

    def test_upload_and_bank(self):
        c = self.admin()
        tok = c.csrf('/upload')
        st, h, body = c.req('/upload', {'csrf': tok}, files=[('files', ('../../evil name.pdf', TRANSFER_INVOICE.replace(b'TR-2026-7', b'TR-2026-8')))])
        self.assertEqual(st, 200)
        self.assertIn(b'TR-2026-8', body)
        con = self.con()
        try:
            names = [r['original_name'] for r in con.execute('SELECT original_name FROM invoices')]
        finally:
            con.close()
        self.assertIn('evil name.pdf', names)
        tok = c.csrf('/bank')
        csv = ('Könyvelés dátuma;Összeg;Devizanem;Partner neve;Közlemény\r\n'
               '2026.10.21.;-381 000;HUF;TERVEZŐ STÚDIÓ KFT;TR-2026-7\r\n').encode('cp1250')
        st, h, body = c.req('/bank', {'csrf': tok, 'account': 'OTP'}, files=[('statement', ('otp.csv', csv))])
        self.assertEqual(st, 200)
        self.assertIn(b'1 invoices confirmed as paid', body)
        self.assertEqual(self.inv(self.find_id('tr.pdf'))['payment_source'], 'bank')

    def test_guards(self):
        c = self.admin()
        st, _, _ = c.req('/', headers={'Host': 'evil.example'})
        self.assertEqual(st, 400)
        for p in ['/static/../invoicebot.db', '/static/app.css/../../invoicebot.json', '/invoices/999999',
                  '/invoices/1/file/../../x', '/download/../../x.zip', '/months/2026-13x']:
            st, _, _ = c.req(p)
            self.assertIn(st, (404, 400), p)
        st, _, _ = c.req('/', data=None)
        st, _, _ = c.req('/login', headers={'X-Forwarded-For': '1.2.3.4'})
        self.assertEqual(st, 200)

    def test_password_change_logs_out(self):
        c = self.admin()
        tok = c.csrf('/account')
        st, _, _ = c.req('/account', {'csrf': tok, 'current': 'wrong', 'new': 'x' * 12, 'again': 'x' * 12})
        self.assertEqual(st, 400)
        st, h, _ = c.req('/account', {'csrf': tok, 'current': 'correct-horse-battery', 'new': 'brand-new-pass-1',
                                      'again': 'brand-new-pass-1'})
        self.assertEqual(h['Location'], '/login?m=password')
        st, h, _ = c.req('/')
        self.assertEqual(st, 303)
        st, h, _ = Client(self.base).login('admin', 'brand-new-pass-1')
        self.assertEqual(st, 303)

    def raw(self, data):
        """Send raw bytes on a fresh connection; return everything the server answers."""
        s = socket.create_connection(('127.0.0.1', self.srv.server_address[1]), timeout=10)
        try:
            s.sendall(data)
            chunks = []
            while True:
                try:
                    b = s.recv(65536)
                except (ConnectionResetError, socket.timeout):
                    break
                if not b:
                    break
                chunks.append(b)
            return b''.join(chunks)
        finally:
            s.close()

    def test_redirect_after_login_stays_local(self):
        for nxt in ['/\\evil.example/phish', '/\t/evil.example', '//evil.example', 'https://evil.example',
                    '/\r\nSet-Cookie: injected=1\r\nX-Injected: yes']:
            c = Client(self.base)
            st, h, body = c.req('/login?' + urllib.parse.urlencode({'next': nxt}))
            tok = re.search(rb'name="login_token" value="([^"]+)"', body).group(1).decode()
            st, h, _ = c.req('/login', {'login_token': tok, 'username': 'admin', 'password': 'correct-horse-battery',
                                        'next': nxt})
            self.assertEqual((st, h['Location']), (303, '/'), nxt)
            self.assertIsNone(h.get('X-Injected'))
        self.assertEqual(safe_local_path('/months/2026-09?m=saved'), '/months/2026-09?m=saved')

    def test_bodies_are_not_read_without_a_login(self):
        port = self.srv.server_address[1]
        head = (f'POST /upload HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: multipart/form-data; '
                f'boundary=x\r\nContent-Length: 50000000\r\n\r\n').encode()
        out = self.raw(head + b'x' * 1000)
        self.assertIn(b'303 See Other', out)
        self.assertIn(b'Location: /login?m=expired', out)
        self.assertIn(b'Connection: close', out)
        out = self.raw(f'POST /login HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Length: -1\r\n\r\n'.encode())
        self.assertIn(b'400 Bad Request', out)
        out = self.raw(f'POST /login HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nTransfer-Encoding: chunked\r\n\r\n'.encode())
        self.assertIn(b'400 Bad Request', out)

    def test_unread_body_closes_the_connection(self):
        port = self.srv.server_address[1]
        smuggled = f'GET /static/app.js HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n\r\n'.encode()
        out = self.raw(f'GET /login HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Length: {len(smuggled)}\r\n\r\n'
                       .encode() + smuggled)
        self.assertEqual(out.count(b'HTTP/1.1 '), 1)

    def test_throttle_semantics(self):
        t = Throttle(ip_limit=3, user_limit=5, window=60)
        tokens = [t.begin('1.1.1.1', 'admin') for _ in range(3)]
        self.assertTrue(all(tokens))
        self.assertIsNone(t.begin('1.1.1.1', 'viewer'))  # the address is spent
        t.succeeded(tokens[0])  # a right password frees only its own attempt
        self.assertIsNotNone(t.begin('1.1.1.1', 'viewer'))
        self.assertIsNone(t.begin('1.1.1.1', 'admin'))
        for ip in ('2.2.2.2', '3.3.3.3', '4.4.4.4'):  # spreading guesses over addresses still hits the user limit
            self.assertIsNotNone(t.begin(ip, 'admin'))
        self.assertIsNone(t.begin('5.5.5.5', 'admin'))

    def test_bad_input_is_a_4xx(self):
        c = self.admin()
        tok = c.csrf()
        for path, data, want in [('/months/2026-13', None, 404), ('/months/2026-00', None, 404),
                                 ('/download/2026-13.zip', None, 404),
                                 (f'/invoices/{self.find_id("tr.pdf")}/paid', {'csrf': tok, 'date': '31/02/2026'}, 400),
                                 ('/bank/link', {'csrf': tok, 'invoice': 'abc', 'txn': '1'}, 400),
                                 ('/bank/link', {'csrf': tok, 'invoice': '999', 'txn': '999'}, 404)]:
            st, _, _ = c.req(path, data)
            self.assertEqual(st, want, path)
        st, h, _ = c.req('/download/selection', {'csrf': tok, 'ids': ['\u00b2']})
        self.assertEqual(st, 303)
        st, h, _ = c.req(f'/invoices/{self.find_id("tr.pdf")}', {'csrf': '\u00e9\u00e9', 'supplier': 'x'})
        self.assertIn('badcsrf', h['Location'])

    def test_logins_are_counted_before_checking(self):
        import concurrent.futures
        c = Client(self.base)
        st, h, body = c.req('/login')
        tok = re.search(rb'name="login_token" value="([^"]+)"', body).group(1).decode()

        def guess(_):
            cc = Client(self.base)
            cc.jar.set_cookie(http.cookiejar.Cookie(0, 'ib_login', tok, None, False, '127.0.0.1', False, False, '/',
                                                    True, False, None, True, None, None, {}))
            return cc.req('/login', {'login_token': tok, 'username': 'admin', 'password': 'wrong-guess-123'})[0]
        with concurrent.futures.ThreadPoolExecutor(20) as ex:
            statuses = list(ex.map(guess, range(20)))
        self.assertLessEqual(statuses.count(401), 8)
        self.assertGreaterEqual(statuses.count(429), 12)

    def test_logout(self):
        c = self.admin()
        tok = c.csrf()
        c.req('/logout', {'csrf': tok})
        st, h, _ = c.req('/')
        self.assertEqual(st, 303)


if __name__ == '__main__':
    unittest.main()
