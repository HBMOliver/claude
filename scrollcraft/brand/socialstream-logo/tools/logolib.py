"""Small vector toolkit for building logo SVGs from glyph outlines and primitives.

Paths are lists of subpaths; each subpath is a list of segments:
  ("M", (x, y)), ("L", (x, y)), ("C", (x1, y1), (x2, y2), (x, y)), ("Z",)
Everything is absolute, cubic-only (arcs are converted to cubics), so affine transforms and
bounding boxes are exact.
"""
import math, re

K = 0.5522847498  # quarter-circle cubic handle factor


# ---------- parsing / writing ----------
def parse(d):
    toks = re.findall(r"[MLCZmlcz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?", d)
    out, sub, i, cmd = [], None, 0, None
    while i < len(toks):
        t = toks[i]
        if t in "MLCZmlcz":
            cmd = t.upper(); i += 1
            if cmd == "Z":
                sub.append(("Z",)); out.append(sub); sub = None
            continue
        if cmd == "M":
            if sub:
                out.append(sub)
            sub = [("M", (float(toks[i]), float(toks[i + 1])))]; i += 2; cmd = "L"
        elif cmd == "L":
            sub.append(("L", (float(toks[i]), float(toks[i + 1])))); i += 2
        elif cmd == "C":
            v = [float(x) for x in toks[i:i + 6]]
            sub.append(("C", (v[0], v[1]), (v[2], v[3]), (v[4], v[5]))); i += 6
    if sub:
        out.append(sub)
    return out


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def to_d(path):
    parts = []
    for sub in path:
        for seg in sub:
            if seg[0] == "Z":
                parts.append("Z")
            else:
                parts.append(seg[0] + " ".join(f"{fmt(p[0])} {fmt(p[1])}" for p in seg[1:]))
    return "".join(parts)


# ---------- transforms ----------
def tf(path, m):
    """Apply affine m = (a, b, c, d, e, f): x' = a x + c y + e, y' = b x + d y + f."""
    a, b, c, d, e, f = m
    P = lambda p: (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)
    return [[(s[0],) + tuple(P(p) for p in s[1:]) for s in sub] for sub in path]


def translate(path, dx, dy):
    return tf(path, (1, 0, 0, 1, dx, dy))


def scale(path, sx, sy=None, cx=0, cy=0):
    sy = sx if sy is None else sy
    return tf(path, (sx, 0, 0, sy, cx - sx * cx, cy - sy * cy))


def rotate(path, deg, cx=0, cy=0):
    r = math.radians(deg); co, si = math.cos(r), math.sin(r)
    return tf(path, (co, si, -si, co, cx - co * cx + si * cy, cy - si * cx - co * cy))


def shear_x(path, deg, y0=0):
    """Slant like an italic: positive deg leans the top to the right (y down)."""
    k = math.tan(math.radians(deg))
    return tf(path, (1, 0, -k, 1, k * y0, 0))


def reverse(path):
    """Reverse the direction of every subpath (for nonzero holes)."""
    out = []
    for sub in path:
        pts, segs = [], []
        cur = sub[0][1]
        for s in sub[1:]:
            if s[0] == "Z":
                continue
            segs.append((cur, s)); cur = s[-1]
        start = sub[0][1]
        new = [("M", cur)]
        for prev, s in reversed(segs):
            if s[0] == "L":
                new.append(("L", prev))
            else:
                new.append(("C", s[2], s[1], prev))
        new.append(("Z",))
        out.append(new)
    return out


# ---------- geometry ----------
def _cubic_extrema(p0, p1, p2, p3):
    ts = [0.0, 1.0]
    for i in (0, 1):
        a = -p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]
        b = 2 * (p0[i] - 2 * p1[i] + p2[i])
        c = p1[i] - p0[i]
        if abs(a) < 1e-12:
            if abs(b) > 1e-12:
                ts.append(-c / b)
        else:
            disc = b * b - 4 * a * c
            if disc >= 0:
                r = math.sqrt(disc)
                ts += [(-b + r) / (2 * a), (-b - r) / (2 * a)]
    pts = []
    for t in ts:
        if 0 <= t <= 1:
            mt = 1 - t
            pts.append(tuple(mt ** 3 * p0[i] + 3 * mt * mt * t * p1[i] + 3 * mt * t * t * p2[i] + t ** 3 * p3[i] for i in (0, 1)))
    return pts


