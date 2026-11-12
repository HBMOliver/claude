#!/usr/bin/env python3
"""SocialStream logo kit (direction G2): master SVGs for every lockup and colour version.

Writes <out>/source/*.svg. Everything else in the kit (one-colour exports, PNGs, web icons, PDFs, the board
and the guide) is generated from these files.
Usage: python3 build_kit.py <kit-folder>
"""
import math, os, sys
from logolib import *
from kitmark import g2_symbol, kit_wordmark

OUT = sys.argv[1] if len(sys.argv) > 1 else "kit"

COLOURS = {
    "night": "#05070F",   # dark ground; the logo's ink on light grounds
    "cream": "#F1EEE6",   # the logo on dark grounds; light grounds
    "stream": "#7FA1C4",  # STREAM on dark grounds (the brand film's dusty blue)
    "deep": "#40658C",    # STREAM on light grounds (same hue, darker: 5.2:1 on cream)
}
SCHEMES = {
    "light": {"ink": COLOURS["night"], "acc": COLOURS["deep"]},     # for cream / white grounds
    "dark": {"ink": COLOURS["cream"], "acc": COLOURS["stream"]},     # for night / photo grounds
}
CAP = 700.0
KERN = {1: -8, 2: -16, 7: -10, 8: -24, 10: -12}

SYMBOLS = {
    # primary drawing, the reversed drawing (heavier S and wider cut against irradiation),
    # and the small-size cut for 32 px and below (bigger S, wider cut)
    "primary": dict(weight=800, gap=0.075, margin=0.08, sy=-0.03),
    "reversed": dict(weight=850, gap=0.085, margin=0.08, sy=-0.03),
    "small": dict(weight=800, fill=0.84, gap=0.12, margin=0.06, sy=-0.02),
    "small-reversed": dict(weight=850, fill=0.84, gap=0.13, margin=0.06, sy=-0.02),
}


def symbol(kind):
    p, meta = g2_symbol(**SYMBOLS[kind])
    return p


def word():
    return kit_wordmark(kern=KERN)


def two_lines(line_gap=0.30):
    """SOCIAL over STREAM, left edges aligned, the narrower line spread to the same width."""
    els = word()
    top, bot = els[:6], els[6:]
    tb, bb = bbox_many([p for p, c in top]), bbox_many([p for p, c in bot])
    bot = [(translate(p, tb[0] - bb[0], CAP * (1 + line_gap)), c) for p, c in bot]
    tb, bb = bbox_many([p for p, c in top]), bbox_many([p for p, c in bot])
    wt, wb = tb[2] - tb[0], bb[2] - bb[0]
    if wt < wb:
        top = [(translate(p, (wb - wt) / 5 * i, 0), c) for i, (p, c) in enumerate(top)]
    else:
        bot = [(translate(p, (wt - wb) / 5 * i, 0), c) for i, (p, c) in enumerate(bot)]
    return top + bot


def horizontal(kind):
    """Symbol left, wordmark right: symbol 1.75 x cap height, centred on the cap band, gap 0.5 cap."""
    w = word()
    s = symbol(kind)
    x0, y0, x1, y1 = bbox(s)
    k = CAP * 1.75 / (y1 - y0)
    s = scale(s, k)
    x0, y0, x1, y1 = bbox(s)
    wx0 = bbox_many([p for p, c in w])[0]
    s = translate(s, wx0 - CAP * 0.5 - x1, -CAP / 2 - (y0 + y1) / 2)
    return [(s, "ink", "evenodd")] + w


def stacked(kind):
    """Symbol centred above the two-line wordmark: symbol 2.2 x cap height, gap 0.55 cap."""
    w = two_lines()
    bx0, by0, bx1, by1 = bbox_many([p for p, c in w])
    s = symbol(kind)
    x0, y0, x1, y1 = bbox(s)
    k = CAP * 2.2 / (y1 - y0)
    s = scale(s, k)
    x0, y0, x1, y1 = bbox(s)
    s = translate(s, (bx0 + bx1) / 2 - (x0 + x1) / 2, by0 - CAP * 0.55 - y1)
    return [(s, "ink", "evenodd")] + w


def write(parts, path, title, scheme, H=256, pad=0.14, square=False):
    paths = [p[0] for p in parts]
    x0, y0, x1, y1 = bbox_many(paths)
    if square:
        side = max(x1 - x0, y1 - y0)
        s = H * (1 - 2 * pad) / side
        W = H
        m = (s, 0, 0, s, W / 2 - s * (x0 + x1) / 2, H / 2 - s * (y0 + y1) / 2)
    else:
        s = H * (1 - 2 * pad) / (y1 - y0)
        W = math.ceil((x1 - x0) * s + 2 * H * pad)
        m = (s, 0, 0, s, (W - (x1 - x0) * s) / 2 - s * x0, H * pad - s * y0)
    els = []
    for part in parts:
        p, key = part[0], part[1]
        rule = part[2] if len(part) > 2 else None
        els.append(el(tf(p, m), SCHEMES[scheme][key], rule))
    open(path, "w").write(svg(els, (0, 0, W, H), title))
    return W


def main():
    src = os.path.join(OUT, "source")
    os.makedirs(src, exist_ok=True)
    n = "socialstream"
    made = []
    for scheme, kind, ksmall in (("light", "primary", "small"), ("dark", "reversed", "small-reversed")):
        made.append(write([(symbol(kind), "ink", "evenodd")], f"{src}/{n}-symbol-{scheme}.svg",
                          f"SocialStream symbol ({scheme} version)", scheme, pad=0.08, square=True))
        made.append(write([(symbol(ksmall), "ink", "evenodd")], f"{src}/{n}-symbol-small-{scheme}.svg",
                          f"SocialStream symbol, small-size cut ({scheme} version)", scheme, pad=0.06, square=True))
        made.append(write(horizontal(kind), f"{src}/{n}-logo-horizontal-{scheme}.svg",
                          f"SocialStream logo, horizontal ({scheme} version)", scheme))
        made.append(write(stacked(kind), f"{src}/{n}-logo-stacked-{scheme}.svg",
                          f"SocialStream logo, stacked ({scheme} version)", scheme, pad=0.10))
        made.append(write(word(), f"{src}/{n}-wordmark-{scheme}.svg", f"SocialStream wordmark ({scheme} version)", scheme))
        made.append(write(two_lines(), f"{src}/{n}-wordmark-stacked-{scheme}.svg",
                          f"SocialStream wordmark, two lines ({scheme} version)", scheme, pad=0.12))
    print("wrote", len(made), "masters to", src)


if __name__ == "__main__":
    main()


def favicon_source(path):
    """Two-colour small cut for browser tabs: night phone with a cream S (no see-through parts), so it
    reads on light and dark tab bars alike."""
    p, meta = g2_symbol(**SYMBOLS["small"])
    # g2_symbol returns [main, foot, S...]; split the phone pieces from the S
    phone, S = p[:2], p[2:]
    x0, y0, x1, y1 = bbox_many([phone, S])
    side = max(x1 - x0, y1 - y0)
    s = 256 * 0.96 / side
    m = (s, 0, 0, s, 128 - s * (x0 + x1) / 2, 128 - s * (y0 + y1) / 2)
    els = [el(tf(phone, m), COLOURS["night"]), el(tf(S, m), COLOURS["cream"])]
    open(path, "w").write(svg(els, (0, 0, 256, 256), "SocialStream favicon"))
