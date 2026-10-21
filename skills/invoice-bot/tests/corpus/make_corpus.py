#!/usr/bin/env python3
"""Synthetic invoice PDF corpus for measuring an invoice field extractor:  python3 make_corpus.py --out DIR

Writes 28 PDFs plus DIR/truth.json (per file: doc_type, supplier_legal_name, invoice_number, amount, currency,
issue/fulfilment/due/paid dates, payment_method, paid_stamp, notes = the builder's docstring). Independent of the
extractor: each page is drawn with reportlab to imitate a real tool or document type (számlázz.hu, Billingo, utility
bills, Stripe, cloud providers, German Rechnung, till slips ...). The buyer is always HB Marketing Kft.; every seller
is fictional. Deterministic: no randomness, no current date. Needs only the standard library and reportlab.
"""
import argparse
import json
import os
from collections import namedtuple
from decimal import ROUND_HALF_UP, Decimal as D
from functools import partial

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# -------------------------------------------------------------------------------------------- fonts
FONT_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts", "~/.fonts", "~/.local/share/fonts", "/Library/Fonts"]
SANS = [("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"), ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf"),
        ("FreeSans.ttf", "FreeSansBold.ttf")]
FONT_CANDIDATES = {  # style -> (regular, bold) TTF files to try in order, then SANS
    "sans": SANS,
    "arial": [("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf"), ("Arial.ttf", "Arial Bold.ttf")],
    "serif": [("LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf"), ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf")],
    "office": [("Carlito-Regular.ttf", "Carlito-Bold.ttf"), ("Calibri.ttf", "Calibri Bold.ttf")],
    "mono": [("DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf"),
             ("LiberationMono-Regular.ttf", "LiberationMono-Bold.ttf")],
}
HELV, TIMES, COURIER = ("Helvetica", "Helvetica-Bold"), ("Times-Roman", "Times-Bold"), ("Courier", "Courier-Bold")
CORE_FONTS = dict(sans=HELV, arial=HELV, office=HELV, serif=TIMES, mono=COURIER)
TRANSLIT = str.maketrans("őűŐŰ", "öüÖÜ")  # the Hungarian letters missing from the core fonts' WinAnsi encoding


def setup_fonts():
    """Register TTF fonts that have Hungarian glyphs; fall back to the PDF core fonts when none is found."""
    found = {}
    for top in FONT_DIRS:
        for root, _, files in sorted(os.walk(os.path.expanduser(top))):
            for name in files:
                found.setdefault(name, os.path.join(root, name))
    fonts = {}
    for style, candidates in FONT_CANDIDATES.items():
        pair = next((p for p in candidates + SANS if p[0] in found and p[1] in found), None)
        if pair is None:
            return CORE_FONTS, True
        fonts[style] = tuple(f.rsplit(".", 1)[0] for f in pair)
        for name, f in zip(fonts[style], pair):
            pdfmetrics.registerFont(TTFont(name, found[f]))
    return fonts, False


FONTS, CORE_ONLY = setup_fonts()


def fix(s):
    """Text as printable with the active fonts: ő/ű become ö/ü only in the core-font fallback."""
    return s.translate(TRANSLIT) if CORE_ONLY else s


# ------------------------------------------------------------------------------------------- layout
BLACK, WHITE, GREY, LIGHT = colors.black, colors.white, colors.Color(.4, .4, .4), colors.Color(.92, .92, .92)
BLUE, GREEN, RED, TEAL = (colors.Color(*c) for c in ((.1, .3, .7), (.1, .55, .25), (.8, .1, .1), (0, .5, .5)))
NAVY, ORANGE, MINT, ICE = (colors.Color(*c) for c in ((.13, .18, .3), (.95, .55, 0), (.85, .93, .93), (.88, .92, 1)))


class Doc:
    """Thin layout layer over a reportlab canvas: x/y in mm from the TOP-left corner, y is the text baseline, align
    is "l", "r" or "c". Side-by-side blocks share baselines (same size and lead), so `pdftotext -layout` keeps them
    on the same text lines, as it does for real invoices."""

    def __init__(self, path, style="sans", size=A4):
        self.c = canvas.Canvas(path, pagesize=size, invariant=1)  # invariant: no timestamps -> identical bytes
        self.h, self.style = size[1] / mm, style

    def text(self, x, y, s, size=9, bold=False, align="l", color=BLACK, maxw=None):
        font, s = FONTS[self.style][bool(bold)], fix(str(s))
        while maxw and size > 5 and pdfmetrics.stringWidth(s, font, size) > maxw * mm:
            size -= 0.25  # shrink to fit a table cell
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        draw = {"l": self.c.drawString, "r": self.c.drawRightString, "c": self.c.drawCentredString}[align]
        draw(x * mm, (self.h - y) * mm, s)

    def lines(self, x, y, rows, size=9, lead=None, first_bold=False, **kw):
        """A block of lines; returns the y of the line after it."""
        lead = lead or size * 0.5
        for i, s in enumerate(rows):
            self.text(x, y + i * lead, s, size, first_bold and i == 0, **kw)
        return y + len(rows) * lead

    def kv(self, x, y, pairs, size=9, dx=35, vx=None, vbold=False, **kw):
        """Label/value pairs, one per line: the value at x+dx, or right-aligned at vx. Returns the next y."""
        for i, (k, v) in enumerate(pairs):
            self.text(x, y + i * size * 0.5, k, size, **kw)
            self.text(vx or x + dx, y + i * size * 0.5, v, size, vbold, "r" if vx else "l", **kw)
        return y + len(pairs) * size * 0.5

    def blocks(self, y, *cols, size=9, tsize=None, tcolor=BLACK, xs=(15, 110)):
        """Titled address blocks side by side at xs (seller / buyer): cols = (title, lines), ...; name in bold."""
        for x, (title, rows) in zip(xs, cols):
            self.text(x, y, title, tsize or size, True, color=tcolor)
            self.lines(x, y + size * 0.5, rows, size, first_bold=True)

    def head(self, title, sub, x=195, y=20, size=18, align="r", color=BLACK):
        """Document title with a smaller line (usually the number) 7 mm below it."""
        self.text(x, y, title, size, True, align, color)
        self.text(x, y + 7, sub, 10, align=align, color=color)

    def table(self, x, y, spec, rows, size=8, lead=5.5, fill=LIGHT, grid=False):
        """spec = "Title:width[l|r|c]|..." (mm); shaded header row at y. Returns the y just below the table."""
        cols = [(t, float(w.rstrip("lrc")), w[-1] if w[-1] in "lrc" else "l")
                for t, w in (c.rsplit(":", 1) for c in spec.split("|"))]
        width = sum(w for _, w, _ in cols)
        if fill:
            self.rect(x, y - lead + 1.8, width, lead, fill)
        for r, row in enumerate([[t for t, _, _ in cols]] + [list(rw) for rw in rows]):
            cx, yy = x, y + r * lead
            for (_, w, al), cell in zip(cols, row):
                tx = {"l": cx + 1.2, "r": cx + w - 1.2, "c": cx + w / 2}[al]
                self.text(tx, yy, cell, size, r == 0, al, maxw=w - 2.4)
                cx += w
            if r == 0 or grid:
                self.hline(yy + 1.8, x, x + width)
        return y + len(rows) * lead + 3

    def totals(self, x, y, pairs, final, size=9.5, big=12, xr=195, rule=False):
        """Summary lines right-aligned at xr, then the bold grand total; returns the y below it."""
        y = self.kv(x, y, pairs, size, vx=xr)
        if rule:
            self.hline(y - 2.5, x, xr)
        return self.kv(x, y + 2, [final], big, vx=xr, vbold=True)

    def hline(self, y, x1=15, x2=195, width=0.5, color=GREY):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x1 * mm, (self.h - y) * mm, x2 * mm, (self.h - y) * mm)

    def rect(self, x, y, w, h, fill=None, stroke=None):
        """Rectangle with its TOP edge at y."""
        self.c.setFillColor(fill or WHITE)
        self.c.setStrokeColor(stroke or BLACK)
        self.c.setLineWidth(0.6)
        self.c.rect(x * mm, (self.h - y - h) * mm, w * mm, h * mm, stroke=int(bool(stroke)), fill=int(bool(fill)))

    def stamp(self, x, y, s, size=22, angle=0, color=GREEN):
        """Rubber-stamp style framed text centred on (x, y), optionally rotated."""
        c, font, s = self.c, FONTS[self.style][1], fix(s)
        w = pdfmetrics.stringWidth(s, font, size)
        c.saveState()
        c.translate(x * mm, (self.h - y) * mm)
        c.rotate(angle)
        c.setFont(font, size)
        c.setFillColor(color)
        c.setStrokeColor(color)
        c.setLineWidth(2)
        c.drawCentredString(0, 0, s)
        c.roundRect(-w / 2 - 8, -size * 0.35, w + 16, size * 1.2, 4)
        c.restoreState()


# --------------------------------------------------------------------------------------- formatting
EN_M = "January February March April May June July August September October November December".split()
HU_M = "január február március április május június július augusztus szeptember október november december".split()


def dt(iso, style="hu"):
    """Print an ISO date the way a given locale or tool does."""
    y, m, d = (int(p) for p in iso.split("-"))
    mon = EN_M[m - 1]
    return {"hu": f"{y}.{m:02}.{d:02}.", "hu_sp": f"{y}. {m:02}. {d:02}.", "hu_long": f"{y}. {HU_M[m - 1]} {d}.",
            "iso": iso, "us": f"{m:02}/{d:02}/{y}", "gb": f"{d:02}/{m:02}/{y}", "de": f"{d:02}.{m:02}.{y}",
            "nl": f"{d:02}-{m:02}-{y}", "cz": f"{d}. {m}. {y}", "long": f"{mon} {d}, {y}",
            "dmy": f"{d} {mon[:3]} {y}"}[style]


