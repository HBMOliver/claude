"""Field identification on invoice text as pdftotext -layout produces it."""
import unittest
from decimal import Decimal

from helpers import COMPANY
from invoicebot.extract import extract
from invoicebot.util import find_amounts, find_dates, fold, clean_text, parse_number, safe_component

SZAMLAZZ = """
                                              SZÁMLA
                                                                     Számla sorszáma: E-KVT-2026-118
 Eladó                                               Vevő
 Kovács és Társa Szolgáltató és Kereskedelmi Kft.    HB Marketing Kft.
 1111 Budapest, Fő utca 1.                           1037 Budapest, Bécsi út 100.
 Adószám: 87654321-2-43                              Adószám: 12345678-2-41
 Bankszámlaszám: 11773016-01234567-00000000

 Fizetési mód        Teljesítés dátuma     Számla kelte        Fizetési határidő
 Átutalás            2026.09.15.           2026.09.15.         2026.09.23.

 Megnevezés                     Menny.   Egységár    Nettó ár    ÁFA    ÁFA érték    Bruttó ár
 Google Ads kampánykezelés      1 db     100 000     100 000     27%    27 000       127 000

                                                   Nettó ár      ÁFA érték      Bruttó ár
                         ÁFA 27%                   100 000       27 000         127 000
                         Összesen                  100 000 Ft    27 000 Ft      127 000 Ft
 Fizetendő:                                                                     127 000 Ft

 A számla a Számlázz.hu online számlázó programmal készült. KBOSS.hu Kft.
"""

BUYER_FIRST = """
SZÁMLA                                                        Számlaszám: 2026/000123
Vevő:                                   Eladó:
HB Marketing Kft.                       Nyomda Pont Bt.
1037 Budapest, Bécsi út 100.            6720 Szeged, Kárász u. 2.
Adószám: 12345678-2-41                  Adószám: 23456789-1-06

Kiállítás dátuma: 2026. 10. 01.   Teljesítés dátuma: 2026. 09. 30.   Fizetési határidő: 2026. 10. 09.
Fizetési mód: Bankkártya

Végösszeg: 45 720 Ft
"""

STRIPE_INVOICE = """
Pixelcraft, Inc.                                          Invoice
548 Market St                                             Invoice number    ABCD1234-0004
San Francisco, CA 94104                                   Date of issue     September 15, 2026
                                                          Date due          September 15, 2026
Bill to
HB Marketing Kft.
Bécsi út 100.

$45.00 due September 15, 2026

Description                         Qty        Unit price          Amount
Professional plan                   3          $15.00              $45.00
                                              Subtotal             $45.00
                                              Total                $45.00
                                              Amount due           $45.00
"""

STRIPE_RECEIPT = """
Receipt
Invoice number   ABCD1234-0004
Receipt number   2345-6789
Date paid        September 15, 2026
Payment method   Visa - 4242

Pixelcraft, Inc.                       Bill to
548 Market St                          HB Marketing Kft.

$45.00 paid on September 15, 2026
Subtotal    $45.00
Total       $45.00
Amount paid $45.00
Amount due  $0.00
"""

HETZNER = """
Serverwerk Hosting GmbH - Industriestr. 25 - 91710 Gunzenhausen - USt-IdNr. DE812345678

HB Marketing Kft.                                          Rechnungsnummer: R0012345678
Bécsi út 100.                                              Rechnungsdatum: 01.10.2026
1037 Budapest                                              Fälligkeitsdatum: 15.10.2026

Rechnung
Pos   Bezeichnung                    Menge      Preis         Gesamt
1     Dedicated Server AX41          1          100,00 €      100,00 €
                                               Summe netto    100,00 €
                                               MwSt. 19%       19,00 €
                                               Gesamtbetrag   119,00 €
"""

CREDIT_NOTE = """
JÓVÁÍRÓ SZÁMLA (SZTORNÓ)                              Számla sorszáma: E-KVT-2026-131
Eredeti számla sorszáma: E-KVT-2026-118
Eladó                                               Vevő
Kovács és Társa Kft.                                HB Marketing Kft.
Számla kelte: 2026.09.30.     Fizetési határidő: 2026.09.30.     Fizetési mód: Átutalás
Fizetendő:                                                          -127 000 Ft
"""

PROFORMA = """
DÍJBEKÉRŐ                                                    Sorszám: D-2026-031
Eladó                                         Vevő
Rendezvény Pont Bt.                           HB Marketing Kft.
Fizetési határidő: 2026.10.10.
Fizetendő: 254 000 Ft
"""

EUR_HU = """
SZÁMLA                                           Számla sorszáma: ABC-2026-77
Szállító:                                        Vevő:
Lumen Fordítóiroda Kft.                          HB Marketing Kft.
Pénznem: EUR      Árfolyam: 1 EUR = 395,12 HUF
Számla kelte: 2026.09.05.  Teljesítés: 2026.09.05.  Fizetési határidő: 2026.09.20.
Nettó összesen:                          984,25 EUR
ÁFA összesen (27%):                      265,75 EUR
Bruttó végösszeg:                      1.250,00 EUR
ÁFA forintban: 105 004 Ft
"""

