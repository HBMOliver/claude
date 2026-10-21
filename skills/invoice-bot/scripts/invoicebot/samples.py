"""Sample invoices for trying the bot (invoice_bot.py demo) and for the tests.

The buyer on every sample is the demo company "Minta Ügynökség Kft." (tax number 11223344-2-41).
"""
from .pdfwriter import PdfDoc

DEMO_COMPANY = {'name': 'Minta Ügynökség Kft.', 'aliases': ['Minta Ugynokseg'], 'tax_ids': ['11223344-2-41'],
                'email_domains': ['minta-ugynokseg.hu']}
BUYER = ['Minta Ügynökség Kft.', '1037 Budapest, Bécsi út 100.', 'Adószám: 11223344-2-41']


def _hu_invoice(seller, number, method, fulfil, issued, due, items, title='SZÁMLA', stamp=None, number_label='Számla sorszáma'):
    d = PdfDoc(f'{title} {number}')
    p = d.page()
    p.text(50, 60, title, size=20, bold=True)
    p.text(545, 60, f'{number_label}: {number}', size=10, bold=True, align='right')
    p.text(50, 105, 'Eladó', size=10, bold=True)
    p.text(310, 105, 'Vevő', size=10, bold=True)
    for i, (a, b) in enumerate(zip(seller + [''] * 4, BUYER + [''] * 4)):
        if a or b:
            p.text(50, 120 + 13 * i, a, size=9, bold=i == 0)
            p.text(310, 120 + 13 * i, b, size=9, bold=i == 0)
    y = 205
    p.line(50, y - 12, 545, y - 12)
    heads = ['Fizetési mód', 'Teljesítés dátuma', 'Számla kelte', 'Fizetési határidő']
    vals = [method, fulfil, issued, due]
    for i, (h, v) in enumerate(zip(heads, vals)):
        p.text(50 + 125 * i, y, h, size=9, bold=True)
        p.text(50 + 125 * i, y + 14, v, size=9)
    y = 255
    cols = [(50, 'Megnevezés', 'left'), (290, 'Menny.', 'right'), (370, 'Nettó ár', 'right'), (420, 'ÁFA', 'right'),
            (480, 'ÁFA érték', 'right'), (545, 'Bruttó ár', 'right')]
    for x, h, al in cols:
        p.text(x, y, h, size=9, bold=True, align=al)
    p.line(50, y + 5, 545, y + 5)
    net_t = vat_t = 0
    for i, (name, qty, net, rate) in enumerate(items):
        vat = round(net * rate / 100)
        net_t, vat_t = net_t + net, vat_t + vat
        yy = y + 20 + 14 * i
        for (x, _, al), v in zip(cols, [name, f'{qty} db', _ft(net), f'{rate}%', _ft(vat), _ft(net + vat)]):
            p.text(x, yy, v, size=9, align=al)
    yy = y + 30 + 14 * len(items)
    p.line(300, yy, 545, yy)
    p.text(300, yy + 14, 'Összesen', size=9, bold=True)
    p.text(370, yy + 14, _ft(net_t) + ' Ft', size=9, align='right')
    p.text(480, yy + 14, _ft(vat_t) + ' Ft', size=9, align='right')
    p.text(545, yy + 14, _ft(net_t + vat_t) + ' Ft', size=9, align='right')
    p.text(300, yy + 40, 'Fizetendő:', size=12, bold=True)
    p.text(545, yy + 40, _ft(net_t + vat_t) + ' Ft', size=12, bold=True, align='right')
    if stamp:
        p.text(50, yy + 80, stamp, size=14, bold=True)
    p.text(50, 800, 'A számla a Példa Számlázó online számlázó programmal készült. Példa Szoftver Kft.', size=7)
    return d.to_bytes(), net_t + vat_t


def _ft(n):
    return f'{n:,}'.replace(',', ' ')