def q(v, places=2):
    return D(str(v)).quantize(D(1).scaleb(-places), ROUND_HALF_UP)


def money(v, places=2, th=",", dp="."):
    """money(1587.5) -> '1,587.50'; th / dp set the thousands separator and the decimal mark."""
    return f"{q(v, places):,.{places}f}".replace(",", "\0").replace(".", dp).replace("\0", th)


huf = partial(money, places=0, th=" ")  # forint, no decimals: 127 000
hun = partial(money, th=".", dp=",")  # Hungarian / German decimals: 1.587,50


def ft(v):
    return f"{huf(v)} Ft"


def pct(rate):  # 27 -> "27%"; exemption codes such as "AAM" stay as they are
    return f"{rate}%" if isinstance(rate, int) else rate


Row = namedtuple("Row", "desc qty unit price rate net vat gross")


def calc(items, places=0):
    """items: (description, qty, unit, net unit price, VAT % or exemption code). VAT is rounded per line (forint:
    to whole numbers). Returns rows, net, vat, gross."""
    rows = []
    for desc, qty, unit, price, rate in items:
        net = q(D(str(qty)) * D(str(price)), places)
        vat = q(net * (rate if isinstance(rate, int) else 0) / 100, places)
        rows.append(Row(desc, qty, unit, D(str(price)), rate, net, vat, net + vat))
    return (rows, *(sum((getattr(r, k) for r in rows), D(0)) for k in ("net", "vat", "gross")))


def row6(r, fmt=huf):
    """Megnevezés | Menny. | Egységár | ÁFA | Nettó | Bruttó."""
    return [r.desc, f"{r.qty} {r.unit}".strip(), fmt(r.price), pct(r.rate), fmt(r.net), fmt(r.gross)]


# ------------------------------------------------------------------------------------- buyer, truth
B_NAME, B_STREET, B_CITY = "HB Marketing Kft.", "Bécsi út 100.", "1037 Budapest"
B_TAX, B_EU, B_ADDR = "12345678-2-41", "HU12345678", "1037 Budapest, Bécsi út 100."
BUYER_HU = [B_NAME, B_ADDR, f"Adószám: {B_TAX}", f"Közösségi adószám: {B_EU}"]
BUYER_EN = [B_NAME, B_STREET, B_CITY, "Hungary", f"VAT ID: {B_EU}"]
CASES = []


def case(filename, style="sans", size=A4):
    """Register a builder: fn(doc) draws one document and returns its truth(); its docstring becomes the notes."""
    def register(fn):
        CASES.append((filename, style, size, fn))
        return fn
    return register


def truth(doc_type, supplier, number, amount, currency, issue, fulfil=None, due=None, paid=None, method=None,
          stamp=False):
    return dict(doc_type=doc_type, supplier_legal_name=fix(supplier), invoice_number=number, amount=f"{q(amount):.2f}",
                currency=currency, issue_date=issue, fulfilment_date=fulfil, due_date=due, paid_date=paid,
                payment_method=method, paid_stamp=stamp)


# ======================================================================================== Hungarian
KT_SELLER = ["Kovács és Társa Kft.", "1134 Budapest, Lehel utca 27.", "Adószám: 24681353-2-41",
             "Bankszámlaszám: 11773016-01234567-00000008"]
KT_ITEMS = [("Weboldal karbantartás, 2026. szeptember", 1, "hó", 60000, 27),
            ("SEO audit és jelentés", 1, "db", 40000, 27)]


def szamlazz_like(d, title, number, issue, fulfil, due, items, ref=""):
    """számlázz.hu-like layout, shared by invoice 01 and its storno 05 (same issuer, same software)."""
    rows, net, vat, gross = calc(items)
    d.text(15, 20, "K&T", 22, True, color=BLUE)
    d.text(36, 20, "webstúdió", 11, color=BLUE)
    d.text(195, 18, title, 20, True, "r")
    d.text(195, 26, f"Számla sorszáma: {number}", 10, True, "r")
    d.text(195, 31.5, ref, 8.5, align="r")
    d.blocks(44, ("Eladó", KT_SELLER), ("Vevő", BUYER_HU), tsize=10)
    d.rect(15, 72, 180, 15, LIGHT)
    heads = ["Fizetési mód", "Teljesítés dátuma", "Számla kelte", "Fizetési határidő"]
    for i, (k, v) in enumerate(zip(heads, ["Átutalás", dt(fulfil), dt(issue), dt(due)])):
        d.text(17 + i * 45, 78, k, 8.5, True)
        d.text(17 + i * 45, 84, v)  # values on the row below the labels
    y = d.table(15, 100, "Megnevezés:64|Menny.:15r|Nettó egységár:23r|Nettó ár:20r|ÁFA:12r|ÁFA érték:20r|Bruttó ár:26r",
                [[r.desc, f"{r.qty} {r.unit}", huf(r.price), huf(r.net), pct(r.rate), huf(r.vat), huf(r.gross)]
                 for r in rows])
    d.hline(y - 1.5, width=1, color=BLACK)
    d.text(16.2, y + 3, "Összesen:", 9, True)
    for xr, v in ((135.8, net), (167.8, vat), (193.8, gross)):  # under Nettó ár, ÁFA érték and Bruttó ár
        d.text(xr, y + 3, huf(v), 9, True, "r")
    y = d.table(95, y + 16, "ÁFA kulcs:25|Nettó ár:25r|ÁFA érték:25r|Bruttó ár:25r",
                [["27%", huf(net), huf(vat), huf(gross)]])
    d.text(195, y + 10, f"Fizetendő: {ft(gross)}", 15, True, "r")
    d.text(105, 287, "Készült a SzámlaPont online számlázó programmal · 1/1. oldal", 7, align="c", color=GREY)
    return gross


@case("01_szamlazz_transfer.pdf")
def c01(d):
    """számlázz.hu-like: dates on the row below their labels; 'Összesen' holds net, VAT, gross; logo is not the name."""
    num, iss, due = "E-KVT-2026-118", "2026-09-15", "2026-09-23"
    gross = szamlazz_like(d, "Számla", num, iss, iss, due, KT_ITEMS)
    return truth("invoice", "Kovács és Társa Kft.", num, gross, "HUF", iss, iss, due, method="transfer")


@case("02_billingo_card.pdf")
def c02(d):
    """Billingo-like: '2026. 09. 15.' dates, seller labelled 'Szállító:'; card, but no 'paid' wording on the page."""
    num, iss = "FPS-2026-0042", "2026-09-15"
    rows, net, vat, gross = calc([("Felhőpont Pro előfizetés – havidíj", 1, "hónap", 36000, 27)])
    seller = ["Felhőpont Szoftver Kft.", "1117 Budapest, Infopark sétány 3.", "Adószám: 26543217-2-43",
              "Cégjegyzékszám: 01-09-345678", "Bankszámlaszám: 12010006-00123456-00100006"]
    d.text(15, 22, "felhőpont", 20, True, color=TEAL)
    d.head("SZÁMLA", f"Számlaszám: {num}", y=18)
    d.blocks(40, ("Szállító:", seller), ("Vevő:", [B_NAME, B_CITY, B_STREET, f"Adószám: {B_TAX}",
                                                   f"EU adószám: {B_EU}"]), tsize=8.5, tcolor=GREY)
    when = dt(iss, "hu_sp")
    d.kv(15, 76, [("Kiállítás dátuma:", when), ("Teljesítés dátuma:", when), ("Fizetési határidő:", when)], dx=34)
    d.kv(110, 76, [("Fizetési mód:", "Bankkártya"), ("Pénznem:", "HUF")], dx=26)
    y = d.table(15, 100, "Tétel:72|Mennyiség:20r|Nettó egységár:26r|ÁFA:12r|Nettó:24r|Bruttó:26r",
                [[r.desc, f"{r.qty} {r.unit}", ft(r.price), pct(r.rate), ft(r.net), ft(r.gross)] for r in rows]
                + [["Időszak: 2026.09.15. – 2026.10.14."]], 8.5, 6)
    d.totals(125, y + 6, [("Nettó összeg:", ft(net)), ("ÁFA (27%):", ft(vat))], ("Végösszeg:", ft(gross)), rule=True)
    return truth("invoice", "Felhőpont Szoftver Kft.", num, gross, "HUF", iss, iss, iss, method="card")


