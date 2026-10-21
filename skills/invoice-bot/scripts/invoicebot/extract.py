"""Read an invoice's text and identify the supplier, invoice number, dates, total and payment details.

How it works: every line is scanned for known labels (Hungarian, English, German, plus a little French
and Italian), e.g. "Számla sorszáma", "Fizetési határidő", "Invoice date", "Gesamtbetrag". A label's
value is taken from the same line (to its right) or, for table headers, from the line below at the same
column. Supplier and buyer blocks ("Eladó" / "Vevő", "From" / "Bill to") are cut out by column so the
buyer (your company) is never taken for the supplier. Every field gets a confidence between 0 and 1;
low-confidence or missing fields send the invoice to review.
"""
import re
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from . import suppliers as S
from .util import (clean_text, currency_mentions, dec_str, find_amounts, find_dates, fold, iso, norm_key,
                   today, CURRENCY_WORDS)

B = r'(?<![a-z0-9])'
E = r'(?![a-z0-9])'


class Label:
    __slots__ = ('rx', 'weight', 'inline', 'title')

    def __init__(self, rx, weight, inline=False, title=False):
        # words of a label are one or two spaces apart; a wider gap is a column boundary
        rx = re.sub(r'(?<!\^)\\s\*', ' {0,2}', rx)
        self.rx = re.compile(rx)
        self.weight = weight
        self.inline = inline   # the value must be on the same line
        self.title = title     # a document title ("SZÁMLA 2026-00077"): take the very next token only


def _L(rx, w, **kw):
    return Label(rx, w, **kw)