def bbox(path):
    xs, ys = [], []
    for sub in path:
        cur = None
        for s in sub:
            if s[0] in ("M", "L"):
                cur = s[1]; xs.append(cur[0]); ys.append(cur[1])
            elif s[0] == "C":
                for p in _cubic_extrema(cur, s[1], s[2], s[3]):
                    xs.append(p[0]); ys.append(p[1])
                cur = s[3]
    return min(xs), min(ys), max(xs), max(ys)


def bbox_many(paths):
    bs = [bbox(p) for p in paths if p]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


# ---------- primitives (cubic only) ----------
def arc(cx, cy, r, a0, a1, rx=None):
    """Cubic segments along a circle (or ellipse with rx) from angle a0 to a1 (deg, y down)."""
    rx = r if rx is None else rx
    n = max(1, int(math.ceil(abs(a1 - a0) / 90 - 1e-9)))
    da = (a1 - a0) / n
    segs = []
    for i in range(n):
        t0, t1 = math.radians(a0 + i * da), math.radians(a0 + (i + 1) * da)
        k = 4 / 3 * math.tan((t1 - t0) / 4)
        p0 = (cx + rx * math.cos(t0), cy + r * math.sin(t0))
        p3 = (cx + rx * math.cos(t1), cy + r * math.sin(t1))
        p1 = (p0[0] - k * rx * math.sin(t0), p0[1] + k * r * math.cos(t0))
        p2 = (p3[0] + k * rx * math.sin(t1), p3[1] - k * r * math.cos(t1))
        segs.append(("C", p1, p2, p3))
    return segs


def pt_on(cx, cy, r, a, rx=None):
    rx = r if rx is None else rx
    return (cx + rx * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))


def circle(cx, cy, r, ccw=False):
    a0, a1 = (0, -360) if ccw else (0, 360)
    return [[("M", (cx + r, cy))] + arc(cx, cy, r, a0, a1) + [("Z",)]]


def rrect(x, y, w, h, r, ccw=False, smooth=1.0):
    """Rounded rectangle; smooth>1 extends the corner curve (continuous-curvature look)."""
    r = min(r, w / 2, h / 2)
    e = r * smooth  # how far from the corner the curve starts
    e = min(e, w / 2, h / 2)
    k = (K * r) + (e - r) * 0.9  # handle length
    pts = [
        ("M", (x + e, y)), ("L", (x + w - e, y)), ("C", (x + w - e + k, y), (x + w, y + e - k), (x + w, y + e)),
        ("L", (x + w, y + h - e)), ("C", (x + w, y + h - e + k), (x + w - e + k, y + h), (x + w - e, y + h)),
        ("L", (x + e, y + h)), ("C", (x + e - k, y + h), (x, y + h - e + k), (x, y + h - e)),
        ("L", (x, y + e)), ("C", (x, y + e - k), (x + e - k, y), (x + e, y)), ("Z",),
    ]
    p = [pts]
    return reverse(p) if ccw else p


def poly(points, close=True):
    sub = [("M", points[0])] + [("L", p) for p in points[1:]]
    if close:
        sub.append(("Z",))
    return [sub]


# ---------- svg ----------
def svg(elements, viewbox, title, width=None, height=None):
    x, y, w, h = viewbox
    W = width or w
    H = height or h
    body = "\n  ".join(elements)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)}" '
            f'width="{fmt(W)}" height="{fmt(H)}" role="img" aria-labelledby="title">\n'
            f'  <title id="title">{title}</title>\n  {body}\n</svg>\n')


def el(path, fill, rule=None, ident=None):
    attrs = f' id="{ident}"' if ident else ""
    if rule:
        attrs += f' fill-rule="{rule}"'
    return f'<path{attrs} fill="{fill}" d="{to_d(path)}"/>'


