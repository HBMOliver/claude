"""Round 2: Montserrat caps wordmarks (from the shirt) and the bold phone/reel S."""
import json, math, os
from logolib import *

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "set3_out.json")))["runs"]
K15 = math.tan(math.radians(15))


def letters(run):
    """[(path at its own origin, glyph dict)] for a run; paths moved so each glyph starts at x=0."""
    out = []
    for g in M[run]["glyphs"]:
        p = parse(g["d"])
        out.append((translate(p, -g["x"], 0), g))
    return out


def line_x(p, q, y):
    """x on the line through p and q at height y."""
    if abs(q[1] - p[1]) < 1e-9:
        return p[0]
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def inter(p, q, c, k=K15):
    """Intersection of line pq with y = c - k*x (a line rising to the right at atan(k))."""
    # param t along pq: x = p.x + t dx, y = p.y + t dy ; y = c - k x
    dx, dy = q[0] - p[0], q[1] - p[1]
    t = (c - k * p[0] - p[1]) / (dy + k * dx)
    return (p[0] + t * dx, p[1] + t * dy)


def sliced_A(A, bar_t=None, gap=None, centre_y=None, ang=15):
    """The shirt's A, drawn clean: no crossbar; a bar rising at `ang` degrees, and the right leg cut
    just under it, so the A reads as sliced once."""
    k = math.tan(math.radians(ang))
    sub = A[0]
    pts = [s[1] for s in sub if s[0] in ("M", "L")]
    p0, p1, p2, p3, p4, p5, p6, p7 = pts[:8]       # see Montserrat's A: outer + inner outline, no curves
    # inner edges: p4 -> p5 is the inner right edge, p7 -> p6 the inner left edge (they cross at the apex)
    xb0, yb0, xb1, yb1 = bbox([sub])
    cap = -yb0
    stem = abs(p3[0] - p4[0])                      # horizontal width of a leg at the baseline
    bar_t = bar_t if bar_t is not None else stem * 0.62
    gap = gap if gap is not None else stem * 0.26
    centre_y = centre_y if centre_y is not None else -cap * 0.30
    cx = (xb0 + xb1) / 2
    c_mid = centre_y + k * cx                      # line through (cx, centre_y)
    L2 = c_mid - bar_t / 2                         # upper edge of the bar
    L1 = c_mid + bar_t / 2                         # lower edge of the bar
    L0 = L1 + gap                                  # lower edge of the cut
    OL, OR = (p0, p1), (p2, p3)
    IR, IL = (p4, p5), (p7, p6)
    apex = None
    # intersection of the two inner edges (the counter's apex)
    (x1, y1), (x2, y2) = IR
    (x3, y3), (x4, y4) = IL
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    a_ = x1 * y2 - y1 * x2
    b_ = x3 * y4 - y3 * x4
    apex = ((a_ * (x3 - x4) - (x1 - x2) * b_) / d, (a_ * (y3 - y4) - (y1 - y2) * b_) / d)
    I = lambda line, c: inter(line[0], line[1], c, k)
    main = [p0, p1, p2, I(OR, L1), I(IL, L1), p7]
    counter = [apex, I(IL, L2), I(IR, L2)]
    foot = [I(OR, L0), p3, p4, I(IR, L0)]
    return poly(oriented(main, +1)) + poly(oriented(counter, -1)) + poly(oriented(foot, +1))


def oriented(pts, sign):
    """Order points so the shoelace area has the given sign (+1 outer, -1 hole; y points down)."""
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if (a > 0) == (sign > 0) else pts[::-1]


def layout(spec, track=0.0):
    """spec: list of (run, index, colour) -> placed paths [(path, colour)], advancing by each glyph's own width."""
    out, x = [], 0.0
    for run, idx, colour, *mod in spec:
        p, g = letters(run)[idx]
        if mod and mod[0] == "slice":
            p = sliced_A(p, **(mod[1] if len(mod) > 1 else {}))
        out.append((translate(p, x, 0), colour))
        x += g["adv"] + track
    return out, x


WORD = "SOCIALSTREAM"


def wordmark(weights, colours=None, track=None, word_gap=0.0, slice_at=None, italic_from=None, ital_run=None):
    """weights: 12 weights (one per letter); slice_at: letter index of the A to slice."""
    colours = colours or ["ink"] * 12
    out, x = [], 0.0
    for i, ch in enumerate(WORD):
        run = f"m{weights[i]}" if italic_from is None or i < italic_from else (ital_run or f"mi{weights[i]}")
        p, g = letters(run)[i]
        if slice_at is not None and i == slice_at:
            p = sliced_A(p)
        out.append((translate(p, x, 0), colours[i]))
        t = (track[i] if isinstance(track, list) else (track or 0))
        x += g["adv"] + t
        if i == 5:
            x += word_gap
    return out


def phone_S(weight=800, fill=0.80, ratio=16 / 9, r=0.18, tilt=0.0):
    """The bold S knocked out of a 9:16 phone/reel tile (even-odd), the S at `fill` of the tile's width."""
    S = letters(f"m{weight}")[0][0]
    x0, y0, x1, y1 = bbox(S)
    sh = 150.0
    S = scale(S, sh / (y1 - y0))
    x0, y0, x1, y1 = bbox(S)
    S = translate(S, 128 - (x0 + x1) / 2, 128 - (y0 + y1) / 2)
    tw = (x1 - x0) / fill
    th = tw * ratio
    tile = rrect(128 - tw / 2, 128 - th / 2, tw, th, tw * r, smooth=1.2)
    p = tile + S
    return rotate(p, tilt, 128, 128) if tilt else p


def phone_S_sliced(weight=800, fill=0.80, ratio=16 / 9, r=0.18, ang=15, gap=0.075, margin=0.07):
    """The phone S with the shirt A's slice: a cut at `ang` degrees takes the phone's foot off.
    The cut sits as high as it can without touching the S (keeps `margin` x tile width clear)."""
    S = letters(f"m{weight}")[0][0]
    x0, y0, x1, y1 = bbox(S)
    sh = 150.0
    S = scale(S, sh / (y1 - y0))
    x0, y0, x1, y1 = bbox(S)
    S = translate(S, 128 - (x0 + x1) / 2, 128 - (y0 + y1) / 2)
    tw = (x1 - x0) / fill
    th = tw * ratio
    tile = rrect(128 - tw / 2, 128 - th / 2, tw, th, tw * r, smooth=1.2)
    # work in a frame where the cut is horizontal
    R = lambda p, a: rotate(p, a, 128, 128)
    t_rot, s_rot = R(tile, ang), R(S, ang)
    s_bottom = bbox(s_rot)[3]
    y_top = s_bottom + margin * tw          # upper edge of the cut
    y_bot = y_top + gap * tw                # lower edge of the cut
    main, _ = cut_y(t_rot[0], y_top, "above")
    foot, _ = cut_y(t_rot[0], y_bot, "below")
    return R([main], -ang) + R([foot], -ang) + S