US_AMBIGUOUS = """
Brightway Media LLC
INVOICE
Invoice #: 1043
Invoice Date: 10/05/2026
Due Date: 11/04/2026
Terms: Net 30
Bill To:
HB Marketing Kft.
Amount Due: $2,450.00
"""

UTILITY = """
Fővárosi Áramszolgáltató Zrt.
1132 Budapest, Váci út 72.  Adószám: 22334455-2-44
SZÁMLA                                  Számlaszám: ÁR-2026-0991234
Vevő:                                   Elszámolt időszak: 2026.09.01. - 2026.09.30.
HB Marketing Kft.                       Számla kelte: 2026.10.03.
                                        Fizetési határidő: 2026.10.18.
                                        Fizetési mód: Csoportos beszedési megbízás
Előző időszak fizetendő: 15 000 Ft
Fizetendő összeg:                                            18.990 Ft
"""

PAID_STAMP = """
SZÁMLA                                  Számlaszám: WS-2026/0451
Eladó: Webshop Kellék Kft.              Vevő: HB Marketing Kft.
Számla kelte: 2026.09.10.   Fizetési határidő: 2026.09.10.
Fizetés dátuma: 2026.09.12.
FIZETVE
Végösszeg: 12 700,- Ft
"""


def ex(text, sender=None, company=COMPANY):
    return extract(text, {'sender': sender} if sender else {}, company)


class TestParsers(unittest.TestCase):
    def test_dates(self):
        def d(s, order='DMY'):
            hits = find_dates(fold(clean_text(s)))
            return hits[0].get(order).isoformat() if hits else None
        self.assertEqual(d('2026.09.15.'), '2026-09-15')
        self.assertEqual(d('2026. 09. 15.'), '2026-09-15')
        self.assertEqual(d('15.09.2026'), '2026-09-15')
        self.assertEqual(d('09/23/2026'), '2026-09-23')
        self.assertEqual(d('05/10/2026', 'MDY'), '2026-05-10')
        self.assertEqual(d('05/10/2026', 'DMY'), '2026-10-05')
        self.assertEqual(d('September 15, 2026'), '2026-09-15')
        self.assertEqual(d('30 Sep 2026'), '2026-09-30')
        self.assertEqual(d('2026. szeptember 15.'), '2026-09-15')
        self.assertEqual(d('15. März 2026'), '2026-03-15')
        self.assertIsNone(d('Adószám: 12345678-2-41'))
        self.assertIsNone(d('Tel: 06-30-123-4567'))

    def test_amounts(self):
        def a(s):
            return [(h.value, h.currency) for h in find_amounts(fold(clean_text(s)))]
        self.assertEqual(a('Fizetendő: 127 000 Ft'), [(Decimal('127000'), 'HUF')])
        self.assertEqual(a('Total $1,200.00'), [(Decimal('1200.00'), 'USD')])
        self.assertEqual(a('Gesamtbetrag 119,00 €'), [(Decimal('119.00'), 'EUR')])
        self.assertEqual(a('18.990 Ft'), [(Decimal('18990'), 'HUF')])
        self.assertEqual(a('12 700,- Ft'), [(Decimal('12700'), 'HUF')])
        self.assertEqual(a('-127 000 Ft'), [(Decimal('-127000'), 'HUF')])
        self.assertEqual(a('1.250,00 EUR'), [(Decimal('1250.00'), 'EUR')])
        self.assertEqual(a('ÁFA 27%'), [])
        self.assertEqual(a('Bank: 11773016-01234567-00000000 Total 500 EUR'), [(Decimal('500'), 'EUR')])
        self.assertEqual(parse_number('0.125'), Decimal('0.125'))

    def test_safe_component(self):
        self.assertEqual(safe_component('Kovács és Társa'), 'Kovacs-es-Tarsa')
        self.assertEqual(safe_component('HBM/2026/0042'), 'HBM-2026-0042')
        self.assertEqual(safe_component('a_b'), 'a-b')
        self.assertEqual(safe_component('CON'), 'CON-')