@case("03_ev_alanyi_adomentes.pdf", "office")
def c03(d):
    """e.v. sole trader, AAM (no VAT); Google Ads, Facebook, 'Google Ireland Ltd.' in items/notes are not the seller."""
    num, iss, ful, due = "SZP-2026-014", "2026-10-01", "2026-09-30", "2026-10-09"
    rows, net, vat, gross = calc([("Google Ads kampánykezelés – 2026. szeptember", 1, "hó", 200000, "AAM"),
                                  ("Facebook hirdetések kezelése és havi riport", 1, "hó", 150000, "AAM")])
    d.head("SZÁMLA", f"Számla sorszáma: {num}", 105, 20, 20, "c")
    seller = [("Név:", "Szabó Péter e.v."), ("Cím:", "2100 Gödöllő, Fenyves utca 12."), ("Adószám:", "68521341-1-33"),
              ("Nyilv. szám:", "54321987"), ("Bankszámla:", "11600006-00000000-87654323")]
    buyer = [("Név:", B_NAME), ("Cím:", B_ADDR), ("Adószám:", B_TAX), ("Közösségi adószám:", B_EU)]
    for i, (title, pairs) in enumerate([("Eladó", seller), ("Vevő", buyer)]):
        d.rect(15 + i * 92, 33, 88, 37, stroke=GREY)
        d.text(18 + i * 92, 39, title, 10, True)
        d.kv(18 + i * 92, 45, pairs, dx=30)
    boxes = [("Számla kelte", dt(iss)), ("Teljesítés dátuma", dt(ful)), ("Fizetési határidő", dt(due)),
             ("Fizetési mód", "Átutalás"), ("Pénznem", "HUF")]
    for i, (k, v) in enumerate(boxes):  # label above value
        d.rect(15 + i * 36, 74, 36, 14, stroke=GREY)
        d.text(17 + i * 36, 79, k, 7.5, color=GREY)
        d.text(17 + i * 36, 85, v, 10, True)
    spec = "Megnevezés:70|Menny.:14r|Egység:14|Nettó egységár:24r|ÁFA:12c|Nettó érték:22r|Bruttó érték:24r"
    y = d.table(15, 100, spec, [[r.desc, r.qty, r.unit, huf(r.price), r.rate, huf(r.net), huf(r.gross)] for r in rows],
                8.5, 6)
    y = d.totals(110, y + 6, [("Nettó érték összesen:", ft(net)), ("ÁFA összesen:", ft(vat))],
                 ("Fizetendő összesen:", ft(gross)))
    d.lines(15, y + 8, ["ÁFA: AAM – alanyi adómentes. Az eladó az Áfa tv. XIII. fejezete szerinti alanyi "
                        "adómentességet alkalmazza.", "A hirdetési díjakat a Google Ireland Ltd. és a Meta Platforms "
                        "Ireland Ltd. közvetlenül számlázza a Megrendelőnek."], 8.5)
    return truth("invoice", "Szabó Péter e.v.", num, gross, "HUF", iss, ful, due, method="transfer")


@case("04_telecom_direct_debit.pdf", "arial")
def c04(d):
    """Telecom bill: unlabelled buyer window address first; '18.990 Ft' dot grouping; direct debit; billing period."""
    num, iss, ful, due = "KN-2609-4471825", "2026-10-03", "2026-09-30", "2026-10-20"
    rows, net, vat, gross = calc([("Üzleti Net 1000 internet", 1, "hó", 11016, 27),
                                  ("Üzleti mobil flotta (3 SIM)", 1, "hó", 3937, 27)])
    dot, period = (lambda v: f"{huf(v, th='.')} Ft"), f"{dt('2026-09-01')} – {dt(ful)}"
    d.text(15, 20, "kristálynet", 22, True, color=BLUE)
    d.text(15, 26, "Üzleti ügyfélszolgálat: 1414 · www.kristalynet.hu", 8, color=GREY)
    d.text(195, 18, "Számla", 16, True, "r")
    d.kv(125, 25, [("Számla sorszáma:", num), ("Ügyfélazonosító:", "7001234567"), ("Számlázási időszak:", period)],
         8, vx=195)
    d.lines(20, 51, [B_NAME, B_STREET, B_CITY], 10)  # envelope window address
    d.rect(115, 44, 80, 25, LIGHT)
    d.kv(118, 51, [("Fizetendő összeg:", dot(gross))], 12, vx=192, vbold=True)
    d.kv(118, 58, [("Fizetési határidő:", dt(due)), ("Fizetési mód:", "Csoportos beszedési megbízás")], 8.5, vx=192)
    d.blocks(82, ("Szolgáltató", ["Kristálynet Távközlési Zrt.", "1097 Budapest, Könyves Kálmán krt. 40.",
                                  "Adószám: 12121216-2-44", "Cégjegyzékszám: 01-10-048888"]),
             ("Vevő (Előfizető)", BUYER_HU), size=8.5)
    d.kv(15, 110, [("Számla kelte:", dt(iss)), ("Teljesítés dátuma:", dt(ful))], 8.5, dx=30)
    d.text(15, 124, "Számlarészletező", 11, True)
    y = d.table(15, 132, "Szolgáltatás:62|Időszak:38|Nettó díj:20r|ÁFA:12r|ÁFA összeg:22r|Bruttó díj:26r",
                [[r.desc, period, dot(r.net), pct(r.rate), dot(r.vat), dot(r.gross)] for r in rows])
    d.text(16.2, y + 2, "Összesen", 9, True)
    for xr, v in ((133.8, net), (167.8, vat), (193.8, gross)):
        d.text(xr, y + 2, dot(v), 9, True, "r")
    d.lines(15, y + 14, [f"A számla összegét csoportos beszedési megbízással {dt(due)[:-1]}-án terheljük "
                         "bankszámláján, kérjük, ne utalja át.", "Hibabejelentés: 1414 · www.kristalynet.hu"], 8)
    return truth("invoice", "Kristálynet Távközlési Zrt.", num, gross, "HUF", iss, ful, due, method="direct_debit")


@case("05_sztorno_credit_note.pdf")
def c05(d):
    """Storno of 01: all amounts negative; 'Eredeti számla: E-KVT-2026-118' is the original, not this number."""
    num, iss, ful = "E-KVT-2026-131", "2026-09-29", "2026-09-15"
    items = [(desc, -qty, unit, price, rate) for desc, qty, unit, price, rate in KT_ITEMS]
    gross = szamlazz_like(d, "Sztornó számla", num, iss, ful, iss, items,
                          "Eredeti számla: E-KVT-2026-118 (kelte: 2026.09.15.)")
    return truth("credit_note", "Kovács és Társa Kft.", num, gross, "HUF", iss, ful, iss, method="transfer")


@case("06_dijbekero_proforma.pdf")
def c06(d):
    """Díjbekérő (payment request / proforma), explicitly 'nem számla'; no fulfilment date."""
    num, iss, due = "DB-2026-0057", "2026-09-24", "2026-10-01"
    rows, net, vat, gross = calc([("Tárhely – Business csomag, 12 hónap", 1, "év", 79900, 27),
                                  (".hu domain megújítás, 1 év", 1, "db", 4990, 27)])
    seller = ["Tárhelyfarm Kft.", "6720 Szeged, Kárász utca 9.", "Adószám: 25369142-2-06",
              "Bankszámlaszám: 10402805-50526789-12341007", "E-mail: penzugy@tarhelyfarm.hu"]
    d.head("DÍJBEKÉRŐ", f"Sorszám: {num}", 105, 22, 22, "c")
    d.text(105, 35, "Ez a dokumentum nem számla.", 8, align="c", color=GREY)
    d.blocks(48, ("Eladó:", seller), ("Vevő:", BUYER_HU))
    for x, s in ((15, f"Kelt: {dt(iss)}"), (75, f"Fizetési határidő: {dt(due)}"), (145, "Fizetési mód: Átutalás")):
        d.text(x, 84, s)
    y = d.table(15, 96, "Megnevezés:70|Menny.:16r|Egységár:22r|Nettó:22r|ÁFA %:14r|Bruttó:36r",
                [[r.desc, f"{r.qty} {r.unit}", huf(r.price), huf(r.net), r.rate, huf(r.gross)] for r in rows], 8.5, 6)
    y = d.totals(120, y + 6, [("Nettó összesen:", ft(net)), ("ÁFA 27%:", ft(vat))], ("Fizetendő:", ft(gross)), big=13)
    d.lines(15, y + 10, [f"Kérjük, az utalás közleményében tüntesse fel a díjbekérő sorszámát: {num}",
                         "A díjbekérő nem minősül számlának, áfa levonására nem jogosít."], 8.5)
    return truth("proforma", "Tárhelyfarm Kft.", num, gross, "HUF", iss, None, due, method="transfer")


@case("07_vevo_first.pdf", "serif")
def c07(d):
    """Buyer (Vevő) block on the LEFT, seller (Eladó) on the right; long-form 'Kelt: Budapest, 2026. szeptember 22.'."""
    num, iss, ful, due = "LF-2026-0093", "2026-09-22", "2026-09-20", "2026-10-06"
    rows, net, vat, gross = calc([("Termékfotózás stúdióban (40 termék)", 1, "alk.", 180000, 27),
                                  ("Képretusálás és vágás", 40, "db", 1500, 27)])
    seller = ["Lencse Fotóstúdió Bt.", "1065 Budapest, Nagymező utca 21.", "Adószám: 22334457-2-42",
              "Bankszámlaszám: 10918001-00000068-12340008"]
    d.head("SZÁMLA", f"Sorszám: {num}", 105, 22, 22, "c")
    d.blocks(44, ("Vevő", BUYER_HU), ("Eladó", seller), size=10, tsize=11)
    d.hline(73)
    d.kv(15, 80, [("Számla kelte:", dt(iss)), ("Teljesítés dátuma:", dt(ful))], 10, dx=36)
    d.kv(110, 80, [("Fizetési határidő:", dt(due)), ("Fizetési mód:", "Átutalás")], 10, dx=36)
    y = d.table(15, 100, "Megnevezés:74|Mennyiség:22r|Egységár:22r|ÁFA:14r|Nettó érték:22r|Bruttó érték:26r",
                [row6(r) for r in rows], 9, 6.5, grid=True)
    y = d.totals(115, y + 6, [("Nettó összesen:", ft(net)), ("ÁFA összesen:", ft(vat))],
                 ("Fizetendő végösszeg:", ft(gross)), 10)
    d.text(15, y + 14, f"Kelt: Budapest, {dt(iss, 'hu_long')}", 10)
    return truth("invoice", "Lencse Fotóstúdió Bt.", num, gross, "HUF", iss, ful, due, method="transfer")


