"""The admin panel over real HTTP: login, roles, CSRF, edits, uploads, downloads, guards."""
import http.cookiejar
import io
import re
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

from helpers import BotTestCase
from invoicebot import auth, collect, samples, web
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
        self.assertEqual(st, 200)
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

    def test_logout(self):
        c = self.admin()
        tok = c.csrf()
        c.req('/logout', {'csrf': tok})
        st, h, _ = c.req('/')
        self.assertEqual(st, 303)


if __name__ == '__main__':
    unittest.main()