LABELS = {
    'number': [
        _L(B + r'szamla\s*(?:sor)?szama?' + E, 10),
        _L(B + r'szamla\s*(?:azonosito(?:ja)?|sorszam)' + E, 9),
        _L(B + r'sorszam(?:a)?' + E, 7),
        _L(B + r'bizonylat\s*(?:sor)?szam(?:a)?' + E, 7),
        _L(B + r'invoice\s*(?:(?:number|no|nr|num|id)' + E + r'\.?|#)', 10),
        _L(B + r'inv\.?\s*(?:no' + E + r'\.?|#)', 8),
        _L(B + r'bill\s*(?:number|no)' + E + r'\.?', 8),
        _L(B + r'receipt\s*(?:(?:number|no|nr)' + E + r'\.?|#)', 6),
        _L(B + r'document\s*(?:number|no)' + E + r'\.?', 6),
        _L(B + r'transaction\s*(?:id|number|no)' + E, 4),
        _L(B + r'reference\s*(?:number|no)' + E, 3),
        _L(B + r'rechnungs?\s*-?\s*(?:nummer|nr)' + E + r'\.?', 10),
        _L(B + r'beleg\s*-?\s*(?:nummer|nr)' + E + r'\.?', 6),
        _L(B + r'(?:facture|fattura|factura)\s*(?:n[o°]|nr|numero|num)' + E + r'\.?', 8),
        _L(B + r'numero\s*(?:de\s*)?(?:facture|factura|fattura)' + E, 9),
        _L(r'^\s*(?:e-?)?szamla' + E, 3, title=True),
        _L(r'^\s*(?:tax\s*)?invoice' + E, 3, title=True),
        _L(r'^\s*rechnung' + E, 3, title=True),
    ],
    'issue': [
        _L(B + r'kiallitas\s*(?:datuma|kelte|napja|ideje)' + E, 10),
        _L(B + r'szamla\s*kelte?' + E, 10),
        _L(B + r'kibocsatas\s*(?:datuma|kelte)' + E, 9),
        _L(B + r'kelte?' + E, 7),
        _L(B + r'kiallitva' + E, 6),
        _L(B + r'invoice\s*date' + E, 10),
        _L(B + r'date\s*of\s*(?:issue|invoice)' + E, 10),
        _L(B + r'issue\s*date' + E, 10),
        _L(B + r'date\s*issued' + E, 9),
        _L(B + r'issued\s*(?:on|date)' + E, 8),
        _L(B + r'(?:billing|bill|receipt|document|statement|tax\s*invoice)\s*date' + E, 7),
        _L(B + r'issued' + E, 5, inline=True),
        _L(B + r'rechnungsdatum' + E, 10),
        _L(B + r'ausstellungsdatum' + E, 9),
        _L(B + r'(?:beleg|quittungs)datum' + E, 7),
        _L(B + r'date\s*de\s*(?:facture|facturation)' + E, 9),
        _L(B + r'data\s*(?:fattura|emissione)' + E, 9),
        _L(B + r'date' + E, 3, inline=True),
        _L(B + r'datum' + E, 3, inline=True),
    ],
    'fulfilment': [
        _L(B + r'teljesites\s*(?:datuma|kelte|napja|idopontja|ideje)' + E, 10),
        _L(B + r'teljesites' + E, 6),
        _L(B + r'date\s*of\s*(?:supply|delivery|service)' + E, 9),
        _L(B + r'(?:supply|delivery|service|performance)\s*date' + E, 8),
        _L(B + r'tax\s*point(?:\s*date)?' + E, 8),
        _L(B + r'(?:liefer\s*-?\s*/?\s*)?leistungsdatum' + E, 9),
        _L(B + r'lieferdatum' + E, 8),
    ],
    'due': [
        _L(B + r'(?:be)?fizetesi\s*hatarido(?:\s*napja)?' + E, 10),
        _L(B + r'fiz\.?\s*hat(?:arido|\.)' + E, 8),
        _L(B + r'hatarido' + E, 6),
        _L(B + r'esedekesseg(?:\s*(?:datuma|napja))?' + E, 9),
        _L(B + r'esedekes' + E, 7),
        _L(B + r'due\s*date' + E, 10),
        _L(B + r'date\s*due' + E, 10),
        _L(B + r'payment\s*due(?:\s*date)?' + E, 9),
        _L(B + r'payment\s*deadline' + E, 9),
        _L(B + r'due\s*(?:by|on)' + E, 8),
        _L(B + r'pay(?:able)?\s*(?:by|before)' + E, 7),
        _L(B + r'due' + E, 5, inline=True),
        _L(B + r'f(?:a|ae)lligkeit(?:sdatum)?' + E, 10),
        _L(B + r'f(?:a|ae)llig(?:\s*(?:am|bis|zum))?' + E, 9),
        _L(B + r'zahlbar\s*bis' + E, 9),
        _L(B + r'zahlungs(?:ziel|frist)' + E, 7),
        _L(B + r'date\s*d\'?\s*echeance' + E, 9),
        _L(B + r'scadenza' + E, 8),
    ],
    'paid': [
        _L(B + r'(?:fizetes|kifizetes|kiegyenlites|befizetes)\s*(?:datuma|napja|idopontja)' + E, 10),
        _L(B + r'(?:fizetve|kifizetve|kiegyenlitve)' + E, 6, inline=True),
        _L(B + r'date\s*paid' + E, 10),
        _L(B + r'paid\s*(?:on|at|date)' + E, 10),
        _L(B + r'payment\s*(?:received|made)(?:\s*on)?' + E, 8),
        _L(B + r'charged\s*on' + E, 8),
        _L(B + r'payment\s*date' + E, 7),
        _L(B + r'paid' + E, 4, inline=True),
        _L(B + r'bezahlt\s*am' + E, 10),
        _L(B + r'zahlungs(?:datum|eingang)(?:\s*am)?' + E, 8),
        _L(B + r'bezahlt' + E, 5, inline=True),
    ],
    'method': [
        _L(B + r'fizetesi\s*mod(?:ja)?' + E, 10),
        _L(B + r'fizetes\s*modja' + E, 10),
        _L(B + r'fiz\.?\s*mod' + E, 8),
        _L(B + r'payment\s*(?:method|type|mode)' + E, 9),
        _L(B + r'method\s*of\s*payment' + E, 9),
        _L(B + r'paid\s*(?:with|by|via|using)' + E, 9),
        _L(B + r'zahlungs\s*(?:art|weise|methode|mittel)' + E, 9),
        _L(B + r'zahlart' + E, 8),
        _L(B + r'mode\s*de\s*(?:paiement|reglement)' + E, 9),
        _L(r'(?:^|(?<=\s\s))\s*method' + E, 5),
    ],
    'total': [
        _L(B + r'fizetendo(?:\s*(?:vegosszeg|osszeg|brutto(?:\s*osszeg)?|ertek))?' + E, 10),
        _L(B + r'osszesen\s*fizetendo' + E, 10),
        _L(B + r'brutto\s*vegosszeg' + E, 10),
        _L(B + r'vegosszeg' + E, 9),
        _L(B + r'szamla\s*(?:vegosszege|osszege|osszesen)' + E, 9),
        _L(B + r'mindosszesen' + E, 9),
        _L(B + r'brutto\s*(?:osszesen|osszeg|ertek(?:\s*osszesen)?|ar\s*osszesen)' + E, 8),
        _L(B + r'osszesen\s*brutto' + E, 8),
        _L(B + r'osszesen' + E, 5),
        _L(B + r'brutto' + E, 3),
        _L(B + r'total\s*(?:amount\s*)?(?:due|payable|to\s*pay)' + E, 10),
        _L(B + r'amount\s*(?:due|payable|to\s*pay)' + E, 10),
        _L(B + r'balance\s*due' + E, 10),
        _L(B + r'grand\s*total' + E, 10),
        _L(B + r'invoice\s*total' + E, 9),
        _L(B + r'total\s*\(?\s*(?:incl|including|inc)' + E, 9),
        _L(B + r'(?:total\s*gross|gross\s*total)' + E, 9),
        _L(B + r'(?:amount|total)\s*paid' + E, 9),
        _L(B + r'total\s*amount' + E, 8),
        _L(B + r'total\s*in\s*[a-z]{3}' + E, 8),
        _L(B + r'total' + E, 5),
        _L(B + r'sum' + E, 3),
        _L(B + r'amount' + E, 2),
        _L(B + r'gesamt\s*-?\s*(?:betrag|summe)' + E, 10),
        _L(B + r'(?:rechnungs|end|zahl)betrag' + E, 10),
        _L(B + r'zu\s*zahlen(?:der\s*betrag)?' + E, 10),
        _L(B + r'brutto\s*(?:betrag|summe)' + E, 8),
        _L(B + r'(?:summe|gesamt)' + E, 5),
        _L(B + r'(?:montant\s*total|total\s*ttc|net\s*a\s*payer|totale(?:\s*fattura)?)' + E, 9),
    ],
    'seller': [
        _L(B + r'(?:elado|szallito|szolgaltato|kibocsato|szamlakibocsato|kiallito|forgalmazo)' + E, 10),
        _L(B + r'szamla\s*kiallitoja' + E, 10),
        _L(B + r'(?:vallalkozo|megbizott)' + E, 8),
        _L(B + r'(?:supplier|seller|vendor|provider|merchant)' + E, 9),
        _L(B + r'(?:billed?|invoiced?|issued|sold|sent)\s*(?:from|by)' + E, 9),
        _L(B + r'service\s*provider' + E, 9),
        _L(B + r'from' + E, 6),
        _L(B + r'(?:verk(?:a|ae)ufer|lieferant|rechnungssteller|auftragnehmer|leistungserbringer)' + E, 10),
        _L(B + r'(?:fournisseur|vendeur|fornitore)' + E, 9),
    ],
    'buyer': [
        _L(B + r'(?:vevo|megrendelo|vasarlo|ugyfel|megbizo|cimzett)' + E, 10),
        _L(B + r'szamla\s*cimzett(?:je)?' + E, 10),
        _L(B + r'(?:billed?|invoiced?|sold|ship(?:ped)?|issued|charged)\s*to' + E, 10),
        _L(B + r'(?:customer|client|buyer|recipient|purchaser)' + E, 9),
        _L(B + r'to' + E, 4),
        _L(B + r'(?:rechnungsempf(?:a|ae)nger|kunde|auftraggeber|k(?:a|ae)ufer|leistungsempf(?:a|ae)nger)' + E, 10),
        _L(B + r'(?:destinataire|acheteur|cliente|committente)' + E, 9),
    ],
    'currency': [
        _L(B + r'(?:penznem|devizanem|deviza|currency|w(?:a|ae)hrung|valuta|devise)' + E, 10),
    ],
    'terms': [
        _L(B + r'(?:payment\s*terms|terms\s*of\s*payment|terms|fizetesi\s*feltetel(?:ek)?|zahlungsbedingungen)' + E, 8),
    ],
}

DATE_FIELDS = ('issue', 'fulfilment', 'due', 'paid')
BLOCK_FIELDS = ('seller', 'buyer')

# a credit note quotes the number of the invoice it corrects: not its own number
_BAD_NUMBER_PREFIX = re.compile(
    r'(?:eredeti|original|helyesbitett|helyesbitendo|modositott|sztornozott|stornozott|stornierte|hivatkozott|'
    r'kapcsolodo|referenced|related|corrected|cancelled|canceled|korrigierte|urspr\w*|vonatkozo|elozo|previous|'
    r'customer|vevo|ugyfel|order|rendeles|megrendeles|purchase|po|contract|szerzodes|proforma|dijbekero)'
    r'\W*(?:\w+\W*){0,2}$')