@case("08_fizetve_stamp.pdf")
def c08(d):
    """'FIZETVE' stamp, 'Kiegyenlítve', 'Fizetés dátuma' before the issue date; seller name in a dark header band."""
    num, iss, paid = "BN-2026-00318", "2026-09-14", "2026-09-12"
    rows, net, vat, gross = calc([("Szórólap A5, 4+4 szín, 135 g, 2000 db", 1, "tétel", 64000, 27),
                                  ("Roll-up 85×200 cm, táskával", 2, "db", 17500, 27)])
    d.rect(0, 0, 210, 32, NAVY)
    d.text(15, 15, "Betűvető Nyomda Kft.", 18, True, color=WHITE)
    d.text(15, 22, "nyomda · grafika · dekoráció", 9, color=WHITE)
    d.head("SZÁMLA", f"Sorszám: {num}", y=15, color=WHITE)
    d.text(15, 39, "1132 Budapest, Váci út 18. · Adószám: 13579241-2-41 · Bankszámla: 12001008-00123456-00100006",
           8, color=GREY)
    d.blocks(51.25, ("Vevő", BUYER_HU), size=9.5, tsize=9, tcolor=GREY)
    d.kv(120, 56, [("Számla kelte:", dt(iss)), ("Teljesítés dátuma:", dt(iss)), ("Fizetési határidő:", dt(iss)),
                   ("Fizetési mód:", "Átutalás"), ("Fizetés dátuma:", dt(paid))], 9.5, vx=195)
    y = d.table(15, 92, "Megnevezés:80|Menny.:20r|Nettó egységár:26r|ÁFA:14r|Bruttó:40r",
                [[r.desc, f"{r.qty} {r.unit}", huf(r.price), pct(r.rate), huf(r.gross)] for r in rows], 8.5, 6)
    y = d.totals(120, y + 6, [("Nettó összesen:", ft(net)), ("ÁFA 27%:", ft(vat))], ("Végösszeg:", ft(gross)))
    d.stamp(160, y + 14, "FIZETVE", 26)  # below the totals: a big stamp beside them would split their text lines
    d.text(160, y + 24, f"Kiegyenlítve: {dt(paid)}", 9, True, "c", GREEN)
    d.text(15, y + 38, "A számla végösszege átutalással kiegyenlítésre került. Köszönjük a megrendelést!", 8.5)
    return truth("invoice", "Betűvető Nyomda Kft.", num, gross, "HUF", iss, iss, iss, paid, "transfer", True)


@case("09_eur_hungarian.pdf", "arial")
def c09(d):
    """Hungarian invoice in EUR ('1.587,50 EUR'); 'ÁFA forintban', the HUF total and the rate are not the total."""
    num, iss, due, rate = "AP-2026-0187", "2026-09-30", "2026-10-15", D("395.12")
    rows, net, vat, gross = calc([("Looker Studio riport fejlesztés", 10, "óra", "65.00", 27),
                                  ("Adatpiac karbantartás, 2026. szeptember", 1, "hó", "600.00", 27)], 2)
    seller = ["Adatpont Analitika Kft.", "2040 Budaörs, Szabadság út 117.", "Adószám: 27183641-2-13",
              "EU adószám: HU27183641", "IBAN: HU93 1160 0006 0000 0000 1234 5676"]
    d.head("Számla", f"Számlaszám: {num}", 15, 22, 20, "l")
    d.text(195, 22, "ADATPONT", 16, True, "r", TEAL)
    d.text(195, 27, "analitika", 9, align="r", color=GREY)
    d.blocks(44, ("Eladó", seller), ("Vevő", BUYER_HU), tcolor=GREY)
    d.kv(15, 80, [("Számla kelte:", dt(iss)), ("Teljesítés dátuma:", dt(iss)), ("Fizetési határidő:", dt(due))], dx=32)
    d.kv(110, 80, [("Fizetési mód:", "Átutalás"), ("Pénznem:", "EUR"),
                   ("Árfolyam:", f"1 EUR = {money(rate, 2, ' ', ',')} HUF (MNB, {dt(iss)})")], dx=24)
    y = d.table(15, 102, "Megnevezés:72|Menny.:18r|Egységár:22r|ÁFA:12r|Nettó:26r|Bruttó:30r",
                [row6(r, hun) for r in rows], 8.5, 6)
    y = d.totals(110, y + 6, [("Nettó összesen:", f"{hun(net)} EUR"), ("ÁFA (27%):", f"{hun(vat)} EUR")],
                 ("Bruttó végösszeg:", f"{hun(gross)} EUR"))
    d.kv(110, y + 4, [("ÁFA forintban:", ft(vat * rate)), ("Végösszeg forintban (tájékoztató):", ft(gross * rate))],
         8.5, vx=195, color=GREY)
    return truth("invoice", "Adatpont Analitika Kft.", num, gross, "EUR", iss, iss, due, method="transfer")


# ========================================================================================== English
def stripe_like(d, title, logo, seller, meta, headline, item, totals):
    """Stripe-hosted invoice / receipt layout (Letter): no colons; seller and 'Bill to' side by side."""
    d.text(18, 24, title, 20, True)
    d.text(197, 24, logo, 12, True, "r", BLUE)
    d.kv(18, 36, meta, dx=32)
    y = 42 + 4.5 * len(meta)
    d.lines(18, y, seller, first_bold=True)
    d.lines(85, y, ["Bill to", B_NAME, B_STREET, B_CITY, "Hungary", f"HU VAT {B_EU}"], first_bold=True)
    d.text(18, y + 36, headline, 15, True)
    y = d.table(18, y + 52, "Description:104|Qty:20r|Unit price:28r|Amount:27r",
                [[item[0], "1", item[1], item[1]], ["Sep 15 – Oct 15, 2026"]], 9, 5.5, fill=None)
    d.kv(112, y + 4, totals, vx=197)


@case("10_stripe_invoice.pdf", "arial", letter)
def c10(d):
    """Stripe-like invoice: no colons, US long dates, '$45.00 due September 15, 2026'; no payment method stated."""
    num, iss, amt = "7F3C2A91-0004", "2026-09-15", D("45.00")
    seller = ["Pixelcraft, Inc.", "548 Market Street, PMB 72296", "San Francisco, California 94104-5401",
              "United States", "billing@pixelcraft.io"]
    stripe_like(d, "Invoice", "PIXELCRAFT", seller,
                [("Invoice number", num), ("Date of issue", dt(iss, "long")), ("Date due", dt(iss, "long"))],
                f"${amt} due {dt(iss, 'long')}", ("Pixelcraft Team plan", f"${amt}"),
                [("Subtotal", f"${amt}"), ("Total", f"${amt}"), ("Amount due", f"${amt} USD")])
    d.text(18, 100, "Pay online: https://pay.pixelcraft.io/i/7F3C2A91", color=BLUE)
    d.text(18, 266, f"{num} · ${amt} due {dt(iss, 'long')} · Page 1 of 1", 8, color=GREY)
    return truth("invoice", "Pixelcraft, Inc.", num, amt, "USD", iss, None, iss)


@case("11_stripe_receipt.pdf", "arial", letter)
def c11(d):
    """Stripe-like receipt: 'Invoice number' (truth) and 'Receipt number'; 'Date paid' is the only date."""
    num, iss, amt = "B4E8D2C6-0012", "2026-09-15", D("45.00")
    seller = ["Notewise Labs, Inc.", "2261 Market Street #4021", "San Francisco, California 94114", "United States",
              "support@notewise.app"]
    stripe_like(d, "Receipt", "notewise", seller,
                [("Invoice number", num), ("Receipt number", "2183-4471"), ("Date paid", dt(iss, "long")),
                 ("Payment method", "Visa – 4242")], f"${amt} paid on {dt(iss, 'long')}",
                ("Notewise Business", f"${amt}"),
                [("Subtotal", f"${amt}"), ("Total", f"${amt}"), ("Amount paid", f"${amt}")])
    return truth("receipt", "Notewise Labs, Inc.", num, amt, "USD", iss, None, None, iss, "card", True)


@case("12_workspace_eur.pdf", "arial")
def c12(d):
    """Cloud invoice: buyer ('Bill to') before seller ('Details'); '€123.45'; VAT 0 reverse charge; period dates."""
    num, iss = "5123456789", "2026-09-30"
    items = [("Cloudly Suite Business Standard", "9", D("103.50")),
             ("Cloudly Drive storage add-on, 2 TB", "1", D("19.95"))]
    total, eur = sum(i[2] for i in items), (lambda v: f"€{money(v)}")
    d.text(15, 22, "Cloudly", 20, True, color=BLUE)
    d.text(195, 22, "Invoice", 16, True, "r")
    d.blocks(36, ("Bill to", BUYER_EN))
    d.kv(120, 36, [("Invoice number:", num), ("Invoice date:", dt(iss, "dmy")), ("Billing ID:", "4417-2290-5531")],
         vx=195)
    d.kv(120, 60, [("Total in EUR", eur(total))], 13, vx=195, vbold=True)
    d.text(15, 76, "Details", 10, True)
    d.lines(15, 82, ["Cloudly Ireland Limited", "14 Hanover Quay", "Dublin 2, D02 XK64", "Ireland",
                     "VAT number: IE 3712345SH"])
    d.text(15, 112, "Summary for 1 Sep 2026 - 30 Sep 2026", 11, True)
    y = d.totals(15, 120, [("Subtotal in EUR", eur(total)), ("VAT (0%)", eur(0))], ("Total in EUR", eur(total)),
                 big=11, rule=True)
    d.lines(15, y + 6, ["Services subject to the reverse charge – VAT to be accounted for by the recipient as per",
                        "Article 196 of Council Directive 2006/112/EC."], 8, color=GREY)
    d.table(15, y + 24, "Description:90|Interval:40|Quantity:22r|Amount (€):28r",
            [[n, "1 Sep – 30 Sep", qty, money(v)] for n, qty, v in items], 8.5, 6)
    return truth("invoice", "Cloudly Ireland Limited", num, total, "EUR", iss)