class TestExtract(unittest.TestCase):
    def test_szamlazz_layout(self):
        r = ex(SZAMLAZZ, 'Számlázz.hu <noreply@szamlazz.hu>')
        self.assertEqual(r['supplier'], 'Kovács és Társa')  # not Google (item line), not KBOSS (footer), not the buyer
        self.assertEqual(r['supplier_tax_id'], '87654321-2-43')
        self.assertEqual(r['invoice_number'], 'E-KVT-2026-118')
        self.assertEqual((r['issue_date'], r['fulfilment_date'], r['due_date']), ('2026-09-15', '2026-09-15', '2026-09-23'))
        self.assertEqual((r['amount'], r['currency']), ('127000.00', 'HUF'))
        self.assertEqual(r['payment_method'], 'transfer')
        self.assertFalse(r['paid_stamp'])
        self.assertGreaterEqual(r['confidence']['supplier'], 0.85)

    def test_buyer_block_first(self):
        r = ex(BUYER_FIRST)
        self.assertEqual(r['supplier'], 'Nyomda Pont')
        self.assertEqual(r['invoice_number'], '2026/000123')
        self.assertEqual((r['issue_date'], r['fulfilment_date'], r['due_date']), ('2026-10-01', '2026-09-30', '2026-10-09'))
        self.assertEqual(r['payment_method'], 'card')
        self.assertEqual(r['amount'], '45720.00')

    def test_stripe_invoice(self):
        r = ex(STRIPE_INVOICE, 'Pixelcraft <invoice+statements@stripe.com>')
        self.assertEqual(r['supplier'], 'Pixelcraft')
        self.assertEqual(r['invoice_number'], 'ABCD1234-0004')
        self.assertEqual((r['issue_date'], r['due_date']), ('2026-09-15', '2026-09-15'))
        self.assertEqual((r['amount'], r['currency']), ('45.00', 'USD'))
        self.assertIsNone(r['paid_date'])
        self.assertFalse(r['paid_stamp'])

    def test_stripe_receipt(self):
        r = ex(STRIPE_RECEIPT)
        self.assertEqual(r['doc_type'], 'receipt')
        self.assertEqual(r['invoice_number'], 'ABCD1234-0004')  # not the receipt number
        self.assertEqual(r['paid_date'], '2026-09-15')
        self.assertEqual(r['payment_method'], 'card')
        self.assertEqual(r['amount'], '45.00')  # not "Amount due $0.00"
        self.assertTrue(r['paid_stamp'])

    def test_german(self):
        r = ex(HETZNER, 'Serverwerk <billing@serverwerk.de>')
        self.assertEqual(r['supplier'], 'Serverwerk Hosting')
        self.assertEqual(r['invoice_number'], 'R0012345678')
        self.assertEqual((r['issue_date'], r['due_date']), ('2026-10-01', '2026-10-15'))
        self.assertEqual((r['amount'], r['currency']), ('119.00', 'EUR'))  # not "Summe netto"

    def test_credit_note(self):
        r = ex(CREDIT_NOTE)
        self.assertEqual(r['doc_type'], 'credit_note')
        self.assertEqual(r['invoice_number'], 'E-KVT-2026-131')  # its own, not the original's
        self.assertEqual(r['amount'], '-127000.00')

    def test_proforma(self):
        self.assertEqual(ex(PROFORMA)['doc_type'], 'proforma')

    def test_eur_invoice_with_huf_conversion(self):
        r = ex(EUR_HU)
        self.assertEqual(r['supplier'], 'Lumen Fordítóiroda')
        self.assertEqual((r['amount'], r['currency']), ('1250.00', 'EUR'))
        self.assertEqual(r['due_date'], '2026-09-20')

    def test_us_dates_resolved_by_currency(self):
        r = ex(US_AMBIGUOUS)
        self.assertEqual(r['issue_date'], '2026-10-05')
        self.assertEqual(r['due_date'], '2026-11-04')
        self.assertEqual(r['invoice_number'], '1043')
        self.assertEqual((r['amount'], r['currency']), ('2450.00', 'USD'))
        self.assertEqual(r['supplier'], 'Brightway Media')
        self.assertEqual(r['terms_days'], 30)

    def test_utility_direct_debit(self):
        r = ex(UTILITY)
        self.assertEqual(r['invoice_number'], 'ÁR-2026-0991234')
        self.assertEqual(r['amount'], '18990.00')  # not the previous period
        self.assertEqual(r['payment_method'], 'direct_debit')
        self.assertEqual(r['issue_date'], '2026-10-03')  # not the billing period
        self.assertEqual(r['supplier'], 'Fővárosi Áramszolgáltató')

    def test_paid_stamp_and_date(self):
        r = ex(PAID_STAMP)
        self.assertEqual(r['paid_date'], '2026-09-12')
        self.assertTrue(r['paid_stamp'])
        self.assertEqual(r['amount'], '12700.00')
        self.assertEqual(r['supplier'], 'Webshop Kellék')
        self.assertEqual(r['invoice_number'], 'WS-2026/0451')

    def test_own_company_never_supplier(self):
        text = 'SZÁMLA  Számlaszám: X-1\nHB MARKETING KFT.\nVevő: HB Marketing Kft.\nFizetendő: 1 000 Ft\n'
        r = ex(text)
        self.assertNotEqual((r['supplier'] or '').lower(), 'hb marketing')

    def test_sales_invoice_detected(self):
        text = ('SZÁMLA                       Számlaszám: HBM-2026-0001\nEladó                         Vevő\n'
                'HB Marketing Kft.             Ügyfél Zrt.\nSzámla kelte: 2026.10.01.\nFizetendő: 100 000 Ft\n')
        r = ex(text)
        self.assertTrue(r['own_company_is_seller'])
        self.assertIsNone(r['supplier'])


if __name__ == '__main__':
    unittest.main()