_WEAK_DATE_PREFIX = re.compile(
    r'(?:start|end|from|to|birth|order|rendeles|delivery|expiry|expiration|renewal|next|last|shipping|travel|'
    r'transaction|value|period|valid|print|nyomtatas|lejarat|ervenyes|kezdo|veg)\W*$')
_NOT_GROSS = re.compile(
    B + r'(?:sub\s*-?\s*total|reszosszeg|resz\s*-?\s*osszeg|netto|net|excl\w*|excluding|without|ex\.?\s*(?:vat|tax)|'
    r'afa\s*nelkul|afa|vat|tax|taxes|mwst|ust|steuer\w*|atvitel|carried\s*forward|brought\s*forward|discount|'
    r'kedvezmeny|engedmeny|deposit|eloleg|previous|elozo|forintban|huf\s*-?\s*ban|ft\s*-?\s*ban|arfolyam|'
    r'exchange\s*rate|kurs|kerekites|rounding|szallitas\s*dija|shipping|egysegar|unit\s*price|quantity|menny\w*)' + E)
_GROSS = re.compile(
    B + r'(?:incl\w*|including|inkl\w*|inc\.?\s*(?:vat|tax)|brutto|gross|afa\s*-?\s*val|afa\s*-?\s*t\s*tartalmaz\w*|'
    r'with\s*(?:vat|tax)|(?:vat|tax)\s*included|fizetendo|vegosszeg|total\s*due|amount\s*due)' + E)
_FOOTER = re.compile(
    r'(?:keszult|keszitette|generalt|generated|powered\s*by|created\s*(?:with|by|using)|szamlazo\s*program\w*|'
    r'szamlazoprogram\w*|szamlazo\s*rendszer\w*|online\s*szamlazo|invoicing\s*(?:software|system|platform)|'
    r'invoice\s*software|szoftver|software|nyomtatvany|program\s*neve|rendszereben|rendszerrel|alkalmazassal)')
_NOT_NAME = re.compile(
    r'^(?:nev|name|cegnev|company\s*name|adoszam|adoazonosito|kozossegi|eu\s*adoszam|vat|tax|cegjegyzek\w*|nyilvantartasi|bankszamla\w*|bank|iban|'
    r'swift|bic|telefon|tel|phone|mobil|fax|e-?mail|web|www|http|cim|szekhely|address|irsz|iranyitoszam|reg\b|'
    r'registration|company\s*(?:no|number|reg)|ust|steuer|kontakt|contact|ugyfelszam|ugyfel\s*azonosito|'
    r'customer\s*(?:no|number|id)|account|szamlaszam|szamla\s*sorszama|datum|date|oldal|page|eredeti|masolat|'
    r'peldany|copy|original|invoice|szamla|rechnung|receipt|nyugta|vevo|elado|szallito|supplier|seller|buyer|'
    r'customer|bill\s*to|from|to|attn|c/o|postal|zip|city|varos|orszag|country|hungary|magyarorszag|budapest)\b')
_BANK_CONTEXT = re.compile(r'(?:bank|szamlavezeto|penzintezet|account|iban|swift|cegbirosag|court|nyilvantarto|'
                           r'konyvvizsgalo|auditor|biztosito|insurer|futar|courier|kiado|fizetesi\s*szolgaltato)\W*$')

METHOD_VALUES = [
    ('direct_debit', re.compile(B + r'(?:csoportos\s*beszed\w*|beszedesi\s*megbizas|direct\s*debit|sepa\s*(?:direct\s*debit|'
                                r'lastschrift)|lastschrift|bankeinzug|prelevement|addebito\s*diretto)')),
    ('cod', re.compile(B + r'(?:utanvet\w*|cash\s*on\s*delivery|nachnahme|contre\s*remboursement)')),
    ('card', re.compile(B + r'(?:bank\s*-?\s*kartya\w*|kartya\w*|szep\s*kartya|(?:credit|debit)\s*card|card|visa|'
                        r'mastercard|master\s*card|maestro|amex|american\s*express|apple\s*pay|google\s*pay|'
                        r'kreditkarte|ec\s*-?\s*karte|carte\s*bancaire|carta\s*di\s*credito)' + E)),
    ('paypal', re.compile(B + r'paypal' + E)),
    ('cash', re.compile(B + r'(?:keszpenz\w*|cash|barzahlung|bar|especes|contanti)' + E)),
    ('transfer', re.compile(B + r'(?:atutalas\w*|utalas\w*|(?:bank|wire)\s*transfer|transfer|(?:bank)?uberweisung|'
                            r'ueberweisung|virement|bonifico)' + E)),
    ('online', re.compile(B + r'(?:online\s*(?:fizetes|payment|bankkartya)|simplepay|barion|stripe|sumup)' + E)),
]
_PAID_STAMP = re.compile(
    B + r'(?:fizetve|kifizetve|kiegyenlitve|penzugyileg\s*rendezve|a\s*szamla\s*kiegyenlites\w*|paid(?:\s*in\s*full)?|'
    r'payment\s*received|bezahlt|beglichen|acquittee|pagato)' + E)
_PAID_NEG = re.compile(r'(?:un|not\s*|nem\s*|to\s*be\s*|will\s*be\s*|must\s*be\s*|be\s*|nicht\s*|if\s*|once\s*|'
                       r'amount\s*|total\s*|still\s*|yet\s*|ha\s*|after\s*|until\s*)$')
_DOC_TYPES = [
    ('credit_note', re.compile(B + r'(?:jovairo\s*szamla|jovairo|sztorno\w*|storno\w*|credit\s*(?:note|memo)|'
                               r'helyesbito\s*szamla|modosito\s*szamla|gutschrift|rechnungskorrektur|avoir|'
                               r'nota\s*di\s*credito)' + E)),
    ('proforma', re.compile(B + r'(?:dijbekero|proforma|pro\s*-?\s*forma|eloleg\s*-?\s*bekero|fizetesi\s*felszolitas|'
                            r'payment\s*request|quotation|quote|estimate|arajanlat|ajanlat|angebot|'
                            r'kostenvoranschlag|order\s*confirmation|rendeles\s*visszaigazolas\w*|'
                            r'auftragsbest(?:a|ae)tigung|devis)' + E)),
    ('receipt', re.compile(B + r'(?:nyugta|receipt|quittung|kassenbon|kassenbeleg|recu|ricevuta|'
                           r'egyszerusitett\s*szamla)' + E)),
    ('invoice', re.compile(B + r'(?:e-?szamla|elektronikus\s*szamla|szamla|szamlaja|invoice|tax\s*invoice|'
                           r'vat\s*invoice|rechnung|facture|fattura|factura|faktura)' + E)),
]
_HU_WORDS = re.compile(B + r'(?:szamla|osszesen|fizetendo|vevo|elado|adoszam|teljesites|hatarido|afa|kelte|'
                       r'sorszama|fizetesi|brutto|netto)' + E)