@case("13_meta_ads_receipt.pdf", "arial")
def c13(d):
    """Ad receipt: 'Receipt for HB Marketing Kft.' is the buyer; seller only in footer; id is the Transaction ID."""
    txn, iss = "7264519830417265-9182736", "2026-09-08"
    camps = [("Őszi akció – konverziós kampány", 98450), ("Márkaismertség – videó", 51550)]
    total = sum(v for _, v in camps)
    d.text(105, 20, "lumina", 18, True, "c", BLUE)
    d.text(30, 36, f"Receipt for {B_NAME}", 14, True)
    d.text(30, 42, "Account ID: 102938475610293", color=GREY)
    d.kv(30, 54, [("Date:", f"{iss} 14:03"), ("Payment method:", "Mastercard ···· 1234"), ("Transaction ID:", txn),
                  ("Product type:", "Lumina ads"), ("Reference number:", "7HX2K9QW")], 10, dx=40)
    d.text(30, 86, "Paid", 11, True, color=GREEN)
    d.text(30, 94, f"Amount: {huf(total)} HUF", 15, True)
    d.text(30, 108, "Campaigns · 2026-09-01 – 2026-09-08", 10, True)
    y = d.totals(30, 115, [(n, f"{huf(v)} HUF") for n, v in camps], ("Total", f"{huf(total)} HUF"), 9.5, 10, 180, True)
    d.blocks(y + 10, ("Billed to", [B_NAME, f"{B_ADDR}, Hungary", f"VAT: {B_EU}"]), tcolor=GREY, xs=(30,))
    d.lines(30, 255, ["Lumina Social Ireland Limited", "9 Spencer Dock, North Wall Quay, Dublin 1, D01 X2Y3, Ireland",
                      "VAT Reg. No. IE 3456789QH", "Reverse charge: the customer is liable for VAT under Article 196 "
                      "of Directive 2006/112/EC."], 8, color=GREY)
    return truth("receipt", "Lumina Social Ireland Limited", txn, total, "HUF", iss, None, None, iss, "card", True)


@case("14_uk_freelancer.pdf", "office")
def c14(d):
    """UK DD/MM/YYYY dates (15/09/2026); 'From:' / 'Bill To:'; year-like number; sort code / account distractors."""
    num, iss, due = "2026-014", "2026-09-15", "2026-09-29"
    rows, net, vat, gross = calc([("Brand identity refresh – logo variations", 1, "", "600.00", 20),
                                  ("Social media template pack (12 designs)", 1, "", "400.00", 20)], 2)
    gbp = lambda v: f"£{money(v)}"
    seller = ["Amelia Hart Design Ltd", "27 Wellington Road", "Bristol BS2 9LT", "United Kingdom",
              "VAT Reg. No. GB 284 7712 09", "Company No. 11223344"]
    d.text(15, 26, "INVOICE", 28, True, color=TEAL)
    d.kv(135, 26, [("Invoice #:", num), ("Date:", dt(iss, "gb")), ("Due Date:", dt(due, "gb"))], 10.5, dx=22)
    d.blocks(50, ("From:", seller), ("Bill To:", BUYER_EN), size=10, tcolor=GREY)
    y = d.table(15, 96, "Description:110|Qty:16r|Rate:26r|Amount:28r",
                [[r.desc, r.qty, gbp(r.price), gbp(r.net)] for r in rows], 10, 7, fill=MINT)
    y = d.totals(125, y + 6, [("Subtotal", gbp(net)), ("VAT (20%)", gbp(vat))], ("Total", gbp(gross)), 10.5, 13)
    d.text(15, y + 12, "Payment details", 10.5, True)
    d.lines(15, y + 18, ["Bank transfer to: Amelia Hart Design Ltd", "Sort code: 20-45-77   Account no.: 63518842",
                         "IBAN: GB43 BUKB 2045 7763 5188 42   BIC: BUKBGB22",
                         "Please use the invoice number as the payment reference. Thank you for your business!"], 10)
    return truth("invoice", "Amelia Hart Design Ltd", num, gross, "GBP", iss, None, due, method="transfer")


@case("15_us_unambiguous_dates.pdf", "sans", letter)
def c15(d):
    """US MM/DD/YYYY made unambiguous by day 23 (09/23/2026); 'P.O. Number' and 'EIN' distractors; 'Amount Due'."""
    num, iss, due = "LA-10293", "2026-09-23", "2026-10-23"
    rows, net, vat, gross = calc([("Marketing attribution model setup", 14, "hrs", "125.00", 0),
                                  ("Looker dashboard development (fixed fee)", 1, "", "700.00", 0)], 2)
    usd = lambda v: f"${money(v)}"
    d.text(18, 22, "Lakeside Analytics LLC", 16, True)
    d.lines(18, 28, ["410 N Lake Shore Dr, Suite 1200, Madison, WI 53703",
                     "(608) 555-0142 · accounts@lakesideanalytics.com", "EIN 47-1234567"], 8.5, color=GREY)
    d.text(197, 22, "INVOICE", 22, True, "r", GREY)
    d.blocks(55, ("Bill To:", [B_NAME, B_STREET, f"{B_CITY}, Hungary", f"VAT ID: {B_EU}"]), xs=(18,))
    d.kv(130, 55, [("Invoice No:", num), ("Invoice Date:", dt(iss, "us")), ("Due Date:", dt(due, "us")),
                   ("Terms:", "Net 30"), ("P.O. Number:", "HBM-0923")], vx=197)
    y = d.table(18, 90, "Description:95|Hours/Qty:22r|Rate:30r|Amount:32r",
                [[r.desc, r.qty, usd(r.price), usd(r.net)] for r in rows], 9, 6.5)
    y = d.totals(125, y + 6, [("Subtotal:", usd(net)), ("Sales Tax (0%):", usd(0))], ("Amount Due:", usd(gross)),
                 big=13, xr=197)
    d.lines(18, y + 12, ["Please remit payment by ACH or wire transfer:",
                         "First Lakeshore Bank · ABA/Routing 075000022 · Account 2209381745 · SWIFT FLSBUS44"], 8.5)
    return truth("invoice", "Lakeside Analytics LLC", num, gross, "USD", iss, None, due, method="transfer")


@case("16_us_ambiguous_dates.pdf", "arial", letter)
def c16(d):
    """QuickBooks-like, every date ambiguous; USD + 'Net 30' (Oct 5 -> Nov 4) mean MM/DD; '1047' under 'INVOICE #'."""
    num, iss, due = "1047", "2026-10-05", "2026-11-04"
    rows, net, vat, gross = calc([("Video editing", 4, "Product clip edit, up to 60 s", "595.00", 0),
                                  ("Motion graphics", 1, "Animated logo and lower thirds", "800.00", 0)], 2)
    d.text(18, 22, "Riverbend Creative LLC", 14, True)
    d.lines(18, 28, ["1820 Riverside Ave", "Jacksonville, FL 32204", "+1 (904) 555-0187", "hello@riverbendcreative.co"])
    d.text(197, 24, "INVOICE", 20, True, "r", TEAL)
    d.blocks(56, ("BILL TO", [B_NAME, B_STREET, f"{B_CITY}, Hungary"]), tsize=8, tcolor=GREY, xs=(18,))
    for x, k, v in ((100, "INVOICE #", num), (124, "DATE", dt(iss, "us")), (150, "DUE DATE", dt(due, "us")),
                    (176, "TERMS", "Net 30")):
        d.text(x, 56, k, 8, True, color=GREY)
        d.text(x, 60.5, v)  # each value under its label
    y = d.table(18, 84, "DATE:24|ACTIVITY:34|DESCRIPTION:62|QTY:14r|RATE:22r|AMOUNT:23r",  # unit = description
                [[a, r.desc, r.unit, r.qty, money(r.price), money(r.net)]
                 for a, r in zip(["10/01/2026", "10/02/2026"], rows)], 8.5, 6.5, fill=MINT)
    d.hline(y, 18, 197)
    d.kv(140, y + 8, [("BALANCE DUE", f"${money(gross)}")], 12, vx=197, vbold=True)
    d.lines(18, y + 22, ["Payment method: ACH bank transfer", "Routing no. 063100277 · Account no. 8812045530"], 8.5)
    return truth("invoice", "Riverbend Creative LLC", num, gross, "USD", iss, None, due, method="transfer")


