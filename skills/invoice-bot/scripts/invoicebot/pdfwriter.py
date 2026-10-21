"""A very small PDF writer (text, lines, boxes) used for the demo invoices and the tests.

Uses the built-in Helvetica fonts with WinAnsi encoding plus the four Hungarian letters that WinAnsi
lacks (Ő ő Ű ű), so no font files are needed.
"""

# Helvetica advance widths (1/1000 em) for ASCII 32..126, from the Adobe core font metrics.
_W = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
      556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
      1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
      667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
      333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
      556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]

# Codes left unused by WinAnsi, mapped to the Hungarian double-acute letters.
_EXTRA = {'Ő': (0x81, 'Ohungarumlaut'), 'ő': (0x8D, 'ohungarumlaut'),
          'Ű': (0x8F, 'Uhungarumlaut'), 'ű': (0x90, 'uhungarumlaut')}
_BASE = {'Ő': 'O', 'ő': 'o', 'Ű': 'U', 'ű': 'u'}


def _encode(s):
    out = bytearray()
    for c in s:
        if c in _EXTRA:
            out.append(_EXTRA[c][0])
            continue
        try:
            b = c.encode('cp1252')
        except UnicodeEncodeError:
            b = b'?'
        out += b
    return bytes(out).replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)')


def text_width(s, size, bold=False):
    import unicodedata
    total = 0
    for c in s:
        c = _BASE.get(c, c)
        if ord(c) > 126:
            c = unicodedata.normalize('NFKD', c)[:1] or 'n'
        o = ord(c)
        total += _W[o - 32] if 32 <= o <= 126 else 556
    return total * size / 1000 * (1.06 if bold else 1.0)


class Page:
    def __init__(self, width=595, height=842):
        self.width, self.height = width, height
        self.ops = []

    def text(self, x, y, s, size=10, bold=False, align='left'):
        """y is measured from the top of the page."""
        if align == 'right':
            x -= text_width(s, size, bold)
        elif align == 'center':
            x -= text_width(s, size, bold) / 2
        font = 'F2' if bold else 'F1'
        self.ops.append(b'BT /%s %.1f Tf 1 0 0 1 %.2f %.2f Tm (' % (font.encode(), size, x, self.height - y)
                        + _encode(s) + b') Tj ET')

    def line(self, x1, y1, x2, y2, width=0.5, gray=0.0):
        self.ops.append(b'%.2f G %.2f w %.2f %.2f m %.2f %.2f l S' %
                        (gray, width, x1, self.height - y1, x2, self.height - y2))

    def rect(self, x, y, w, h, width=0.5, fill=None):
        if fill is not None:
            self.ops.append(b'%.2f g %.2f %.2f %.2f %.2f re f 0 g' % (fill, x, self.height - y - h, w, h))
        else:
            self.ops.append(b'%.2f w %.2f %.2f %.2f %.2f re S' % (width, x, self.height - y - h, w, h))


class PdfDoc:
    def __init__(self, title=''):
        self.pages = []
        self.title = title

    def page(self):
        p = Page()
        self.pages.append(p)
        return p

    def to_bytes(self):
        objs = []

        def add(body):
            objs.append(body)
            return len(objs)

        diffs = b' '.join(b'%d /%s' % (code, name.encode()) for code, name in _EXTRA.values())
        enc = add(b'<< /Type /Encoding /BaseEncoding /WinAnsiEncoding /Differences [' + diffs + b'] >>')
        f1 = add(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding %d 0 R >>' % enc)
        f2 = add(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding %d 0 R >>' % enc)
        pages_id = len(objs) + 1 + 2 * len(self.pages)  # placeholder index computed below
        page_ids = []
        content_ids = []
        for p in self.pages:
            stream = b'\n'.join(p.ops)
            content_ids.append(add(b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream'))
            page_ids.append(add(None))
        pages_id = add(None)
        for pid, cid, p in zip(page_ids, content_ids, self.pages):
            objs[pid - 1] = (b'<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] /Resources << /Font << '
                             b'/F1 %d 0 R /F2 %d 0 R >> >> /Contents %d 0 R >>' % (pages_id, p.width, p.height, f1, f2, cid))
        kids = b' '.join(b'%d 0 R' % i for i in page_ids)
        objs[pages_id - 1] = b'<< /Type /Pages /Kids [%s] /Count %d >>' % (kids, len(page_ids))
        catalog = add(b'<< /Type /Catalog /Pages %d 0 R >>' % pages_id)
        info = add(b'<< /Producer (invoicebot) /Title (' + _encode(self.title) + b') >>')
        out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = []
        for i, body in enumerate(objs, 1):
            offsets.append(len(out))
            out += b'%d 0 obj\n' % i + body + b'\nendobj\n'
        xref = len(out)
        out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
        for off in offsets:
            out += b'%010d 00000 n \n' % off
        out += b'trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (
            len(objs) + 1, catalog, info, xref)
        return bytes(out)

    def save(self, path):
        with open(path, 'wb') as f:
            f.write(self.to_bytes())