_EN_WORDS = re.compile(B + r'(?:invoice|total|due|date|bill|amount|subtotal|tax|vat|paid|receipt)' + E)
_DE_WORDS = re.compile(B + r'(?:rechnung|betrag|datum|steuer|mwst|ust|summe|gesamt|zahlbar)' + E)


class Hit:
    __slots__ = ('field', 'line', 'start', 'end', 'weight', 'label')

    def __init__(self, field, line, start, end, label):
        self.field, self.line, self.start, self.end = field, line, start, end
        self.weight, self.label = label.weight, label

    def __repr__(self):
        return f'Hit({self.field} L{self.line} {self.start}-{self.end} w{self.weight})'


class Val:
    __slots__ = ('start', 'end', 'value')

    def __init__(self, start, end, value):
        self.start, self.end, self.value = start, end, value


class Region:
    __slots__ = ('top', 'bottom', 'left', 'right')

    def __init__(self, top, bottom, left, right):
        self.top, self.bottom, self.left, self.right = top, bottom, left, right

    def contains(self, line, col):
        return self.top <= line <= self.bottom and self.left <= col < self.right


class Doc:
    def __init__(self, text):
        self.text = clean_text(text)
        self.lines = self.text.split('\n')
        self.f = [fold(l) for l in self.lines]
        self.ftext = '\n'.join(self.f)
        self.n = len(self.lines)
        self._dates = {}
        self._amounts = {}
        self.hits = defaultdict(list)
        self.by_line = defaultdict(list)
        self._scan()
        self.order = 'DMY'

    def _scan(self):
        raw = []
        for field, labels in LABELS.items():
            for lab in labels:
                for i, fl in enumerate(self.f):
                    if not fl.strip():
                        continue
                    for m in lab.rx.finditer(fl):
                        if m.end() > m.start():
                            raw.append(Hit(field, i, m.start(), m.end(), lab))
        # a label inside a longer label is not a label ("date" in "due date", "paid" in "amount paid")
        raw.sort(key=lambda h: (h.line, -(h.end - h.start)))
        kept = defaultdict(list)
        for h in raw:
            if any(k.start <= h.start and h.end <= k.end and (k.end - k.start) > (h.end - h.start)
                   for k in kept[h.line]):
                continue
            if any(k.field == h.field and k.start == h.start and k.end == h.end for k in kept[h.line]):
                continue
            kept[h.line].append(h)
        for line, hs in kept.items():
            for h in sorted(hs, key=lambda h: h.start):
                self.hits[h.field].append(h)
                self.by_line[line].append(h)

    def dates(self, i):
        if i not in self._dates:
            self._dates[i] = find_dates(self.f[i])
        return self._dates[i]

    def amounts(self, i):
        if i not in self._amounts:
            self._amounts[i] = find_amounts(self.f[i], self.dates(i))
        return self._amounts[i]

    def next_lines(self, i, k):
        out = []
        for j in range(i + 1, self.n):
            if self.lines[j].strip():
                out.append(j)
                if len(out) >= k:
                    break
            elif j - i > k + 4:
                break
        return out


# ------------------------------------------------------------------ value lookup
def _same_line(doc, hit, vals):
    after = [v for v in vals if v.start >= hit.end]
    if not after:
        return None
    v = min(after, key=lambda v: v.start)
    for h in doc.by_line[hit.line]:
        if h is hit or h.field == hit.field:
            continue
        if hit.end <= h.start and h.end <= v.start and h.field not in ('terms',):
            return None
    return v


def _aligned(vals, hit, slack=6):
    best, best_score = None, None
    for v in vals:
        overlap = min(hit.end, v.end) - max(hit.start, v.start)
        if overlap > 0:
            score = overlap + 100
        else:
            gap = max(v.start - hit.end, hit.start - v.end)
            if gap > slack:
                continue
            score = -gap
        if best_score is None or score > best_score:
            best, best_score = v, score
    return best


def _below(doc, hit, finder, max_lines=2):
    for j in doc.next_lines(hit.line, max_lines):
        vals = finder(j)
        if vals:
            v = _aligned(vals, hit)
            return (v, j) if v else (None, None)
    return None, None


def _lookup(doc, hit, finder, allow_below=True):
    v = _same_line(doc, hit, finder(hit.line))
    if v:
        return v, hit.line, 'same_line'
    if hit.label.inline or not allow_below:
        return None, None, None
    v, j = _below(doc, hit, finder)
    if v:
        return v, j, 'below'
    return None, None, None


# ------------------------------------------------------------------ dates
def _date_vals(doc, i):
    return [Val(h.start, h.end, h) for h in doc.dates(i)]


def _resolve_order(doc, default_order, currency):
    dmy = mdy = 0
    slash = False
    for i in range(doc.n):
        for h in doc.dates(i):
            if h.kind in ('num', 'num2'):
                if '/' in doc.f[i][h.start:h.end]:
                    slash = True
                if set(h.cands) == {'DMY'}:
                    dmy += 1
                elif set(h.cands) == {'MDY'}:
                    mdy += 1
    if mdy > dmy:
        return 'MDY'
    if dmy:
        return 'DMY'
    if slash and currency == 'USD':
        return 'MDY'
    return default_order


def _find_dates(doc):
    found = {}
    # header rows: several date labels on one line, values in the same order on the next line
    for line, hs in doc.by_line.items():
        dh = [h for h in hs if h.field in DATE_FIELDS]
        if len(dh) >= 2 and any(not h.label.inline for h in dh) and not doc.dates(line):
            for j in doc.next_lines(line, 1):
                ds = doc.dates(j)
                if len(ds) == len(dh):
                    for h, d in zip(dh, ds):
                        _offer(found, h.field, d.get(doc.order), h.weight + 0.5, h.line, 'row')
    for field in DATE_FIELDS:
        for hit in doc.hits[field]:
            if hit.weight <= 3 and _WEAK_DATE_PREFIX.search(doc.f[hit.line][:hit.start]):
                continue
            v, j, how = _lookup(doc, hit, lambda i: _date_vals(doc, i))
            if v:
                _offer(found, field, v.value.get(doc.order), hit.weight, hit.line, how)
    return found