@case("17_aws_style.pdf", "arial")
def c17(d):
    """AWS-like 'TOTAL AMOUNT DUE ON October 2, 2026  USD 87.12'; account no. / period decoys; legal name in footer."""
    num, iss = "EUINHU26-1234567", "2026-10-02"
    charges = [("Elastic Compute Service", D("61.40")), ("Simple Object Storage", D("18.22")),
               ("Data Transfer", D("7.50"))]
    total, usd = sum(v for _, v in charges), (lambda v: f"USD {money(v)}")
    d.text(15, 20, "nimbus", 20, True, color=ORANGE)
    d.text(15, 25.5, "web services", color=GREY)
    d.lines(130, 18, ["Account number:", "441722905531", "Bill to Address:", B_NAME, B_STREET, f"{B_CITY}, HU",
                      f"VAT ID: {B_EU}"], 8.5)
    d.text(15, 52, "Invoice", 18, True)
    d.text(15, 64, "Invoice Summary", 11, True)
    d.kv(15, 72, [("Invoice Number:", num), ("Invoice Date:", dt(iss, "long"))], 9.5, vx=195)
    d.hline(79)
    d.kv(15, 86, [(f"TOTAL AMOUNT DUE ON {dt(iss, 'long')}", usd(total))], 11, vx=195, vbold=True)
    d.text(15, 97, "This invoice is for the billing period September 1 - September 30, 2026")
    d.text(15, 105, "Greetings from Nimbus Web Services, we're writing to provide you with an electronic invoice for "
                    "your use of NWS services.", 8.5)
    d.text(15, 120, "Summary", 11, True)
    y = d.totals(15, 127, [("Nimbus Web Services Service Charges", usd(total)), ("    Charges", usd(total)),
                           ("    Credits", usd(0)), ("    Tax *", usd(0))], ("Total for this invoice", usd(total)),
                 9, 10, rule=True)
    d.text(15, y + 8, "Detail", 11, True)
    d.kv(20, y + 15, [(n, usd(v)) for n, v in charges], vx=195)
    d.lines(15, 268, ["* Reverse charge: VAT to be accounted for by the recipient (Article 196, Council Directive "
                      "2006/112/EC).", "Nimbus Web Services EMEA SARL, 12 Rue de la Gare, L-1611 Luxembourg · "
                      "R.C.S. Luxembourg B 186284 · VAT Registration Number: LU 30456789"], 7.5, color=GREY)
    return truth("invoice", "Nimbus Web Services EMEA SARL", num, total, "USD", iss, None, iss)


# =========================================================================================== German
@case("18_hetzner_rechnung.pdf", "arial")
def c18(d):
    """German Rechnung: DD.MM.YYYY, '119,00 €', 'Rechnungsempfänger' window, seller in footer; period is no date."""
    num, iss, due = "R0012345678", "2026-10-01", "2026-10-15"
    per = f"{dt('2026-09-01', 'de')} – {dt('2026-09-30', 'de')}"  # carried in the unit column
    items = [("Cloud Server CPX31", 2, "29.00"), ("Storage Box BX21", 1, "21.00"), ("Backup-Speicher 200 GB", 1, "21")]
    rows, net, vat, gross = calc([(n, k, per, p, 19) for n, k, p in items], 2)
    eur = lambda v: f"{hun(v)} €"
    d.text(195, 20, "FELDBERG", 18, True, "r", RED)
    d.text(195, 26, "Rechenzentrum", align="r", color=GREY)
    d.text(20, 47, "Feldberg Rechenzentrum GmbH · Gewerbering 14 · 93055 Regensburg", 6.5, color=GREY)
    d.text(20, 52, "Rechnungsempfänger", 7, color=GREY)
    d.lines(20, 57, [B_NAME, B_STREET, B_CITY, "Ungarn"], 10)
    d.kv(122, 57, [("Rechnungsnummer:", num), ("Rechnungsdatum:", dt(iss, "de")), ("Kundennummer:", "K0815471"),
                   ("Fälligkeitsdatum:", dt(due, "de"))], 10, vx=195)
    d.text(20, 92, f"Rechnung {num}", 14, True)
    d.text(20, 101, "Für die im Leistungszeitraum erbrachten Leistungen berechnen wir Ihnen:", 9.5)
    y = d.table(20, 118, "Pos.:12|Bezeichnung:58|Zeitraum:44|Menge:14r|Einzelpreis:24r|Gesamt:23r",
                [[i + 1, r.desc, r.unit, r.qty, eur(r.price), eur(r.net)] for i, r in enumerate(rows)], 8.5, 6)
    y = d.totals(120, y + 6, [("Summe netto", eur(net)), ("USt. 19 %", eur(vat))], ("Gesamtbetrag", eur(gross)),
                 big=11, rule=True)
    d.lines(20, y + 10, [f"Zahlbar bis {dt(due, 'de')} ohne Abzug per Überweisung auf das unten genannte Konto.",
                         f"Verwendungszweck: {num}", "Mit freundlichen Grüßen, Ihr Feldberg-Team"], 9.5)
    for i, col in enumerate([["Feldberg Rechenzentrum GmbH", "Gewerbering 14", "93055 Regensburg"],
                             ["Geschäftsführer: Jonas Feldberg", "Amtsgericht Regensburg HRB 17421",
                              "USt-IdNr.: DE298417365"],
                             ["Sparkasse Regensburg", "IBAN: DE70 7505 0000 1234 5678 90", "BIC: BYLADEM1RBG"]]):
        d.lines(20 + i * 60, 272, col, 7, color=GREY)
    return truth("invoice", "Feldberg Rechenzentrum GmbH", num, gross, "EUR", iss, None, due, method="transfer")


@case("19_de_quittung_card.pdf")
def c19(d):
    """German Quittung paid by Kreditkarte: 'Bezahlt am 03.10.2026', rotated 'BEZAHLT' stamp, 'Belegnummer'."""
    num, iss = "BW-Q-2026-08812", "2026-10-03"
    rows, net, vat, gross = calc([("Bildpaket „Herbst“ – 10 Standardlizenzen", 1, "Paket", "50.00", 19)], 2)
    eur = lambda v: f"{hun(v)} €"
    d.text(15, 22, "Bildwerk Stockfotos GmbH", 15, True)
    d.lines(15, 28, ["Schanzenstraße 7 · 20357 Hamburg · Deutschland",
                     "USt-IdNr.: DE312456789 · www.bildwerk-stock.de"], 8.5, color=GREY)
    d.text(195, 22, "Quittung", 20, True, "r")
    d.blocks(46, ("Kunde", [B_NAME, B_STREET, f"{B_CITY}, Ungarn"]), tcolor=GREY)
    d.kv(125, 46, [("Belegnummer:", num), ("Datum:", dt(iss, "de")), ("Kundenkonto:", "hb-marketing")], vx=195)
    y = d.table(15, 74, "Artikel:105|Menge:20r|Einzelpreis:27r|Betrag:28r",
                [[r.desc, r.qty, eur(r.price), eur(r.net)] for r in rows], 9, 6.5)
    y = d.totals(115, y + 6, [("Zwischensumme (netto)", eur(net)), ("zzgl. 19 % MwSt.", eur(vat))],
                 ("Gesamtbetrag", eur(gross)))
    d.lines(15, y + 10, ["Zahlungsart: Kreditkarte (Visa •••• 4242)", f"Bezahlt am {dt(iss, 'de')}"], 10)
    d.stamp(160, y + 16, "BEZAHLT", 22, angle=12, color=RED)
    d.text(15, y + 26, "Betrag dankend erhalten.", 10, True, color=GREEN)
    return truth("receipt", "Bildwerk Stockfotos GmbH", num, gross, "EUR", iss, None, None, iss, "card", True)


# =================================================================================== tricky formats
OFFICE = """\
100231|Fénymásolópapír A4, 80 g, 500 lap|csom|1890|40; 100245|Fénymásolópapír A3, 80 g, 500 lap|csom|3790|5
200118|Golyóstoll, kék, 0,7 mm|db|145|100; 200119|Golyóstoll, fekete, 0,7 mm|db|145|50
200310|Zseléstoll, piros|db|390|20; 200402|Szövegkiemelő készlet, 4 szín|kész|1290|15
200511|Alkoholos filc, fekete|db|420|24; 300021|Gyorsfűző A4, PP, kék|db|89|200
300045|Iratpapucs A4, karton|db|690|30; 300102|Iratrendező 75 mm, szürke|db|990|40
300108|Iratrendező 50 mm, kék|db|950|20; 300214|Genotherm, lefűzhető, 100 db|csom|1450|10
400010|Tűzőgép 24/6, 30 lap|db|2490|6; 400011|Tűzőkapocs 24/6, 1000 db|doboz|199|50
400120|Lyukasztó, 2 lyukú, 25 lap|db|2190|4; 400215|Gemkapocs 28 mm, 100 db|doboz|159|40
400216|Gemkapocs 50 mm, 100 db|doboz|329|20; 500030|Öntapadós jegyzettömb 76×76, sárga|tömb|310|60
500031|Jelölőcímke, neon, 5×25 lap|csom|590|30; 500140|Spirálfüzet A4, kockás|db|690|25
500141|Spirálfüzet A5, vonalas|db|490|25; 600005|Ragasztóstift, 20 g|db|350|30
600110|Hibajavító roller|db|590|20; 700012|Tintapatron, fekete, XL|db|8990|6
700013|Tintapatron, színes, XL|db|9890|4; 800001|Kiszállítási díj|alk.|2990|1"""  # cikkszám|name|unit|price|qty


