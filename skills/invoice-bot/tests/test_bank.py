"""Bank statement parsing and matching payments to unpaid invoices."""
import os
import unittest
from decimal import Decimal

from helpers import BotTestCase, dbm
from invoicebot import bank, collect, pipeline as P, samples
from test_pipeline import TRANSFER_INVOICE, drop, simple_pdf

OTP = ('Számlaszám: 11773016-01234567;;;;;;\r\n'
       'Könyvelés dátuma;Értéknap;Típus;Összeg;Devizanem;Partner neve;Közlemény\r\n'
       '2026.10.21.;2026.10.21.;Átutalás;-381 000,00;HUF;TERVEZŐ STÚDIÓ KFT;TR-2026-7\r\n'
       '2026.10.22.;2026.10.22.;Jóváírás;500 000,00;HUF;Ügyfél Zrt.;Megbízás\r\n').encode('cp1250')
REVOLUT = (b'Type,Product,Started Date,Completed Date,Description,Amount,Fee,Currency,State,Balance\n'
           b'CARD_PAYMENT,Current,2026-10-02 10:00:00,2026-10-03 09:00:00,Figma,-45.00,0.00,USD,COMPLETED,100\n'
           b'CARD_PAYMENT,Current,2026-10-04 10:00:00,2026-10-04 11:00:00,Canva,-12.99,0.00,USD,REVERTED,100\n'
           b'TOPUP,Current,2026-10-01 10:00:00,2026-10-01 10:00:00,Top-up,500.00,0.00,USD,COMPLETED,600\n')
DEBIT_CREDIT = (b'Date,Description,Debit,Credit,Payee\n'
                b'10/23/2026,Invoice 2026-15,1250.00,,Lumen Translations\n'
                b'10/24/2026,Refund,,20.00,Shop\n')


class TestStatements(unittest.TestCase):
    def test_otp_cp1250_semicolon(self):
        rows = bank.read_statement(OTP)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r['date'], r['amount'], r['currency']), ('2026-10-21', Decimal('381000.00'), 'HUF'))
        self.assertEqual(r['counterparty'], 'TERVEZŐ STÚDIÓ KFT')
        self.assertEqual(r['description'], 'TR-2026-7')

    def test_revolut(self):
        rows = bank.read_statement(REVOLUT, 'EUR')
        self.assertEqual([(r['date'], r['amount'], r['currency']) for r in rows], [('2026-10-03', Decimal('45.00'), 'USD')])

    def test_debit_credit_columns_us_dates(self):
        rows = bank.read_statement(DEBIT_CREDIT, 'USD')
        self.assertEqual([(r['date'], r['amount']) for r in rows], [('2026-10-23', Decimal('1250.00'))])
        self.assertEqual(rows[0]['counterparty'], 'Lumen Translations')

    def test_no_header(self):
        with self.assertRaises(ValueError):
            bank.read_statement(b'hello,world\n1,2\n')

    def test_number_token_boundaries(self):
        self.assertTrue(bank._number_in('E-KVT-2026-118', 'utalas e-kvt-2026-118 szamla'))
        self.assertTrue(bank._number_in('2026/000123', 'szla 2026 000123'))
        self.assertFalse(bank._number_in('0042', 'ref 12004213'))
        self.assertFalse(bank._number_in('12', 'anything 12'))


