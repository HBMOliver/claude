"""Collect -> identify -> name -> file by payment month, and every way an invoice moves afterwards."""
import email.message
import io
import os
import unittest
import zipfile

from helpers import BotTestCase, dbm
from invoicebot import collect, export, pipeline as P, samples
from invoicebot.pdfwriter import PdfDoc


def demo(name):
    return dict(samples.demo_files())[name]


def drop(bot, name, data):
    p = bot.inbox / name
    p.write_bytes(data)
    os.utime(p, (0, 0))  # older than the "still being written" guard
    return p


def simple_pdf(lines):
    d = PdfDoc()
    p = d.page()
    for i, (x, text) in enumerate(lines):
        p.text(x, 60 + 14 * i, text, size=10)
    return d.to_bytes()


TRANSFER_INVOICE = simple_pdf([
    (50, 'SZÁMLA'), (350, 'Számla sorszáma: TR-2026-7'),
    (50, 'Eladó'), (300, 'Vevő'),
    (50, 'Tervező Stúdió Kft.'), (300, 'Minta Ügynökség Kft.'),
    (50, 'Adószám: 99887766-2-13'), (300, 'Adószám: 11223344-2-41'),
    (50, 'Számla kelte: 2026.10.05.   Fizetési határidő: 2026.10.20.   Fizetési mód: Átutalás'),
    (50, 'Fizetendő: 381 000 Ft'),
])