@case("20_two_page_atvitel.pdf")
def c20(d):
    """Two pages: 'Átvitel' subtotal on page 1, 'Áthozat' and totals on page 2; COD ('Utánvét'); order no. decoy."""
    num, iss, split = "KI-26-004512", "2026-09-21", 21
    parts = [s.strip().split("|") for s in OFFICE.replace("\n", ";").split(";")]
    rows, net, vat, gross = calc([(n, int(k), u, int(p), 27) for _, n, u, p, k in parts])
    spec = "Cikkszám:16|Megnevezés:62|Menny.:12r|Egys.:12|Nettó egységár:22r|Nettó érték:22r|ÁFA:10r|Bruttó érték:24r"
    body = [[p[0], r.desc, r.qty, r.unit, huf(r.price), huf(r.net), "27%", huf(r.gross)] for p, r in zip(parts, rows)]

    def header(page):
        d.text(15, 20, "Kárpát Irodaellátó Nyrt.", 14, True)
        d.head("SZÁMLA", f"Számlaszám: {num}", y=18, size=16)
        d.text(195, 288, f"{page}/2. oldal", 8, align="r", color=GREY)

    def carry(y, label):  # page-1 subtotal under the Nettó érték and Bruttó érték columns
        d.text(16.2, y, label, 8.5, True)
        for xr, k in ((159.8, "net"), (193.8, "gross")):
            d.text(xr, y, huf(sum(getattr(r, k) for r in rows[:split])), 8.5, True, "r")

    header(1)
    d.lines(15, 26, ["1239 Budapest, Ócsai út 5.", "Adószám: 10293841-2-44 · Cégjegyzékszám: 01-10-041234",
                     "Bankszámlaszám: 10700024-45671234-00000008"], 8.5, color=GREY)
    d.blocks(48.5, ("Vevő", BUYER_HU), xs=(110,))
    d.kv(15, 53, [("Számla kelte:", dt(iss)), ("Teljesítés dátuma:", dt(iss)), ("Fizetési határidő:", dt(iss)),
                  ("Fizetési mód:", "Utánvét"), ("Rendelésszám:", "R-100482")], dx=34)
    carry(d.table(15, 84, spec, body[:split], 8, 7.5) + 2, "Átvitel:")
    d.c.showPage()
    header(2)
    carry(40, "Áthozat:")
    y = d.table(15, 52, spec, body[split:], 8, 7.5)
    d.totals(110, y + 8, [("Nettó összesen:", ft(net)), ("ÁFA 27%:", ft(vat)), ("Bruttó összesen:", ft(gross))],
             ("Fizetendő:", ft(gross)), big=13)
    return truth("invoice", "Kárpát Irodaellátó Nyrt.", num, gross, "HUF", iss, iss, iss, method="cod")


@case("21_total_incl_vat.pdf", "arial")
def c21(d):
    """Bilingual: 'Total excl. VAT', 'VAT total', per-rate VAT table (27%/5%); only 'Total (incl. VAT)' is the total."""
    num, iss, ful, due = "DDA-2026-0211", "2026-09-18", "2026-09-17", "2026-10-02"
    rows, net, vat, gross = calc([("Online marketing workshop, 2 days / 2 napos képzés", 2, "fő", 180000, 27),
                                  ("Workbook (printed book) / Munkafüzet (könyv)", 2, "db", 12000, 5)])
    h = lambda v: f"{huf(v)} HUF"
    seller = ["Danube Digital Academy Kft.", "1052 Budapest, Deák Ferenc tér 3.", "Adószám / Tax no.: 28765437-2-42",
              "Bank: 10103001-11223344-00000002"]
    d.head("INVOICE / SZÁMLA", f"No. / Sorszám: {num}", 15, 22, 18, "l")
    d.rect(130, 13, 65, 19, LIGHT)
    d.text(133, 20, "Total (incl. VAT)")
    d.text(192, 28, h(gross), 14, True, "r")
    d.blocks(44, ("Seller / Eladó", seller), ("Customer / Vevő", [B_NAME, B_ADDR, f"Adószám / Tax no.: {B_TAX}",
                                                                  f"EU VAT: {B_EU}"]), tcolor=GREY)
    d.kv(15, 74, [("Invoice date / Kelte:", dt(iss, "iso")), ("Fulfilment date / Teljesítés:", dt(ful, "iso"))], dx=48)
    d.kv(110, 74, [("Due date / Fizetési határidő:", dt(due, "iso")), ("Payment / Fizetési mód:", "Bank transfer")],
         dx=46)
    y = d.table(15, 94, "Description / Megnevezés:76|Qty:16r|Unit price:22r|VAT:12r|Net:26r|Gross:28r",
                [row6(r) for r in rows], 8.5, 6)
    by_rate = {r.rate: [x for x in rows if x.rate == r.rate] for r in rows}
    y = d.table(15, y + 10, "VAT rate / ÁFA kulcs:40|Net / Nettó:30r|VAT / ÁFA:30r|Gross / Bruttó:30r",
                [[pct(k), *(huf(sum(getattr(r, f) for r in v)) for f in ("net", "vat", "gross"))]
                 for k, v in by_rate.items()], 8.5, 6)
    d.totals(100, y + 6, [("Total excl. VAT / Nettó összesen:", h(net)), ("VAT total / ÁFA összesen:", h(vat))],
             ("Total (incl. VAT) / Bruttó összesen:", h(gross)), big=11, rule=True)
    return truth("invoice", "Danube Digital Academy Kft.", num, gross, "HUF", iss, ful, due, method="transfer")


@case("22_slash_number_cash.pdf", "serif")
def c22(d):
    """Number with slashes '2026/000123'; cash ('Készpénz'), due date = issue date, but no 'paid' wording."""
    num, iss = "2026/000123", "2026-09-26"
    rows, net, vat, gross = calc([("Plakátnyomtatás A2, színes, 170 g", 10, "db", 2400, 27),
                                  ("Spirálozás A4, műanyag borítóval", 5, "db", 600, 27)])
    d.lines(15, 20, ["Tóth és Fia Másolószalon Bt.", "1036 Budapest, Lajos utca 54.", "Adószám: 21436587-2-41",
                     "Tel.: +36 1 388 1234"], 9.5, first_bold=True)
    d.text(195, 20, "1. példány – eredeti", 8, align="r", color=GREY)
    d.text(105, 50, "SZÁMLA", 20, True, "c")
    d.text(15, 64, f"Számla száma: {num}", 11, True)
    d.kv(15, 74, [("Vevő neve:", B_NAME), ("Vevő címe:", B_ADDR), ("Vevő adószáma:", B_TAX)], 10, dx=32)
    d.table(15, 98, "Teljesítés kelte:45c|Számla kelte:45c|Fizetési határidő:45c|Fizetés módja:45c",
            [[dt(iss), dt(iss), dt(iss), "Készpénz"]], 9, 6, grid=True)
    y = d.table(15, 118, "Megnevezés:78|Menny.:18r|Egységár:20r|Nettó:20r|ÁFA:14r|Bruttó:30r",
                [[r.desc, f"{r.qty} {r.unit}", huf(r.price), huf(r.net), pct(r.rate), huf(r.gross)] for r in rows],
                9, 6.5, grid=True)
    d.totals(110, y + 6, [("Nettó összesen:", ft(net)), ("ÁFA összesen:", ft(vat)), ("Bruttó összesen:", ft(gross))],
             ("Fizetendő:", ft(gross)), 10, 13)
    return truth("invoice", "Tóth és Fia Másolószalon Bt.", num, gross, "HUF", iss, iss, iss, method="cash")


@case("23_number_in_title.pdf")
def c23(d):
    """Unlabelled number on the title line ('SZÁMLA  2026-00077'); buyer 'Megrendelő'; no colons, wide gaps."""
    num, iss, ful, due = "2026-00077", "2026-09-26", "2026-09-25", "2026-10-10"
    rows, net, vat, gross = calc([("Terembérlet 2026.09.25., 8 óra", 1, "alk.", 280000, 27),
                                  ("Technikai felszerelés (projektor, hangosítás)", 1, "csomag", 45000, 27),
                                  ("Kávészünet", 40, "fő", 1500, 27)])
    seller = ["Kertész Rendezvényház Kft.", "2094 Nagykovácsi, Kossuth Lajos utca 80.", "Adószám: 23456787-2-13",
              "Bankszámlaszám: 10400009-01239876-00000000"]
    d.text(15, 24, "SZÁMLA", 20, True)
    d.text(58, 24, num, 20, True)
    d.blocks(40, ("Szolgáltató", seller), ("Megrendelő", BUYER_HU), tcolor=GREY)
    d.kv(15, 72, [("Számla kelte", dt(iss)), ("Teljesítés", dt(ful)), ("Fizetési határidő", dt(due)),
                  ("Fizetési mód", "Átutalás")], vx=100)
    y = d.table(15, 100, "Megnevezés:82|Menny.:20r|Egységár:22r|ÁFA:12r|Nettó:20r|Bruttó:24r",
                [row6(r) for r in rows], 8.5, 6)
    d.totals(110, y + 6, [("Nettó:", ft(net)), ("ÁFA (27%):", ft(vat))], ("Összesen fizetendő:", ft(gross)))
    return truth("invoice", "Kertész Rendezvényház Kft.", num, gross, "HUF", iss, ful, due, method="transfer")


