"""Final G2 symbol: the bold S on a 9:16 phone, its foot sliced off, the whole phone tilted 15 degrees."""
from logolib import *
from caps import letters
from refine import recut_terminals


def g2_symbol(weight=800, fill=0.80, ratio=16 / 9, r=0.18, gap=0.075, margin=0.08, sy=0.0,
              ang_local=30, tilt=15, recut=True):
    """sy: shift of the S along the phone's axis as a fraction of the phone height (negative = up);
    ang_local: cut angle in the phone's own frame (30 here = 15 degrees once the phone tilts 15)."""
    S = letters(f"m{weight}")[0][0]
    if recut:
        S = recut_terminals(S, 75)
    x0, y0, x1, y1 = bbox(S)
    sh = 150.0
    S = scale(S, sh / (y1 - y0))
    x0, y0, x1, y1 = bbox(S)
    S = translate(S, 128 - (x0 + x1) / 2, 128 - (y0 + y1) / 2)
    tw = (x1 - x0) / fill
    th = tw * ratio
    tile = rrect(128 - tw / 2, 128 - th / 2, tw, th, tw * r, smooth=1.2)
    R = lambda p, a: rotate(p, a, 128, 128)
    t_rot, s_rot = R(tile, ang_local), R(S, ang_local)
    y_top = bbox(s_rot)[3] + margin * tw       # cut placed from the centred S, then the S may move up
    y_bot = y_top + gap * tw
    main, _ = cut_y(t_rot[0], y_top, "above")
    foot, _ = cut_y(t_rot[0], y_bot, "below")
    S = translate(S, 0, sy * th)
    mark = R([main], -ang_local) + R([foot], -ang_local) + S
    return rotate(mark, tilt, 128, 128), dict(tw=tw, th=th)


from caps import sliced_A
from refine import snap_M

WORD = "SOCIALSTREAM"


def kit_wordmark(bold=800, light=400, track_bold=-12, track_light=18, word_gap=70, kern=None):
    """SOCIAL (bold, sliced A) + STREAM (light). S terminals re-cut at 75 degrees, M at exact 60.
    kern: {index: extra space after that letter (1000-unit em)}."""
    kern = kern or {}
    out, x = [], 0.0
    for i, ch in enumerate(WORD):
        w = bold if i < 6 else light
        p, g = letters(f"m{w}")[i]
        if ch == "S":
            p = recut_terminals(p, 75)
        if i == 4:
            p = sliced_A(p)
        if ch == "M":
            p = snap_M(p)
        out.append((translate(p, x, 0), "ink" if i < 6 else "acc"))
        x += g["adv"] + (track_bold if i < 6 else track_light) + kern.get(i, 0)
        if i == 5:
            x += word_gap
    return out