def fit(paths, box=256, pad=0.08, cy_bias=0.0):
    """Scale+translate a group of paths to sit centred in a box×box square with padding.
    Returns (transformed paths, matrix). cy_bias moves the optical centre up by a fraction of box."""
    x0, y0, x1, y1 = bbox_many(paths)
    w, h = x1 - x0, y1 - y0
    s = box * (1 - 2 * pad) / max(w, h)
    dx = box / 2 - s * (x0 + x1) / 2
    dy = box / 2 - s * (y0 + y1) / 2 - cy_bias * box
    m = (s, 0, 0, s, dx, dy)
    return [tf(p, m) for p in paths], m


# ---------- cutting a closed contour with a horizontal line ----------
def _split_cubic(p0, p1, p2, p3, t):
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a, b, c = lerp(p0, p1), lerp(p1, p2), lerp(p2, p3)
    d, e = lerp(a, b), lerp(b, c)
    f = lerp(d, e)
    return (p0, a, d, f), (f, e, c, p3)


def _roots_cubic_y(p0, p1, p2, p3, yc):
    # solve y(t) = yc on [0,1] numerically (robust bisection on sampled sign changes)
    def y(t):
        mt = 1 - t
        return mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1] - yc
    ts, N = [], 64
    prev = y(0)
    for i in range(1, N + 1):
        t1 = i / N
        cur = y(t1)
        if prev == 0:
            pass
        if (prev < 0) != (cur < 0):
            a, b = (i - 1) / N, t1
            for _ in range(60):
                m = (a + b) / 2
                if (y(a) < 0) != (y(m) < 0):
                    b = m
                else:
                    a = m
            ts.append((a + b) / 2)
        prev = cur
    return ts


def segments(sub):
    """List of cubic segments (p0,p1,p2,p3) for a closed subpath (lines become cubics)."""
    out, cur, start = [], None, None
    for s in sub:
        if s[0] == "M":
            cur = start = s[1]
        elif s[0] == "L":
            out.append((cur, cur, s[1], s[1])); cur = s[1]
        elif s[0] == "C":
            out.append((cur, s[1], s[2], s[3])); cur = s[3]
        elif s[0] == "Z":
            if abs(cur[0] - start[0]) > 1e-6 or abs(cur[1] - start[1]) > 1e-6:
                out.append((cur, cur, start, start))
    return out


def cut_y(sub, yc, keep="above"):
    """Cut one closed contour by the line y=yc; return the closed piece(s) on one side.
    Assumes the line crosses the contour exactly twice (true for an S cut through its spine)."""
    segs = []
    for sg in segments(sub):
        ts = _roots_cubic_y(*sg, yc)
        rest, t_prev = sg, 0.0
        for t in sorted(ts):
            tt = (t - t_prev) / (1 - t_prev)
            a, b = _split_cubic(*rest, tt)
            segs.append(a); rest = b; t_prev = t
        segs.append(rest)
    inside = lambda sg: ((sg[0][1] + sg[3][1]) / 2 < yc) if keep == "above" else ((sg[0][1] + sg[3][1]) / 2 > yc)
    # rotate so we start at the first kept segment after a crossing
    n = len(segs)
    k0 = next(i for i in range(n) if inside(segs[i]) and not inside(segs[i - 1]))
    segs = segs[k0:] + segs[:k0]
    piece = [("M", segs[0][0])]
    for sg in segs:
        if inside(sg):
            piece.append(("C", sg[1], sg[2], sg[3]))
        else:
            break
    piece.append(("L", piece[0][1]))
    piece.append(("Z",))
    return piece, (piece[0][1], piece[-3][-1])  # start point and end point on the cut line


def crossings_y(sub, yc):
    xs = []
    for sg in segments(sub):
        for t in _roots_cubic_y(*sg, yc):
            mt = 1 - t
            xs.append(mt ** 3 * sg[0][0] + 3 * mt * mt * t * sg[1][0] + 3 * mt * t * t * sg[2][0] + t ** 3 * sg[3][0])
    return sorted(xs)
