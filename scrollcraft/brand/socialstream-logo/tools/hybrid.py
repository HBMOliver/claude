import json, math
from logolib import *

def load(path, run, i=0):
    return parse(json.load(open(path))["runs"][run]["glyphs"][i]["d"])

def piece_segs(piece):
    """cubic segments of an open piece produced by cut_y (drop the closing line)."""
    segs, cur = [], piece[0][1]
    for s in piece[1:]:
        if s[0] == "C":
            segs.append((cur, s[1], s[2], s[3])); cur = s[3]
    return segs

def unit(v):
    n = math.hypot(*v) or 1
    return (v[0] / n, v[1] / n)

def hybrid_S(rom, ita, f1=0.47, f2=0.53, bridge_k=0.42, dx_extra=0.0):
    """Upper part of the roman S joined to the lower part of the italic S."""
    r, i = rom[0], ita[0]
    rx0, ry0, rx1, ry1 = bbox(rom)
    ix0, iy0, ix1, iy1 = bbox(ita)
    # same height and baseline
    s = (ry1 - ry0) / (iy1 - iy0)
    i = scale([i], s)[0]
    ix0, iy0, ix1, iy1 = bbox([i])
    i = translate([i], 0, ry1 - iy1)[0]
    H = ry1 - ry0
    y1, y2 = ry0 + H * f1, ry0 + H * f2
    # spine centre of roman at y1 and its local slope, to place the italic part
    cr1 = sum(crossings_y(r, y1)) / 2
    cr1b = sum(crossings_y(r, y1 - H * 0.04)) / 2
    slope = (cr1 - cr1b) / (H * 0.04)
    ci2 = sum(crossings_y(i, y2)) / 2
    target = cr1 + slope * (y2 - y1) * 0.85
    i = translate([i], target - ci2 + dx_extra, 0)[0]
    up, (ua, ub) = cut_y(r, y1, "above")
    lo, (la, lb) = cut_y(i, y2, "below")
    U, L = piece_segs(up), piece_segs(lo)
    # U runs ua -> ub ; L runs la -> lb.  Join ub -> (lower crossing on the same side) etc.
    def side(p, xs):
        return "L" if abs(p[0] - min(xs)) < abs(p[0] - max(xs)) else "R"
    xu = [ua[0], ub[0]]; xl = [la[0], lb[0]]
    if side(ub, xu) != side(la, xl):
        L = [(sg[3], sg[2], sg[1], sg[0]) for sg in reversed(L)]
        la, lb = lb, la
    def bridge(p, p_prev_ctrl, q, q_next_ctrl):
        d = math.hypot(q[0] - p[0], q[1] - p[1]) * bridge_k
        t1 = unit((p[0] - p_prev_ctrl[0], p[1] - p_prev_ctrl[1]))
        t2 = unit((q_next_ctrl[0] - q[0], q_next_ctrl[1] - q[1]))
        return (p, (p[0] + t1[0] * d, p[1] + t1[1] * d), (q[0] - t2[0] * d, q[1] - t2[1] * d), q)
    b1 = bridge(U[-1][3], U[-1][2], L[0][0], L[0][1])
    b2 = bridge(L[-1][3], L[-1][2], U[0][0], U[0][1])
    segs = U + [b1] + L + [b2]
    sub = [("M", segs[0][0])] + [("C", sg[1], sg[2], sg[3]) for sg in segs] + [("Z",)]
    return [sub]