class TestMatching(BotTestCase):
    def collect_one(self, data, name='a.pdf'):
        drop(self.bot, name, data)
        rep = collect.run(self.bot, imap=False)
        return [i for i in rep.items if i['result'] == 'new'][0]['id']

    def test_confident_match_moves_invoice(self):
        inv_id = self.collect_one(TRANSFER_INVOICE)
        res = bank.import_statement(self.bot, OTP, 'otp.csv')
        self.assertEqual([m['invoice_id'] for m in res['matched']], [inv_id])
        inv = self.inv(inv_id)
        self.assertEqual((inv['payment_source'], inv['payment_date'], inv['paid']), ('bank', '2026-10-21', 1))
        self.assertEqual(inv['file_path'], '2026/2026-10/2026-10-21_Tervezo-Studio_TR-2026-7.pdf')
        # importing the same statement again changes nothing
        res = bank.import_statement(self.bot, OTP, 'otp.csv')
        self.assertEqual((res['new_payments'], res['matched']), (0, []))

    def test_amount_only_is_a_suggestion(self):
        inv_id = self.collect_one(TRANSFER_INVOICE)
        csv = ('Könyvelés dátuma;Összeg;Devizanem;Partner neve;Közlemény\r\n'
               '2026.10.20.;-381 000;HUF;Valaki;utalás\r\n').encode('cp1250')
        res = bank.import_statement(self.bot, csv, 'x.csv')
        self.assertEqual(res['matched'], [])
        self.assertEqual([s['invoice_id'] for s in res['suggestions']], [inv_id])
        self.assertEqual(self.inv(inv_id)['paid'], 0)
        # dismissing it keeps it from coming back
        con = self.con()
        try:
            with con:
                bank.reject(self.bot, con, inv_id, res['suggestions'][0]['txn_id'])
        finally:
            con.close()
        self.assertEqual(bank.match_all(self.bot)['suggestions'], [])

    def test_payment_imported_before_the_invoice_arrives(self):
        bank.import_statement(self.bot, OTP, 'otp.csv')
        inv_id = self.collect_one(TRANSFER_INVOICE)
        inv = self.inv(inv_id)
        self.assertEqual((inv['payment_source'], inv['payment_date']), ('bank', '2026-10-21'))

    def test_wrong_amount_or_currency_never_matches(self):
        inv_id = self.collect_one(TRANSFER_INVOICE)
        csv = ('Könyvelés dátuma;Összeg;Devizanem;Partner neve;Közlemény\r\n'
               '2026.10.21.;-381 000;EUR;Tervező Stúdió;TR-2026-7\r\n'
               '2026.10.21.;-380 000;HUF;Tervező Stúdió;TR-2026-7\r\n').encode('cp1250')
        res = bank.import_statement(self.bot, csv, 'x.csv')
        self.assertEqual((res['matched'], res['suggestions']), ([], []))

    def test_unlink_and_mark_unpaid(self):
        inv_id = self.collect_one(TRANSFER_INVOICE)
        bank.import_statement(self.bot, OTP, 'otp.csv')
        inv = P.mark_unpaid(self.bot, inv_id)
        self.assertEqual(inv['paid'], 0)
        self.assertIsNone(inv['bank_txn_id'])
        self.assertTrue(inv['file_path'].startswith('_unpaid/'))

    def test_two_monthly_invoices_same_amount(self):
        def monthly(no, issued, due):
            return simple_pdf([(50, 'SZÁMLA'), (350, f'Számla sorszáma: NET-{no}'), (50, 'Eladó'), (300, 'Vevő'),
                               (50, 'Netszolg Kft.'), (300, 'Minta Ügynökség Kft.'),
                               (50, f'Számla kelte: {issued}   Fizetési határidő: {due}   Fizetési mód: Átutalás'),
                               (50, 'Fizetendő: 9 990 Ft')])
        a = self.collect_one(monthly('2026-09', '2026.09.05.', '2026.09.20.'), 'sep.pdf')
        b = self.collect_one(monthly('2026-10', '2026.10.05.', '2026.10.20.'), 'oct.pdf')
        csv = ('Könyvelés dátuma;Összeg;Devizanem;Partner neve;Közlemény\r\n'
               '2026.10.20.;-9 990;HUF;NETSZOLG KFT;havidij\r\n'
               '2026.09.21.;-9 990;HUF;NETSZOLG KFT;havidij\r\n').encode('cp1250')
        bank.import_statement(self.bot, csv, 'x.csv')
        self.assertEqual(self.inv(a)['payment_date'], '2026-09-21')
        self.assertEqual(self.inv(b)['payment_date'], '2026-10-20')


if __name__ == '__main__':
    unittest.main()