@case("24_values_below_labels.pdf", "arial")
def c24(d):
    """Dutch B.V.: each value on the line BELOW its label in a 2x2 grid; '17-09-2026' dates; '€ 2.340,00'; VAT 0."""
    num, iss, due = "INV-7781", "2026-09-17", "2026-10-01"
    rows, net, vat, gross = calc([("Video production – 30 s product spot", 1, "", "1800.00", 0),
                                  ("Voice-over recording (EN)", 1, "", "540.00", 0)], 2)
    eur = lambda v: f"€ {hun(v)}"
    d.text(15, 24, "Brightwave Media B.V.", 16, True)
    d.lines(15, 30, ["Westerstraat 187, 1015 MA Amsterdam, The Netherlands", "BTW NL859123456B01 · KvK 76543210"],
            8.5, color=GREY)
    d.text(195, 24, "INVOICE", 18, True, "r", BLUE)
    d.blocks(44, ("Billed To", [B_NAME, B_STREET, B_CITY, "Hungary", f"VAT {B_EU}"]), size=10, tsize=7.5, tcolor=GREY)
    grid = [("Invoice No.", num), ("Issue Date", dt(iss, "nl")), ("Due Date", dt(due, "nl")),
            ("Amount Due", eur(gross))]
    for i, (k, v) in enumerate(grid):
        x, y = 125 + (i % 2) * 38, 44 + (i // 2) * 15
        d.text(x, y, k, 7.5, color=GREY)
        d.text(x, y + 5, v, 10, True)
    y = d.table(15, 84, "Description:110|Qty:16r|Unit Price:26r|Amount:28r",
                [[r.desc, r.qty, hun(r.price), hun(r.net)] for r in rows], 9, 6.5, fill=ICE)
    y = d.totals(120, y + 6, [("Subtotal", eur(net)), ("VAT 0% (reverse charge)", eur(vat))], ("Total", eur(gross)))
    d.text(15, y + 10, "Payment Details", 9, True)
    for x, k, v in ((15, "Method", "Bank transfer"), (50, "IBAN", "NL91 ABNA 0417 1643 00"),
                    (115, "BIC", "ABNANL2A"), (150, "Reference", num)):
        d.text(x, y + 17, k, 7.5, color=GREY)
        d.text(x, y + 22, v)
    return truth("invoice", "Brightwave Media B.V.", num, gross, "EUR", iss, None, due, method="transfer")


@case("25_nyugta_cafe.pdf", "mono", (80 * mm, 190 * mm))
def c25(d):
    """80 mm till slip: trade name 'FEKETE RIGÓ KÁVÉZÓ', legal name 'Rigó Gasztro Kft.'; card, 'Fizetve' printed."""
    num, iss = "ESZ-2026-00412", "2026-09-19"
    items = [("Cappuccino", 2, 890), ("Zöldséges wrap", 3, 1790), ("Házi limonádé 0,5 l", 1, 1300)]
    total, rule = sum(n * p for _, n, p in items), "-" * 38
    d.text(40, 12, "FEKETE RIGÓ KÁVÉZÓ", 11, True, "c")
    d.lines(40, 18, ["Üzemeltető: Rigó Gasztro Kft.", "1061 Budapest, Andrássy út 21.", "Adószám: 25836910-2-42"],
            7.5, align="c")
    d.text(40, 34, rule, 7.5, align="c")
    d.text(40, 40, "EGYSZERŰSÍTETT SZÁMLA", 9, True, "c")
    d.lines(5, 46, [f"Sorszám: {num}", f"Kelt: {dt(iss)} 12:47", f"Teljesítés: {dt(iss)}", f"Vevő: {B_NAME}",
                    B_ADDR, f"Vevő adószáma: {B_TAX}"], 7.5)
    d.text(40, 76, rule, 7.5, align="c")
    y = d.kv(5, 82, [p for name, n, pr in items for p in ((name, ""), (f"  {n} x {huf(pr)}", huf(n * pr)))],
             7.5, vx=75)
    d.text(40, y, rule, 7.5, align="c")
    y = d.totals(5, y + 4, [], ("ÖSSZESEN:", ft(total)), xr=75, big=10)
    y = d.kv(5, y + 1, [("ebből ÁFA 5% (tartalom):", ft(D(total) * 5 / 105)), ("Fizetési mód:", "Bankkártya"),
                        ("Fizetve:", ft(total))], 7.5, vx=75)
    d.lines(40, y + 6, ["Köszönjük, hogy nálunk fogyasztott!", "NAV ellenőrző kód: 7F2A-91C3"], 7, align="c")
    return truth("invoice", "Rigó Gasztro Kft.", num, total, "HUF", iss, iss, None, iss, "card", True)


@case("26_amount_in_words.pdf", "serif")
def c26(d):
    """Total also in words ('azaz százhuszonhétezer forint'); IBAN and phone share its lines; contract no. decoy."""
    num, iss, ful, due = "HR-2026-0412", "2026-09-28", "2026-09-25", "2026-10-12"
    rows, net, vat, gross = calc([("Rendezvényszervezési díj – őszi partnertalálkozó", 1, "alk.", 70000, 27),
                                  ("Helyszíni koordináció", 4, "óra", 7500, 27)])
    assert gross == 127000, "the amount in words below is written for 127 000 Ft"
    d.text(15, 22, "Horizont Rendezvény Kft.", 16, True)
    d.lines(15, 28, ["1118 Budapest, Budaörsi út 64.", "Adószám: 26061232-2-43 · Cégjegyzékszám: 01-09-987654",
                     "Telefon: +36 1 445 2026 · Mobil: +36 30 912 3456"])
    d.head("SZÁMLA", f"Sorszám: {num}", y=22)
    d.blocks(52, ("Vevő:", BUYER_HU), size=10)
    d.kv(120, 57, [("Számla kelte:", dt(iss)), ("Teljesítés dátuma:", dt(ful)), ("Fizetési határidő:", dt(due)),
                   ("Fizetési mód:", "Banki átutalás")], 10, vx=195)
    d.text(15, 82, "Szerződésszám: SZ-2026/118", color=GREY)
    y = d.table(15, 94, "Megnevezés:84|Menny.:18r|Egységár:22r|ÁFA:12r|Nettó:20r|Bruttó:24r",
                [row6(r) for r in rows], 9, 6.5)
    y = d.kv(120, y + 6, [("Nettó összesen:", ft(net)), ("ÁFA 27%:", ft(vat))], 10, vx=195) + 6
    d.lines(15, y, ["Bankszámlaszám: 11773016-20147852-00000009", "IBAN: HU35 1177 3016 2014 7852 0000 0009",
                    "SWIFT/BIC: OTPVHUHB", "Ügyfélszolgálat: +36 1 445 2026"], 10)
    d.kv(120, y, [("Fizetendő végösszeg:", ft(gross))], 11, vx=195, vbold=True)
    d.text(195, y + 5, "azaz százhuszonhétezer forint", 10, align="r")
    return truth("invoice", "Horizont Rendezvény Kft.", num, gross, "HUF", iss, ful, due, method="transfer")


@case("27_payment_terms_days.pdf", "office")
def c27(d):
    """'Payment terms: 14 days' and no due date printed (so null); Czech dates '22. 9. 2026'; taxable supply date."""
    num, iss = "2026-0193", "2026-09-22"
    rows, net, vat, gross = calc([("Sound design for 3 social video ads", 3, "pcs", "220.00", 0),
                                  ("Music licence, online use, 12 months", 1, "pcs", "200.00", 0)], 2)
    eur = lambda v: f"{money(v, 2, ' ', ',')} EUR"
    d.text(15, 24, "Vltava Sound Design s.r.o.", 16, True)
    d.lines(15, 30, ["Na Florenci 15, 110 00 Praha 1, Czech Republic", "IČO: 08451234 · DIČ / VAT: CZ08451234"],
            color=GREY)
    d.text(195, 24, "INVOICE", 18, True, "r")
    d.blocks(46, ("Bill to:", BUYER_EN), size=9.5)
    d.kv(118, 46, [("Invoice no.:", num), ("Issue date:", dt(iss, "cz")), ("Date of taxable supply:", dt(iss, "cz")),
                   ("Payment terms:", "14 days"), ("Payment method:", "Bank transfer")], 9.5, vx=195)
    y = d.table(15, 84, "Description:100|Qty:18r|Unit price:30r|Total:32r",
                [[r.desc, f"{r.qty} {r.unit}", eur(r.price), eur(r.net)] for r in rows], 9.5, 7)
    y = d.totals(115, y + 6, [("Total excl. VAT", eur(net)), ("VAT 0 % – reverse charge", eur(vat))],
                 ("Total to pay", eur(gross)), 10)
    d.text(15, y + 10, "Bank: Vltava Bank a.s. · IBAN: CZ65 0800 0000 1920 0014 5399 · BIC: VLTBCZPP")
    return truth("invoice", "Vltava Sound Design s.r.o.", num, gross, "EUR", iss, iss, None, method="transfer")


@case("28_minimal.pdf", "serif")
def c28(d):
    """Minimal: big seller name, 'Invoice 0042', 'Date 2026-09-30', 'Total 500 EUR', no colons; PayPal requested."""
    num, iss, total = "0042", "2026-09-30", D("500")
    d.text(20, 35, "Brume Studio SARL", 26)
    d.lines(20, 60, [f"Invoice {num}", f"Date {iss}"], 12, lead=7)
    d.text(20, 82, f"Billed to {B_NAME}, {B_STREET}, {B_CITY}, Hungary · VAT {B_EU}", 10)
    d.kv(20, 100, [("Illustrations for the autumn campaign (5 pieces)", f"{total} EUR")], 11, vx=190)
    d.text(20, 115, f"Total {total} EUR", 13, True)
    d.text(20, 124, "Please pay via PayPal to pay@brume-studio.fr", 10)
    d.text(20, 135, "VAT reverse charged, art. 196 Directive 2006/112/EC · 12 rue des Lilas, 69003 Lyon, France · "
                    "TVA FR41 853912004", 8, color=GREY)
    return truth("invoice", "Brume Studio SARL", num, total, "EUR", iss, method="paypal")


# --------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Generate the synthetic invoice PDF corpus and truth.json.")
    ap.add_argument("--out", required=True, help="output directory (created if missing)")
    out = ap.parse_args().out
    os.makedirs(out, exist_ok=True)
    records = []
    for filename, style, size, build in CASES:
        doc = Doc(os.path.join(out, filename), style, size)
        record = build(doc)
        doc.c.save()
        records.append({"file": filename, **record, "notes": fix(" ".join(build.__doc__.split()))})
    with open(os.path.join(out, "truth.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")
    note = " (no TTF font found: core fonts, ő/ű printed as ö/ü)" if CORE_ONLY else ""
    print(f"Wrote {len(records)} PDFs and truth.json to {out}{note}")


if __name__ == "__main__":
    main()