def _receipt_en(seller, addr, number, receipt_no, paid, amount, card='Visa - 4242'):
    d = PdfDoc('Receipt')
    p = d.page()
    p.text(50, 60, 'Receipt', size=22, bold=True)
    rows = [('Invoice number', number), ('Receipt number', receipt_no), ('Date paid', paid), ('Payment method', card)]
    for i, (k, v) in enumerate(rows):
        p.text(50, 95 + 14 * i, k, size=9)
        p.text(160, 95 + 14 * i, v, size=9)
    p.text(50, 175, seller, size=10, bold=True)
    for i, a in enumerate(addr):
        p.text(50, 189 + 13 * i, a, size=9)
    p.text(320, 175, 'Bill to', size=10, bold=True)
    for i, a in enumerate(BUYER[:2] + ['Hungary']):
        p.text(320, 189 + 13 * i, a, size=9)
    p.text(50, 260, f'${amount:.2f} paid on {paid}', size=14, bold=True)
    p.text(50, 300, 'Description', size=9, bold=True)
    p.text(400, 300, 'Qty', size=9, bold=True, align='right')
    p.text(545, 300, 'Amount', size=9, bold=True, align='right')
    p.text(50, 316, 'Team plan (monthly)', size=9)
    p.text(400, 316, '1', size=9, align='right')
    p.text(545, 316, f'${amount:.2f}', size=9, align='right')
    for i, (k, v) in enumerate([('Subtotal', amount), ('Total', amount), ('Amount paid', amount)]):
        p.text(400, 350 + 14 * i, k, size=9, bold=k == 'Amount paid')
        p.text(545, 350 + 14 * i, f'${v:.2f}', size=9, align='right')
    return d.to_bytes()


def _de_invoice():
    d = PdfDoc('Rechnung')
    p = d.page()
    p.text(50, 50, 'Serverwerk Hosting GmbH  -  Industriestr. 25  -  91710 Gunzenhausen  -  USt-IdNr. DE812345678', size=7)
    for i, a in enumerate(BUYER[:2] + ['Ungarn']):
        p.text(50, 90 + 13 * i, a, size=10)
    rows = [('Rechnungsnummer:', 'R0012345678'), ('Rechnungsdatum:', '01.10.2026'), ('Fälligkeitsdatum:', '15.10.2026'),
            ('Kundennummer:', 'K123456')]
    for i, (k, v) in enumerate(rows):
        p.text(360, 90 + 13 * i, k, size=9)
        p.text(545, 90 + 13 * i, v, size=9, align='right')
    p.text(50, 180, 'Rechnung', size=16, bold=True)
    p.text(50, 210, 'Pos   Bezeichnung', size=9, bold=True)
    p.text(545, 210, 'Gesamt', size=9, bold=True, align='right')
    p.text(50, 226, '1     Dedicated Server AX41 (10/2026)', size=9)
    p.text(545, 226, '100,00 €', size=9, align='right')
    for i, (k, v) in enumerate([('Summe netto', '100,00 €'), ('Reverse Charge, MwSt. 0%', '0,00 €'), ('Gesamtbetrag', '100,00 €')]):
        p.text(360, 260 + 14 * i, k, size=9, bold=k == 'Gesamtbetrag')
        p.text(545, 260 + 14 * i, v, size=9, bold=k == 'Gesamtbetrag', align='right')
    p.text(50, 330, 'Bitte überweisen Sie den Betrag bis zum 15.10.2026 auf unser Konto.', size=9)
    return d.to_bytes()


def _utility():
    d = PdfDoc('Számla')
    p = d.page()
    p.text(50, 55, 'Fővárosi Áramszolgáltató Zrt.', size=14, bold=True)
    p.text(50, 70, '1132 Budapest, Váci út 72.  Adószám: 22334455-2-44', size=8)
    p.text(50, 110, 'SZÁMLA', size=18, bold=True)
    p.text(360, 110, 'Számlaszám: ÁR-2026-0991234', size=9, align='left')
    p.text(50, 140, 'Vevő:', size=9, bold=True)
    for i, a in enumerate(BUYER):
        p.text(50, 154 + 13 * i, a, size=9)
    rows = [('Elszámolt időszak:', '2026.09.01. - 2026.09.30.'), ('Számla kelte:', '2026.10.03.'),
            ('Fizetési határidő:', '2026.10.18.'), ('Fizetési mód:', 'Csoportos beszedési megbízás')]
    for i, (k, v) in enumerate(rows):
        p.text(320, 140 + 14 * i, k, size=9)
        p.text(420, 140 + 14 * i, v, size=9)
    p.text(50, 240, 'Fizetendő összeg:', size=12, bold=True)
    p.text(545, 240, '18.990 Ft', size=12, bold=True, align='right')
    return d.to_bytes()


