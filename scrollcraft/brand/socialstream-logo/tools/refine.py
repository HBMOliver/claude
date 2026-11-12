"""Kit-stage letter refinements for the G2 wordmark (Montserrat-based outlines)."""
import math
from logolib import *
from logolib import _split_cubic


def _bez(sg, t):
    p0, p1, p2, p3 = sg
    mt = 1 - t
    return tuple(mt ** 3 * p0[i] + 3 * mt * mt * t * p1[i] + 3 * mt * t * t * p2[i] + t ** 3 * p3[i] for i in (0, 1))


def _line_root(sg, K, d, prefer_end):
    """t in [0,1] where cubic sg crosses the line through K with direction d; root nearest prefer_end."""
    f = lambda t: (lambda P: (P[0] - K[0]) * d[1] - (P[1] - K[1]) * d[0])(_bez(sg, t))
    roots, N, prev = [], 200, f(0.0)
    for i in range(1, N + 1):
        t1 = i / N
        cur = f(t1)
        if prev == 0:
            roots.append((i - 1) / N)
        elif (prev < 0) != (cur < 0):
            a, b = (i - 1) / N, t1
            for _ in range(60):
                m = (a + b) / 2
                if (f(a) < 0) != (f(m) < 0):
                    b = m
                else:
                    a = m
            roots.append((a + b) / 2)
        prev = cur
    if not roots:
        return None
    return min(roots, key=lambda t: abs(t - prefer_end))


def recut_terminals(path, target_deg=75.0, min_len=40.0):
    """Re-cut straight, slanted terminal faces (between two curves) to `target_deg` (measured like a
    compass from +x, counter-clockwise, y up), keeping the end nearest the glyph's vertical centre and
    trimming the curve on the other end."""
    x0, y0, x1, y1 = bbox(path)
    cy = (y0 + y1) / 2
    out = []
    for sub in path:
        # rebuild as a list of segments with explicit start points
        segs, cur, start = [], None, None
        for s in sub:
            if s[0] == "M":
                cur = start = s[1]
            elif s[0] == "L":
                segs.append(["L", cur, s[1]]); cur = s[1]
            elif s[0] == "C":
                segs.append(["C", cur, s[1], s[2], s[3]]); cur = s[3]
        n = len(segs)
        for i in range(n):
            sg = segs[i]
            if sg[0] != "L":
                continue
            A, B = sg[1], sg[2]
            ln = math.hypot(B[0] - A[0], B[1] - A[1])
            ang = math.degrees(math.atan2(-(B[1] - A[1]), B[0] - A[0])) % 180
            if ln < min_len or ang < 20 or ang > 160 or abs(ang - 90) < 5:
                continue
            prv, nxt = segs[(i - 1) % n], segs[(i + 1) % n]
            if prv[0] != "C" or nxt[0] != "C":
                continue
            # outer end = farther from the vertical centre
            outer_is_A = abs(A[1] - cy) > abs(B[1] - cy)
            K = B if outer_is_A else A
            O = A if outer_is_A else B
            # direction from K toward O at the target angle (choose the sign that points toward O)
            th = math.radians(target_deg)
            d = (math.cos(th), -math.sin(th))
            if (O[0] - K[0]) * d[0] + (O[1] - K[1]) * d[1] < 0:
                d = (-d[0], -d[1])
            if outer_is_A:
                cub = (prv[1], prv[2], prv[3], prv[4])
                t = _line_root(cub, K, d, 1.0)
                if t is None or t < 0.02:
                    continue
                a, _ = _split_cubic(*cub, t)
                segs[(i - 1) % n] = ["C", a[0], a[1], a[2], a[3]]
                segs[i] = ["L", a[3], K]
            else:
                cub = (nxt[1], nxt[2], nxt[3], nxt[4])
                t = _line_root(cub, K, d, 0.0)
                if t is None or t > 0.98:
                    continue
                _, b = _split_cubic(*cub, t)
                segs[i] = ["L", K, b[0]]
                segs[(i + 1) % n] = ["C", b[0], b[1], b[2], b[3]]
        new = [("M", segs[0][1])]
        for sg in segs:
            if sg[0] == "L":
                new.append(("L", sg[2]))
            else:
                new.append(("C", sg[2], sg[3], sg[4]))
        new.append(("Z",))
        out.append(new)
    return out


def snap_M(path):
    """Montserrat M is one polygon of 16 points; move the two V-bottom flats horizontally so the four
    diagonals sit at exactly 60 / 120 degrees (the tops and stems stay where they are)."""
    sub = path[0]
    pts = [s[1] for s in sub if s[0] in ("M", "L")]
    if len(pts) < 16:
        return path
    p = [list(q) for q in pts[:16]]
    t60 = math.tan(math.radians(60))
    # outer V: p2 (top inner-left of the left stem) -> p3 (V bottom, right end) ; p4 (V bottom, left end) -> p5
    dy = abs(p[3][1] - p[2][1]); p[3][0] = p[2][0] + dy / t60
    dy = abs(p[5][1] - p[4][1]); p[4][0] = p[5][0] - dy / t60
    # inner V: p10 (inner top right) -> p11 (inner bottom, right) ; p12 (inner bottom, left) -> p13
    dy = abs(p[11][1] - p[10][1]); p[11][0] = p[10][0] - dy / t60
    dy = abs(p[13][1] - p[12][1]); p[12][0] = p[13][0] + dy / t60
    return poly([tuple(q) for q in p])