def _offer(found, field, d, weight, line, how):
    if d is None:
        return
    cur = found.get(field)
    if cur is None or weight > cur['weight'] or (weight == cur['weight'] and line < cur['line']):
        found[field] = {'date': d, 'weight': weight, 'line': line, 'how': how}


def _period_dates(doc):
    """Dates that are part of a range ('2026.09.01 - 2026.09.30'): never an issue date on their own."""
    out = set()
    for i in range(doc.n):
        ds = doc.dates(i)
        for a, b in zip(ds, ds[1:]):
            if re.fullmatch(r'\s*(?:-|to|till|until|bis|ig|–)\s*', doc.f[i][a.end:b.start]):
                out.add((i, a.start))
                out.add((i, b.start))
    return out


# ------------------------------------------------------------------ invoice number
_TOKEN = re.compile(r'(?<![\w/#.-])#?\s?([^\W_][\w/.-]*[^\W_]|\d)(?![\w/-])')
_ANY_TOKEN = re.compile(r'[^\s:]+')


def _number_vals(doc, i, short_ok=False):
    line = doc.lines[i]
    dates = doc.dates(i)
    out = []
    for m in _TOKEN.finditer(line):
        tok = m.group(1)
        if not re.search(r'\d', tok) or len(tok) > 40:
            continue
        if any(d.start <= m.start(1) < d.end or m.start(1) <= d.start < m.end(1) for d in dates):
            continue
        if re.fullmatch(r'\d{8}-\d-\d{2}', tok) or re.fullmatch(r'[A-Z]{2}\d{2}[A-Z0-9]{10,30}', tok):
            continue
        if not short_ok and re.fullmatch(r'\d{1,3}(?:[.,]\d+)?', tok) and len(re.sub(r'\D', '', tok)) <= 2:
            continue  # a stray small number in a table row below a label
        out.append(Val(m.start(1), m.end(1), tok.rstrip('.')))
    return out