def _proforma():
    d = PdfDoc('Díjbekérő')
    p = d.page()
    p.text(50, 60, 'DÍJBEKÉRŐ', size=20, bold=True)
    p.text(545, 60, 'Sorszám: D-2026-031', size=10, align='right')
    p.text(50, 100, 'Eladó', size=10, bold=True)
    p.text(310, 100, 'Vevő', size=10, bold=True)
    for i, (a, b) in enumerate(zip(['Rendezvény Pont Bt.', '1051 Budapest, Nádor u. 5.', 'Adószám: 33445566-1-41'], BUYER)):
        p.text(50, 115 + 13 * i, a, size=9)
        p.text(310, 115 + 13 * i, b, size=9)
    p.text(50, 180, 'Fizetési határidő: 2026.10.10.', size=9)
    p.text(50, 220, 'Fizetendő: 254 000 Ft', size=12, bold=True)
    p.text(50, 250, 'Ez a dokumentum nem számla. A számlát a befizetés után állítjuk ki.', size=8)
    return d.to_bytes()


def _no_number():
    d = PdfDoc('Invoice')
    p = d.page()
    p.text(50, 60, 'Brightline Studio Ltd', size=16, bold=True)
    p.text(50, 76, '12 Market Street, London', size=8)
    p.text(50, 120, 'INVOICE', size=18, bold=True)
    p.text(360, 120, 'Date: 2026-09-28', size=9)
    p.text(50, 150, 'Bill To:', size=9, bold=True)
    for i, a in enumerate(BUYER[:2]):
        p.text(50, 164 + 13 * i, a, size=9)
    p.text(50, 220, 'Illustrations for the autumn campaign', size=9)
    p.text(545, 220, '£800.00', size=9, align='right')
    p.text(400, 250, 'Total', size=10, bold=True)
    p.text(545, 250, '£800.00', size=10, bold=True, align='right')
    return d.to_bytes()


def demo_files():
    """[(file name, bytes)] — a typical month of incoming invoices."""
    a, _ = _hu_invoice(['Kovács és Társa Szolgáltató Kft.', '1111 Budapest, Fő utca 1.', 'Adószám: 87654321-2-43',
                        'Bankszámlaszám: 11773016-01234567'],
                       'E-KVT-2026-118', 'Átutalás', '2026.09.15.', '2026.09.15.', '2026.09.23.',
                       [('Google Ads kampánykezelés', 1, 100000, 27)])
    b, _ = _hu_invoice(['Fotó Műhely Bt.', '1072 Budapest, Klauzál tér 2.', 'Adószám: 44556677-1-42'],
                       'FM-2026/0042', 'Bankkártya', '2026.09.20.', '2026.09.20.', '2026.09.20.',
                       [('Termékfotózás, 20 kép', 1, 36000, 27)], number_label='Számlaszám')
    return [
        ('szamla_E-KVT-2026-118.pdf', a),
        ('fotomuhely.pdf', b),
        ('receipt-2345-6789.pdf', _receipt_en('Pixelcraft, Inc.', ['548 Market St', 'San Francisco, CA 94104'],
                                              'ABCD1234-0004', '2345-6789', 'September 15, 2026', 45.00)),
        ('Rechnung_R0012345678.pdf', _de_invoice()),
        ('aram_szeptember.pdf', _utility()),
        ('dijbekero.pdf', _proforma()),
        ('brightline.pdf', _no_number()),
    ]


def demo_bank_csv():
    """An OTP-style statement (cp1250, ';', decimal comma) paying two of the demo invoices."""
    rows = [
        'Könyvelés dátuma;Értéknap;Típus;Összeg;Devizanem;Partner neve;Közlemény',
        '2026.09.24.;2026.09.24.;Átutalás;-127 000,00;HUF;KOVÁCS ÉS TÁRSA KFT;E-KVT-2026-118 számla',
        '2026.09.25.;2026.09.25.;Jóváírás;350 000,00;HUF;Ügyfél Zrt.;Megbízási díj',
        '2026.10.02.;2026.10.02.;Kártyás vásárlás;-4 590,00;HUF;SPAR 1234;',
    ]
    eur = [
        'Booking date,Amount,Currency,Counterparty,Reference',
        '14/10/2026,-100.00,EUR,Serverwerk Hosting GmbH,R0012345678',
    ]
    return ('\r\n'.join(rows) + '\r\n').encode('cp1250'), ('\n'.join(eur) + '\n').encode('utf-8')