class TestCollectAndFile(BotTestCase):
    def run_inbox(self):
        rep = collect.run(self.bot, imap=False)
        self.assertIsNotNone(rep)
        self.assertEqual(rep.errors, [])
        return rep

    def test_demo_month(self):
        for name, data in samples.demo_files():
            drop(self.bot, name, data)
        rep = self.run_inbox()
        c = rep.counts()
        self.assertEqual(c['new'], 7)
        files = self.files()
        # paid by card on its date; receipt with its paid date; direct debit on its due date
        self.assertIn('2026/2026-09/2026-09-20_Foto-Muhely_FM-2026-0042.pdf', files)
        self.assertIn('2026/2026-09/2026-09-15_Pixelcraft_ABCD1234-0004.pdf', files)
        self.assertIn('2026/2026-10/2026-10-18_Fovarosi-Aramszolgaltato_AR-2026-0991234.pdf', files)
        # transfers wait for payment, named with the due date
        self.assertIn('_unpaid/2026-09-23_Kovacs-es-Tarsa_E-KVT-2026-118.pdf', files)
        self.assertIn('_unpaid/2026-10-15_Serverwerk-Hosting_R0012345678.pdf', files)
        # proforma kept apart; the one without a number waits for review
        self.assertTrue(any(f.startswith('_other/') and 'dijbekero' in f for f in files))
        self.assertTrue(any(f.startswith('_review/') and 'brightline' in f for f in files))
        self.assertEqual(list(self.bot.inbox.iterdir()), [])
        # month summaries
        summary = (self.bot.archive / '2026/2026-09/_summary.csv').read_text(encoding='utf-8-sig')
        self.assertIn('Pixelcraft', summary)
        self.assertIn('Foto' if 'Foto' in summary else 'Fotó', summary)

    def test_same_file_twice(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        self.run_inbox()
        drop(self.bot, 'copy.pdf', TRANSFER_INVOICE)
        rep = self.run_inbox()
        self.assertEqual(rep.counts()['already_known'], 1)
        self.assertEqual(len(self.files()), 1)

    def test_resent_invoice_is_duplicate(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        self.run_inbox()
        drop(self.bot, 'b.pdf', TRANSFER_INVOICE.replace(b'invoicebot', b'invoicebox'))  # same invoice, other bytes
        rep = self.run_inbox()
        new = [i for i in rep.items if i['result'] == 'new'][0]
        self.assertEqual(new['status'], 'duplicate')
        self.assertTrue(new['file_path'].startswith('_duplicates/'))
        inv = P.update(self.bot, new['id'], {'not_duplicate': True})
        self.assertEqual(inv['status'], 'filed')

    def test_mark_paid_moves_and_renames(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        rep = self.run_inbox()
        inv_id = rep.items[0]['id']
        self.assertEqual(self.inv(inv_id)['file_path'], '_unpaid/2026-10-20_Tervezo-Studio_TR-2026-7.pdf')
        inv = P.mark_paid(self.bot, inv_id, '2026-11-02')
        self.assertEqual(inv['file_path'], '2026/2026-11/2026-11-02_Tervezo-Studio_TR-2026-7.pdf')
        self.assertTrue((self.bot.archive / inv['file_path']).is_file())
        self.assertEqual((inv['payment_source'], inv['paid']), ('manual', 1))
        inv = P.mark_unpaid(self.bot, inv_id)
        self.assertEqual(inv['file_path'], '_unpaid/2026-10-20_Tervezo-Studio_TR-2026-7.pdf')
        self.assertFalse((self.bot.archive / '2026/2026-11').exists())  # empty month folder removed

    def test_review_until_complete_then_learn_supplier(self):
        drop(self.bot, 'brightline.pdf', demo('brightline.pdf'))
        rep = self.run_inbox()
        inv_id = rep.items[0]['id']
        self.assertEqual(self.inv(inv_id)['status'], 'review')
        inv = P.update(self.bot, inv_id, {'invoice_number': 'BL-2026-77', 'supplier': 'Brightline'})
        self.assertEqual(inv['status'], 'filed')
        self.assertTrue(inv['file_path'].endswith('_Brightline_BL-2026-77.pdf'))
        con = self.con()
        try:
            row = con.execute("SELECT aliases FROM suppliers WHERE name = 'Brightline'").fetchone()
        finally:
            con.close()
        self.assertIn('Brightline Studio Ltd', row['aliases'])
        # the next invoice printed under that name is filed as "Brightline" without help
        drop(self.bot, 'next.pdf', simple_pdf([(50, 'Brightline Studio Ltd'), (50, 'INVOICE  No. BL-2026-80'),
                                               (50, 'Date: 2026-10-10'), (50, 'Bill To:'), (50, 'Minta Ügynökség Kft.'),
                                               (50, 'Paid by card'), (50, 'Total £120.00')]))
        rep = self.run_inbox()
        self.assertEqual(rep.items[0]['supplier'], 'Brightline')

    def test_update_validation(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        with self.assertRaises(ValueError):
            P.update(self.bot, inv_id, {'due_date': 'tomorrow-ish'})
        with self.assertRaises(ValueError):
            P.update(self.bot, inv_id, {'currency': 'euro'})
        inv = P.update(self.bot, inv_id, {'amount': '1.234,50', 'currency': 'eur'})
        self.assertEqual((inv['amount'], inv['currency']), ('1234.50', 'EUR'))
        inv = P.update(self.bot, inv_id, {'amount': None})  # back to what was read
        self.assertEqual(inv['amount'], '381000.00')

    def test_supplier_rule_confirms_payment(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        con = self.con()
        try:
            with con:
                from invoicebot import suppliers
                suppliers.upsert(con, 'Tervező Stúdió', paid_on='due_date', set_paid_on=True)
        finally:
            con.close()
        P.refile_all(self.bot)
        inv = self.inv(inv_id)
        self.assertEqual((inv['paid'], inv['payment_source']), (1, 'supplier_rule'))
        self.assertEqual(inv['file_path'], '2026/2026-10/2026-10-20_Tervezo-Studio_TR-2026-7.pdf')

    def test_ignore_and_restore(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        inv = P.update(self.bot, inv_id, {'status': 'ignored'})
        self.assertTrue(inv['file_path'].startswith('_other/'))
        inv = P.update(self.bot, inv_id, {'status': None})
        self.assertTrue(inv['file_path'].startswith('_unpaid/'))

    def test_reextract_keeps_overrides(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        P.update(self.bot, inv_id, {'supplier': 'Tervező'})
        inv = P.reextract(self.bot, inv_id)
        self.assertEqual(inv['supplier'], 'Tervező')

    def test_name_collision(self):
        a = simple_pdf([(50, 'SZÁMLA  Számlaszám: 1'), (50, 'Eladó: Alfa Kft.'), (50, 'Vevő: Minta Ügynökség Kft.'),
                        (50, 'Számla kelte: 2026.10.01.'), (50, 'Fizetési mód: készpénz'), (50, 'Fizetendő: 1 000 Ft')])
        b = a.replace(b'1 000 Ft', b'2 000 Ft')
        drop(self.bot, 'a.pdf', a)
        drop(self.bot, 'b.pdf', b)
        rep = self.run_inbox()
        paths = sorted(i['file_path'] for i in rep.items if i['result'] == 'new')
        # same supplier and number: the second is treated as a duplicate, so no name clash in the month
        self.assertTrue(any(p.startswith('_duplicates/') for p in paths))
        self.assertIn('2026/2026-10/2026-10-01_Alfa_1.pdf', paths)

    def test_estimate_policy(self):
        self.bot.set_option('payment.unconfirmed', 'estimate')
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        inv = self.inv(inv_id)
        self.assertEqual(inv['paid'], 0)
        self.assertEqual(inv['file_path'], '2026/2026-10/2026-10-20_Tervezo-Studio_TR-2026-7.pdf')

    def test_eml_and_zip_in_inbox(self):
        msg = email.message.EmailMessage()
        msg['From'] = 'Tervező Stúdió <szamla@tervezo.hu>'
        msg['To'] = 'szamla@minta-ugynokseg.hu'
        msg['Subject'] = 'Számla TR-2026-7'
        msg.set_content('Csatolva a számla.')
        msg.add_attachment(TRANSFER_INVOICE, maintype='application', subtype='pdf', filename='szamla.pdf')
        msg.add_attachment(b'\x89PNG\r\n\x1a\n' + b'0' * 100, maintype='image', subtype='png', filename='logo.png')
        drop(self.bot, 'mail.eml', msg.as_bytes())
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('invoices/../evil/../fotomuhely.pdf', demo('fotomuhely.pdf'))
            z.writestr('readme.txt', 'hello')
        drop(self.bot, 'batch.zip', buf.getvalue())
        drop(self.bot, 'notes.txt', b'just notes')
        rep = self.run_inbox()
        new = [i for i in rep.items if i['result'] == 'new']
        self.assertEqual(len(new), 2)  # the logo is ignored
        inv = self.inv([i for i in new if i['original_name'] == 'szamla.pdf'][0]['id'])
        self.assertEqual(inv['source_detail']['sender'], 'Tervező Stúdió <szamla@tervezo.hu>')
        self.assertTrue((self.bot.inbox / '_not_processed' / 'notes.txt').exists())
        self.assertFalse((self.bot.inbox / 'mail.eml').exists())
        self.assertFalse(any('evil' in f for f in self.files()))

    def test_export_zip(self):
        for name, data in samples.demo_files():
            drop(self.bot, name, data)
        self.run_inbox()
        res = export.export(self.bot, '2026-09')
        with zipfile.ZipFile(res['path']) as z:
            names = sorted(z.namelist())
        self.assertIn('invoices_2026-09/summary.csv', names)
        self.assertIn('invoices_2026-09/2026-09-15_Pixelcraft_ABCD1234-0004.pdf', names)
        self.assertEqual(res['count'], 2)  # the transfer invoice is not paid yet
        res = export.export(self.bot, '2026')
        with zipfile.ZipFile(res['path']) as z:
            self.assertIn('invoices_2026/2026-10/2026-10-18_Fovarosi-Aramszolgaltato_AR-2026-0991234.pdf', z.namelist())

    def test_verify_detects_hand_moves(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        path = self.bot.archive / self.inv(inv_id)['file_path']
        path.rename(self.bot.archive / 'moved.pdf')
        con = self.con()
        try:
            missing = [r for r in con.execute('SELECT file_path FROM invoices')
                       if not (self.bot.archive / r['file_path']).exists()]
        finally:
            con.close()
        self.assertEqual(len(missing), 1)


class TestSafety(BotTestCase):
    """Regression tests for the review findings: files are never lost, collections never get stuck."""

    def run_inbox(self):
        rep = collect.run(self.bot, imap=False)
        self.assertIsNotNone(rep)
        return rep

    def zip_bytes(self, members, compression=zipfile.ZIP_DEFLATED):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', compression=compression) as z:
            for name, data in members:
                z.writestr(name, data)
        return buf.getvalue()

    def test_stored_zip_is_not_taken_for_a_pdf(self):
        second = TRANSFER_INVOICE.replace(b'TR-2026-7', b'TR-2026-8')
        drop(self.bot, 'two.zip', self.zip_bytes([('a.pdf', TRANSFER_INVOICE), ('b.pdf', second)], zipfile.ZIP_STORED))
        rep = self.run_inbox()
        self.assertEqual(sorted(i['invoice_number'] for i in rep.items if i['result'] == 'new'), ['TR-2026-7', 'TR-2026-8'])
        self.assertEqual(list(self.bot.inbox.iterdir()), [])  # fully imported: removed

    def test_partly_imported_container_is_kept(self):
        drop(self.bot, 'mixed.zip', self.zip_bytes([('a.pdf', TRANSFER_INVOICE), ('notes.xlsx', b'PK-not-a-pdf')]))
        rep = self.run_inbox()
        self.assertEqual(rep.counts()['new'], 1)
        self.assertTrue((self.bot.inbox / '_not_processed' / 'mixed.zip').exists())

    def test_unreadable_zip_does_not_stop_the_run(self):
        good = self.zip_bytes([('a.pdf', TRANSFER_INVOICE)], zipfile.ZIP_STORED)
        bad = bytearray(good)
        i = bad.index(b'%PDF') + 200
        bad[i:i + 4] = b'XXXX'  # the CRC no longer matches
        drop(self.bot, 'a_broken.zip', bytes(bad))
        drop(self.bot, 'b_next.pdf', TRANSFER_INVOICE.replace(b'TR-2026-7', b'TR-2026-9'))
        rep = self.run_inbox()
        self.assertEqual(rep.errors, [])
        self.assertEqual([i['invoice_number'] for i in rep.items if i['result'] == 'new'], ['TR-2026-9'])
        self.assertTrue((self.bot.inbox / '_not_processed' / 'a_broken.zip').exists())

    def test_zip_inside_zip_is_not_opened(self):
        inner = self.zip_bytes([('a.pdf', TRANSFER_INVOICE)])
        drop(self.bot, 'outer.zip', self.zip_bytes([('inner.zip', inner)]))
        rep = self.run_inbox()
        self.assertEqual(rep.counts()['new'], 0)
        self.assertTrue((self.bot.inbox / '_not_processed' / 'outer.zip').exists())

    def test_not_processed_never_overwrites(self):
        for month in ('07', '08', '09'):
            d = self.bot.inbox / f'2026-{month}'
            d.mkdir()
            drop(self.bot, f'2026-{month}/statement.xlsx', f'not an invoice {month}'.encode())
        self.run_inbox()
        kept = sorted(p.read_text() for p in (self.bot.inbox / '_not_processed').iterdir())
        self.assertEqual(kept, ['not an invoice 07', 'not an invoice 08', 'not an invoice 09'])

    def test_failed_move_is_undone_and_nothing_is_orphaned(self):
        for name, data in samples.demo_files():
            drop(self.bot, name, data)
        self.run_inbox()
        real, calls = P.shutil.move, [0]

        def flaky(src, dst):
            calls[0] += 1
            if calls[0] == 3:
                raise PermissionError(13, 'in use by another program', src)
            return real(src, dst)
        P.shutil.move = flaky
        try:
            self.bot.set_option('naming.pattern', '{date}_{supplier}_{number}_{currency}')
            done, errors = P.refile_all(self.bot)
        finally:
            P.shutil.move = real
        self.assertEqual(len(errors), 1)
        self.assertEqual(P.find_problems(self.bot), [])  # ledger and archive still agree
        adopted, done, errors = P.repair(self.bot)
        self.assertEqual(errors, [])
        self.assertEqual(P.find_problems(self.bot), [])
        self.assertTrue(all(f.endswith(('HUF.pdf', 'EUR.pdf', 'USD.pdf', 'GBP.pdf')) or f.startswith(('_review', '_other'))
                            for f in self.files()))

    def test_repair_finds_a_file_moved_by_hand(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        path = self.bot.archive / self.inv(inv_id)['file_path']
        (self.bot.archive / 'somewhere').mkdir()
        path.rename(self.bot.archive / 'somewhere' / 'renamed.pdf')
        self.assertEqual([k for k, _, _ in P.find_problems(self.bot)], ['missing', 'stray'])
        adopted, done, errors = P.repair(self.bot)
        self.assertEqual(adopted, 1)
        self.assertEqual(P.find_problems(self.bot), [])
        self.assertTrue((self.bot.archive / self.inv(inv_id)['file_path']).is_file())

    def test_unrelated_supplier_correction_teaches_nothing(self):
        drop(self.bot, 'a.pdf', TRANSFER_INVOICE)
        inv_id = self.run_inbox().items[0]['id']
        P.update(self.bot, inv_id, {'supplier': 'Delta Facility'})
        con = self.con()
        try:
            row = con.execute("SELECT aliases, tax_ids FROM suppliers WHERE name = 'Delta Facility'").fetchone()
        finally:
            con.close()
        self.assertEqual((row['aliases'], row['tax_ids']), ('[]', '[]'))

    def test_folder_settings_cannot_leave_the_archive(self):
        for key, value in (('folders.unpaid', ''), ('folders.layout', '{yyyy}/../../x'), ('folders.review', '/etc'),
                           ('naming.pattern', '{supplier}/{number}'), ('naming.space', '_')):
            with self.assertRaises(ValueError, msg=key):
                self.bot.set_option(key, value)
        import json
        cfg = json.loads(self.bot.config_path.read_text())
        cfg.setdefault('folders', {})['other'] = '../outside'
        self.bot.config_path.write_text(json.dumps(cfg))
        from invoicebot.config import Bot
        with self.assertRaises(ValueError):
            Bot(self.bot.home)

    def test_csv_cells_never_become_formulas(self):
        from invoicebot import export
        out = export.csv_bytes(self.bot, [{'supplier': '=HYPERLINK("//evil/x","y")', 'amount': '-100.00',
                                           'invoice_number': '+1', 'currency': 'HUF', 'file_path': 'a/b.pdf'}])
        text = out.decode('utf-8-sig')
        self.assertIn('"\'=HYPERLINK', text)
        self.assertIn("'+1", text)
        self.assertIn('-100.00', text)  # plain negative numbers stay numbers


class FakeIMAP:
    """Just enough of imaplib.IMAP4 for collect_imap."""

    def __init__(self, messages):
        self.messages = messages  # {uid: raw bytes}
        self.stored = []

    def select(self, mailbox, readonly=False):
        self.readonly = readonly
        return 'OK', [str(len(self.messages)).encode()]

    def response(self, code):
        return code, [b'777']

    def uid(self, command, *args):
        command = command.upper()
        if command == 'SEARCH':
            return 'OK', [b' '.join(str(u).encode() for u in self.messages)]
        if command == 'FETCH':
            uids, what = args[0], args[1]
            uids = uids.decode() if isinstance(uids, bytes) else uids
            out = []
            for u in str(uids).split(','):
                raw = self.messages[int(u)]
                if 'BODYSTRUCTURE' in what:
                    kind = b'("application" "pdf" NIL NIL NIL "base64" 1000)' if b'application/pdf' in raw else b'("text" "plain")'
                    hdr = b'Message-ID: <m' + u.encode() + b'@x>\r\n\r\n'
                    out += [(u.encode() + b' (UID ' + u.encode() + b' BODYSTRUCTURE ' + kind + b' BODY[HEADER.FIELDS (FROM MESSAGE-ID)] {%d}' % len(hdr), hdr), b')']
                else:
                    out += [(u.encode() + b' (UID ' + u.encode() + b' BODY[] {%d}' % len(raw), raw), b')']
            return 'OK', out
        if command == 'STORE':
            self.stored.append(args)
            return 'OK', []
        raise AssertionError(command)

    def close(self):
        raise AssertionError('CLOSE expunges deleted messages: it must never be used')

    def logout(self):
        pass


class TestImap(BotTestCase):
    def test_collects_once_and_skips_non_invoices(self):
        self.bot.set_option('imap', {'enabled': True, 'host': 'imap.example', 'username': 'szamla@x.hu'})
        os.environ['INVOICEBOT_IMAP_PASSWORD'] = 'x'

        def mail(subject, attachment=None, name='a.pdf'):
            m = email.message.EmailMessage()
            m['From'] = 'Supplier <billing@supplier.example>'
            m['Subject'] = subject
            m['Message-ID'] = f'<{subject.replace(" ", "")}@x>'
            m.set_content('hello')
            if attachment:
                m.add_attachment(attachment, maintype='application', subtype='pdf', filename=name)
            return m.as_bytes()

        brochure = simple_pdf([(50, 'Autumn newsletter'), (50, 'Our new products are here. Visit our shop.')])
        fake = FakeIMAP({1: mail('Invoice', TRANSFER_INVOICE), 2: mail('No attachment'), 3: mail('Brochure', brochure)})
        rep = collect.Report()
        collect.collect_imap(self.bot, rep, connect=lambda icfg, pw: fake)
        self.assertEqual(rep.errors, [])
        self.assertEqual([i['result'] for i in rep.items], ['new', 'skipped'])
        self.assertTrue(fake.readonly)
        rep2 = collect.Report()
        collect.collect_imap(self.bot, rep2, connect=lambda icfg, pw: fake)
        self.assertEqual(rep2.items, [])  # already seen
        con = self.con()
        try:
            self.assertEqual(con.execute('SELECT count(*) FROM seen_messages').fetchone()[0], 3 + 3)
        finally:
            con.close()
        del os.environ['INVOICEBOT_IMAP_PASSWORD']

    def test_failed_fetch_is_retried_not_forgotten(self):
        self.bot.set_option('imap', {'enabled': True, 'host': 'imap.example', 'username': 'szamla@x.hu', 'mark_seen': True})
        os.environ['INVOICEBOT_IMAP_PASSWORD'] = 'x'
        m = email.message.EmailMessage()
        m['From'] = 'Supplier <billing@supplier.example>'
        m['Message-ID'] = '<inv1@x>'
        m.set_content('hello')
        m.add_attachment(TRANSFER_INVOICE, maintype='application', subtype='pdf', filename='a.pdf')
        fake = FakeIMAP({1: m.as_bytes()})
        real_uid, fails = fake.uid, [1]

        def flaky(command, *args):
            if command.upper() == 'FETCH' and fails[0]:
                fails[0] -= 1
                return 'NO', [b'Some messages could not be FETCHed (Failure)']
            return real_uid(command, *args)
        fake.uid = flaky
        rep = collect.Report()
        collect.collect_imap(self.bot, rep, connect=lambda icfg, pw: fake)
        self.assertEqual([i for i in rep.items if i['result'] == 'new'], [])
        rep = collect.Report()
        collect.collect_imap(self.bot, rep, connect=lambda icfg, pw: fake)
        self.assertEqual(len([i for i in rep.items if i['result'] == 'new']), 1)
        self.assertTrue(fake.stored)  # marked as seen, on a folder opened read-write, without CLOSE
        del os.environ['INVOICEBOT_IMAP_PASSWORD']

    def test_folder_names_utf7(self):
        self.assertEqual(collect.imap_utf7('Számlák'), 'Sz&AOE-ml&AOE-k')
        self.assertEqual(collect.imap_utf7('A&B'), 'A&-B')
        self.assertEqual(collect.imap_utf7('INBOX'), 'INBOX')


if __name__ == '__main__':
    unittest.main()