def _find_number(doc):
    best = None
    for hit in doc.hits['number']:
        prefix = re.split(r'\s{2,}', doc.f[hit.line][:hit.start])[-1]
        if _BAD_NUMBER_PREFIX.search(prefix):
            continue
        if hit.label.title:
            m = _ANY_TOKEN.search(doc.lines[hit.line], hit.end)
            if not m or m.start() - hit.end > 30:
                continue
            tok = m.group(0).strip('#.,;')
            if not (re.search(r'\d', tok) and len(tok) >= 3) or doc.dates(hit.line) and any(
                    d.start <= m.start() < d.end for d in doc.dates(hit.line)):
                continue
            val, how = tok, 'title'
        else:
            v, j, how = _lookup(doc, hit, lambda i, h=hit: _number_vals(doc, i, short_ok=i == h.line))
            if not v:
                continue
            val = v.value
        conf = {10: 0.95, 9: 0.92}.get(hit.weight, 0.85 if hit.weight >= 7 else 0.75 if hit.weight >= 6 else 0.55)
        if how == 'below':
            conf -= 0.05
        cand = (hit.weight, -hit.line, val, conf, how)
        if best is None or cand[:2] > best[:2]:
            best = cand
    if best:
        return best[2], round(best[3], 2)
    # unlabelled: "No. 0042" / "# 0042" near the top
    for i in range(min(doc.n, max(15, doc.n // 3))):
        m = re.search(r'(?:^|\s)(?:no|nr|#)\.?\s*:?\s*([A-Za-z0-9][\w/-]*\d[\w/-]*)', doc.f[i])
        if m:
            return doc.lines[i][m.start(1):m.end(1)], 0.4
    return None, 0.0


# ------------------------------------------------------------------ total
def _find_total(doc):
    cands = []
    for hit in doc.hits['total']:
        amts = [a for a in doc.amounts(hit.line) if a.start >= hit.end and a.value != 0]
        how, line = 'same_line', hit.line
        if not amts and not hit.label.inline:
            for j in doc.next_lines(hit.line, 2):
                vals = [Val(a.start, a.end, a) for a in doc.amounts(j) if a.value != 0]
                if vals:
                    v = _aligned(vals, hit, slack=12)
                    if v:
                        amts, how, line = [v.value], 'below', j
                    break
        if not amts:
            continue
        # labels between the total label and the amounts belong to other cells
        nxt = [h.start for h in doc.by_line[hit.line] if h.start >= hit.end and h.field != 'total'
               and h.field != 'currency']
        if how == 'same_line' and nxt:
            amts = [a for a in amts if a.start < min(nxt)] or []
            if not amts:
                continue
        a = max(amts, key=lambda a: abs(a.value))
        lf = doc.f[hit.line]
        ctx = lf[max(0, hit.start - 14):(a.end if how == 'same_line' else len(lf))]
        if _NOT_GROSS.search(ctx) and not _GROSS.search(ctx):
            continue
        if abs(a.value) > Decimal('10000000000'):
            continue
        score = hit.weight * 10 + (4 if a.currency else 0) + 3 * hit.line / max(1, doc.n)
        cands.append((score, a, hit))
    if cands:
        score, a, hit = max(cands, key=lambda c: c[0])
        conf = 0.95 if hit.weight >= 9 else 0.85 if hit.weight >= 8 else 0.7 if hit.weight >= 5 else 0.5
        if not a.currency:
            conf -= 0.05
        return a, round(conf, 2)
    # unlabelled: the largest amount that carries a currency
    best = None
    for i in range(doc.n):
        if _NOT_GROSS.search(doc.f[i]) and not _GROSS.search(doc.f[i]):
            continue
        for a in doc.amounts(i):
            if a.currency and a.value != 0 and (best is None or abs(a.value) > abs(best.value)):
                best = a
    return (best, 0.4) if best else (None, 0.0)


def _doc_currency(doc, default):
    for hit in doc.hits['currency']:
        seg = doc.f[hit.line][hit.end:hit.end + 25]
        m = re.search(r'(?<![a-z])(huf|eur|usd|gbp|chf|pln|czk|ron|sek|nok|dkk|forint|euro|ft|€|\$|£)(?![a-z])', seg)
        if m:
            return CURRENCY_WORDS.get(m.group(1), default)
    counts = currency_mentions(doc.ftext)
    if counts:
        return max(counts.items(), key=lambda kv: kv[1])[0]
    return default


# ------------------------------------------------------------------ payment method / paid
def _classify_method(text):
    for code, rx in METHOD_VALUES:
        if rx.search(text):
            return code
    return None


def _find_method(doc):
    for hit in sorted(doc.hits['method'], key=lambda h: -h.weight):
        seg = doc.f[hit.line][hit.end:]
        seg = re.split(r'\s{3,}', seg.strip(' :'), maxsplit=1)[0] if seg.strip(' :') else ''
        m = _classify_method(seg) if seg else None
        if m:
            return m, 0.9
        for j in doc.next_lines(hit.line, 1):
            col = doc.f[j][max(0, hit.start - 4):hit.end + 22]
            m = _classify_method(col)
            if m:
                return m, 0.85
    strong = [
        ('direct_debit', r'csoportos\s*beszedesi\s*megbizas\w*|direct\s*debit'),
        ('card', r'paid\s*(?:with|by)\s*(?:visa|mastercard|card|amex)|card\s*ending|kartyaval\s*fizetve|'
                 r'bankkartyaval\s*fizetve|(?:visa|mastercard|maestro)\s*(?:-|\*|·|x){0,4}\s*\d{4}'),
        ('transfer', r'atutalassal|atutalas\s*utjan|kerjuk\s*(?:a\s*)?(?:szamla\s*)?(?:osszeget\s*)?(?:a\s*)?(?:fenti\s*)?'
                     r'bankszamla\w*|(?:bank|wire)\s*transfer|remit\s*(?:payment|to)|pay(?:ment)?\s*by\s*(?:ach|bacs|bank)|'
                     r'(?:per|durch|mittels)\s*(?:bank)?(?:ue|u)berweisung|bitte\s*(?:uberweisen|ueberweisen)|'
                     r'par\s*virement|tramite\s*bonifico'),
        ('paypal', r'paypal'),
    ]
    for code, rx in strong:
        if re.search(rx, doc.ftext):
            return code, 0.6
    return None, 0.0


def _paid_stamp(doc):
    for i, fl in enumerate(doc.f):
        for m in _PAID_STAMP.finditer(fl):
            if _PAID_NEG.search(fl[:m.start()]):
                continue
            amts = [a for a in doc.amounts(i) if a.start >= m.end()]
            if amts and all(a.value == 0 for a in amts):
                continue
            return True
    return False


def _terms_days(doc):
    for hit in doc.hits['terms']:
        seg = doc.f[hit.line][hit.end:hit.end + 40]
        m = re.search(r'(?:net\s*)?(\d{1,3})\s*(?:days?|nap|tage?|jours|giorni)', seg) or re.search(r'net\s*(\d{1,3})', seg)
        if m:
            return int(m.group(1))
    m = re.search(B + r'net\s*(\d{1,3})' + E, doc.ftext)
    if m and 0 < int(m.group(1)) <= 120:
        return int(m.group(1))
    return None


# ------------------------------------------------------------------ doc type
def _doc_type(doc):
    head = [doc.f[i] for i in range(min(doc.n, 30))]
    head_text = '\n'.join(head)
    for t in ('credit_note', 'proforma'):
        rx = dict(_DOC_TYPES)[t]
        for i, fl in enumerate(head[:20]):
            m = rx.search(fl)
            if m and (t == 'credit_note' or _title_like(fl, m)):
                return t
    rec, inv = dict(_DOC_TYPES)['receipt'], dict(_DOC_TYPES)['invoice']
    first = None
    for fl in head[:15]:
        mr, mi = rec.search(fl), inv.search(fl)
        if mr and _title_like(fl, mr) and not mi:
            first = first or 'receipt'
        elif mi and _title_like(fl, mi) and not mr:
            first = first or 'invoice'
        if first:
            break
    if first:
        return first
    if inv.search(head_text) or doc.hits['number']:
        return 'invoice'
    if rec.search(head_text):
        return 'receipt'
    return 'unknown'


def _title_like(fl, m):
    """The keyword is a heading: at the start of a cell, not inside a sentence."""
    before = re.split(r'\s{2,}', fl[:m.start()])[-1]
    after = fl[m.end():].strip()
    return not before.strip(' :-|') and (len(after) < 40 or re.match(r'\s{2,}|[:#\d(]', fl[m.end():] + ' '))


def invoice_score(doc, ex):
    s = 0
    if ex['doc_type'] in ('invoice', 'receipt', 'credit_note'):
        s += 1
    if ex['invoice_number']:
        s += 1
    if ex['amount'] is not None:
        s += 1
    if ex['issue_date'] or ex['due_date'] or ex['paid_date']:
        s += 1
    if ex['supplier_tax_id'] or S.find_tax_ids(doc.lines, doc.f):
        s += 1
    return s


# ------------------------------------------------------------------ supplier
class Own:
    """Your own company (the buyer): never the supplier."""

    def __init__(self, company):
        names = [company.get('name') or ''] + list(company.get('aliases') or [])
        self.keys = {S.core_key(n) for n in names if len(S.core_key(n)) >= 3}
        self.tax = {S.tax_core(t) for t in company.get('tax_ids') or [] if t}
        self.domains = {d.lower() for d in company.get('email_domains') or []}

    def matches(self, name):
        k = S.core_key(name)
        if not k:
            return False
        return any(k == o or (len(o) >= 5 and (' ' + o + ' ') in (' ' + k + ' ')) for o in self.keys)


def _segments(text, offset=0):
    """Split a line into cells separated by 2+ spaces or by ' - ', ' | ', ' · ' (letterheads): [(start, text)]."""
    out = []
    for m in re.finditer(r'\S(?:.*?\S)?(?=\s{2,}|\s[-|·•]\s|$)', text):
        out.append((offset + m.start(), m.group(0)))
    return out


def _clean_name(seg):
    s = seg.strip(' :;,|-')
    prefix = ''
    m = re.match(r'^([^:]{1,24}):\s*(.+)$', s)
    if m:
        prefix, s = m.group(1), m.group(2)
    s = re.split(r',\s*(?=\d{4}\b)|,\s*(?=H-\d{4})|\s+-\s+(?=\d)|;\s*', s)[0]
    parts = re.split(r',\s+', s)
    for i in range(len(parts) - 1):  # the shortest comma-prefix that ends in a legal form
        cand = ', '.join(parts[:i + 1])
        if S.LEGAL_END.search(fold(cand)):
            s = cand
            break
    return s.strip(' :;,|-'), fold(prefix).strip()


def _name_like(name):
    if not (2 <= len(name) <= 90):
        return False
    if sum(c.isalpha() for c in name) < 2:
        return False
    fn = fold(name)
    if _NOT_NAME.match(fn) or '@' in name or 'www.' in fn or 'http' in fn:
        return False
    if re.match(r'^(?:h-)?\d{4}\b', fn) and not S.LEGAL_END.search(fn):
        return False
    if re.fullmatch(r'[\d\s./-]+', name):
        return False
    words = fn.split()
    if len(words) > 12:
        return False
    return True


def _block_label_ok(doc, hit):
    fl = doc.f[hit.line]
    before = re.split(r'\s{2,}', fl[:hit.start])[-1]
    if before.strip(' :|-*') and not re.fullmatch(r'.*[\]):|]\s*', before):
        return False
    rest = fl[hit.end:]
    q = re.match(r'\s*(?:neve|name|adatai|details|information|info|megnevezese|address)(?![a-z])', rest)
    if q:
        rest = rest[q.end():]
    if not rest.strip() or re.match(r'\s*:', rest):
        return True
    # a column header: the next cell starts after a gap ("Eladó          Vevő")
    return bool(re.match(r'\s{2,}', rest)) or bool(re.match(r'\s*\(', rest))


def _region(doc, hit, block_hits):
    left = max(0, hit.start - 3)
    right = 10 ** 6
    for h in block_hits:
        if h.line == hit.line and h.start > hit.start:
            right = min(right, h.start - 1)
    bottom, blanks = hit.line, 0
    for j in range(hit.line + 1, min(doc.n, hit.line + 10)):
        seg = doc.lines[j][left:right]
        if not seg.strip():
            blanks += 1
            if blanks >= 2:
                break
            continue
        if any(h.line == j and left <= h.start < right for h in block_hits):
            break
        blanks = 0
        bottom = j
    return Region(hit.line, bottom, left, right)


def _region_name(doc, reg, hit):
    for j in range(reg.top, reg.bottom + 1):
        line = doc.lines[j]
        a = hit.end if j == reg.top else reg.left
        text = line[a:reg.right] if a < len(line) else ''
        if j == reg.top:
            text = re.sub(r'^\s*(?:neve|name|adatai|details|information|info|megnevezese)?\s*:?', '', text,
                          flags=re.I)
        for off, seg in _segments(text, a):
            if seg.rstrip().endswith(':'):
                continue  # a label cell such as "Név:"; the name is in the next cell
            name, prefix = _clean_name(seg)
            if prefix and _BANK_CONTEXT.search(prefix):
                continue
            if _name_like(name):
                return name, j, off
    return None, None, None


def _legal_segments(doc, skip):
    for i, line in enumerate(doc.lines):
        fl = doc.f[i]
        if _FOOTER.search(fl):
            continue
        for off, seg in _segments(line):
            name, prefix = _clean_name(seg)
            if prefix and (_BANK_CONTEXT.search(prefix) or _NOT_NAME.match(prefix + ' ')):
                if not re.match(r'^(?:nev|name|cegnev|company|elado|szallito|supplier|seller|from)', prefix):
                    continue
            if _BANK_CONTEXT.search(fl[max(0, off - 22):off]):
                continue
            if not (S.LEGAL_END.search(fold(name)) and _name_like(name)):
                continue
            if skip(i, off):
                continue
            yield i, off, name


def _find_supplier(doc, meta, own, registry):
    cands = []
    notes = []
    block_hits = [h for f in BLOCK_FIELDS for h in doc.hits[f] if _block_label_ok(doc, h)]
    seller_hits = [h for h in block_hits if h.field == 'seller']
    buyer_regs = [_region(doc, h, block_hits) for h in block_hits if h.field == 'buyer']
    seller_regs = []
    tax_ids = S.find_tax_ids(doc.lines, doc.f)

    def in_buyer(i, col):
        return any(r.contains(i, col) for r in buyer_regs)

    for h in seller_hits:
        reg = _region(doc, h, block_hits)
        seller_regs.append(reg)
        name, line, col = _region_name(doc, reg, h)
        if not name:
            continue
        if own.matches(name):
            notes.append('own_company_is_seller')
            continue
        cands.append({'name': name, 'conf': 0.86 if h.weight >= 9 else 0.8, 'how': 'label', 'line': line})

    sender_name, sender_addr, sender_domain = S.sender_parts((meta or {}).get('sender'))
    own_tax = own.tax

    if registry is not None:
        line_keys = [S.name_key(l) for l in doc.lines]
        for row, i, ak in registry.find_in_lines(line_keys):
            if _FOOTER.search(doc.f[i]):
                continue
            col = doc.f[i].find(ak.split()[0][:4]) if ak else 0
            if in_buyer(i, max(col, 0)) or own.matches(ak):
                continue
            in_seller = any(r.contains(i, max(col, 0)) for r in seller_regs)
            top = i < max(12, doc.n * 0.4)
            cands.append({'name': row['name'], 'conf': 0.97 if in_seller else 0.9 if top else 0.6,
                          'how': 'known', 'line': i, 'known': row})
        supplier_tax = [t for t in tax_ids if t[3] not in own_tax and not in_buyer(t[0], t[1])]
        row = registry.by_tax([t[3] for t in supplier_tax])
        if row:
            cands.append({'name': row['name'], 'conf': 0.96, 'how': 'known_tax', 'line': supplier_tax[0][0], 'known': row})
        row = registry.by_domain(sender_domain) if sender_domain not in own.domains else None
        if row:
            cands.append({'name': row['name'], 'conf': 0.8, 'how': 'known_domain', 'line': -1, 'known': row})

    for i, off, name in _legal_segments(doc, lambda i, off: in_buyer(i, off)):
        if own.matches(name):
            continue
        top = i < max(10, doc.n * 0.3)
        in_seller = any(r.contains(i, off) for r in seller_regs)
        cands.append({'name': name, 'conf': 0.82 if in_seller else 0.68 if top else 0.5, 'how': 'legal_form', 'line': i})

    if sender_domain and sender_domain not in own.domains:
        guess = S.sender_name_guess(sender_name)
        if guess and not own.matches(guess):
            in_text = S.core_key(guess) and (' ' + S.core_key(guess) + ' ') in (' ' + norm_key(doc.text) + ' ')
            cands.append({'name': guess, 'conf': 0.72 if in_text else 0.45, 'how': 'sender', 'line': -1})
        elif sender_domain not in S.PLATFORM_DOMAINS:
            guess = S.domain_name_guess(sender_domain)
            if guess:
                in_text = (' ' + guess.lower() + ' ') in (' ' + norm_key(doc.text) + ' ')
                cands.append({'name': guess, 'conf': 0.6 if in_text else 0.35, 'how': 'sender_domain', 'line': -1})

    # letterhead: first name-like line at the top that is not a title or label
    for i in range(min(doc.n, 6)):
        for off, seg in _segments(doc.lines[i]):
            name, prefix = _clean_name(seg)
            if prefix or in_buyer(i, off) or own.matches(name) or not _name_like(name):
                continue
            if any(h.line == i and h.start <= off + 2 for h in doc.by_line[i]):
                continue
            if any(rx.search(fold(name)) for _, rx in _DOC_TYPES):
                continue
            cands.append({'name': name, 'conf': 0.3, 'how': 'letterhead', 'line': i})
            break
        else:
            continue
        break

    if not cands:
        return None, notes, tax_ids
    # merge candidates naming the same company
    groups = {}
    for c in cands:
        k = S.core_key(c['known']['name'] if c.get('known') else c['name'])
        if not k:
            continue
        g = groups.setdefault(k, {'cands': [], 'conf': 0})
        g['cands'].append(c)
    for k in sorted(groups, key=len):
        toks = k.split()
        if len(toks[0]) < 4:
            continue
        longer = [o for o in groups if o != k and o.split()[:len(toks)] == toks]
        if len(longer) == 1:  # "nimbus" (logo) agrees with "nimbus web services emea" (legal name)
            groups[longer[0]]['cands'] += [dict(c, conf=min(c['conf'], 0.5)) for c in groups.pop(k)['cands']]
    for k, g in groups.items():
        best = max(g['cands'], key=lambda c: c['conf'])
        hows = {c['how'] for c in g['cands']}
        g['conf'] = min(0.99, best['conf'] + 0.05 * (len(hows) - 1))
        g['best'] = best
    if not groups:
        return None, notes, tax_ids
    g = max(groups.values(), key=lambda g: (g['conf'], -max(c['line'] for c in g['cands'])))
    best = g['best']
    known = next((c['known'] for c in g['cands'] if c.get('known')), None)
    raw = next((c['name'] for c in sorted(g['cands'], key=lambda c: -c['conf']) if c['how'] in ('label', 'legal_form')),
               best['name'])
    result = {'raw': raw, 'conf': round(g['conf'], 2), 'how': best['how'], 'known': known, 'line': best['line'],
              'sender_domain': sender_domain}
    # the supplier's tax number: the one printed nearest to its name, never ours or the buyer's
    sup_tax = [t for t in tax_ids if t[3] not in own_tax and not in_buyer(t[0], t[1])]
    if sup_tax and best['line'] >= 0:
        sup_tax.sort(key=lambda t: abs(t[0] - best['line']))
    result['tax_id'] = sup_tax[0][2] if sup_tax else None
    return result, notes, tax_ids


# ------------------------------------------------------------------ main entry
def extract(text, meta=None, company=None, registry=None, default_currency='HUF', date_order='DMY'):
    """Everything the bot can tell from the text. Values are plain JSON types (dates as ISO strings)."""
    doc = Doc(text)
    own = Own(company or {})
    hu = len(_HU_WORDS.findall(doc.ftext))
    en = len(_EN_WORDS.findall(doc.ftext))
    de = len(_DE_WORDS.findall(doc.ftext))
    language = 'hu' if hu >= max(en, de) and hu else 'de' if de > en else 'en' if en else None

    total, amount_conf = _find_total(doc)
    currency = (total.currency if total and total.currency else None) or _doc_currency(doc, default_currency)
    doc.order = _resolve_order(doc, date_order, currency)
    dates = _find_dates(doc)

    issue = dates.get('issue', {}).get('date')
    date_conf = {f: (0.95 if v['weight'] >= 9 else 0.85 if v['weight'] >= 6 else 0.6) for f, v in dates.items()}
    if issue is None and dates.get('paid'):
        issue = dates['paid']['date']
        date_conf['issue'] = 0.75
    if issue is None:
        periods = _period_dates(doc)
        for i in range(doc.n):
            ds = [d for d in doc.dates(i) if (i, d.start) not in periods]
            if ds:
                issue = ds[0].get(doc.order)
                date_conf['issue'] = 0.4
                break
    fulfilment = dates.get('fulfilment', {}).get('date')
    due = dates.get('due', {}).get('date')
    paid = dates.get('paid', {}).get('date')
    now = today()
    if paid and paid > now + timedelta(days=1):
        # a "payment date" in the future is a due date
        due = due or paid
        paid = None
    if due and issue and due < issue - timedelta(days=1):
        due = None
        date_conf.pop('due', None)
    terms = _terms_days(doc)

    number, number_conf = _find_number(doc)
    method, method_conf = _find_method(doc)
    doc_type = _doc_type(doc)
    stamp = _paid_stamp(doc) or doc_type == 'receipt'
    if paid is None and issue and stamp and (doc_type == 'receipt' or method in ('card', 'cash')):
        paid = issue  # a receipt or a slip marked paid at the till is dated the day it was paid
        date_conf['paid'] = 0.8

    sup, notes, tax_ids = _find_supplier(doc, meta, own, registry)
    supplier = supplier_raw = supplier_tax = None
    supplier_conf, supplier_how, supplier_known = 0.0, None, None
    if sup:
        supplier_raw = sup['raw']
        supplier_known = sup['known']['name'] if sup['known'] else None
        supplier = supplier_known or S.display_name(supplier_raw, hungarian=language == 'hu')
        if registry is not None and not supplier_known:
            row = registry.by_name(supplier_raw)
            if row:
                supplier = supplier_known = row['name']
        supplier_conf, supplier_how, supplier_tax = sup['conf'], sup['how'], sup['tax_id']

    amount = total.value if total else None
    if amount is not None and doc_type == 'credit_note' and amount > 0:
        amount = -amount
    if number and supplier_tax and S.tax_core(number) == S.tax_core(supplier_tax):
        number, number_conf = None, 0.0

    ex = {
        'doc_type': doc_type,
        'language': language,
        'supplier': supplier,
        'supplier_raw': supplier_raw,
        'supplier_known': supplier_known,
        'supplier_tax_id': supplier_tax,
        'supplier_how': supplier_how,
        'sender_domain': sup['sender_domain'] if sup else S.sender_parts((meta or {}).get('sender'))[2],
        'tax_ids': sorted({t[2] for t in tax_ids}),
        'invoice_number': number,
        'issue_date': iso(issue),
        'fulfilment_date': iso(fulfilment),
        'due_date': iso(due),
        'paid_date': iso(paid),
        'terms_days': terms,
        'payment_method': method,
        'paid_stamp': bool(stamp),
        'amount': dec_str(amount) if amount is not None else None,
        'currency': currency,
        'own_company_is_seller': 'own_company_is_seller' in notes and not supplier,
        'date_order': doc.order,
        'confidence': {
            'supplier': supplier_conf,
            'invoice_number': number_conf,
            'amount': amount_conf,
            'issue_date': date_conf.get('issue', 0.0),
            'due_date': date_conf.get('due', 0.0),
            'paid_date': date_conf.get('paid', 0.0),
            'payment_method': method_conf,
        },
    }
    ex['invoice_score'] = invoice_score(doc, ex)
    return ex
