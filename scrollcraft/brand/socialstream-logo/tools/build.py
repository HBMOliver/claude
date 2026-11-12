#!/usr/bin/env python3
"""Build the four SocialStream logo concepts (round 1) as clean SVG files.

Outputs (into OUT):
  concepts/<x>-symbol.svg   one-colour symbol, 256 x 256 (black)
  concepts/<x>-lockup.svg   lockup, height 256 (ink + accent; greyscale on the sheet)
  test/<x>-*-cream.svg      the same files with a cream fill, for dark-ground checks
  colour/                   the recommended concept in the film palette
Glyph outlines come from Fraunces (SIL OFL 1.1) and Plus Jakarta Sans (SIL OFL 1.1), printed by Chrome
and read from the PDF with glyphs.py; nothing in the SVGs depends on an installed font.
"""
import json, math, os, sys
from logolib import *
from hybrid import hybrid_S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
G = {}
for f in ("set1_out.json", "set2_out.json"):
    G.update(json.load(open(os.path.join(HERE, f)))["runs"])

INK, ACC = "#111111", "#7fa1c4"          # concept files: black + the film's dusty blue
CREAM, NIGHT = "#f1eee6", "#05070f"
ITALIC_DEG = 16                           # Fraunces Italic's own slant; the brand's lean
D_LEAN_DEG = 15                           # D is geometric: a clean 15 degrees


def glyphs(run):
    return [(parse(g["d"]), g) for g in G[run]["glyphs"]]


def stem_centre(path, y):
    """x centre of the stroke(s) crossing y (for aligning stems)."""
    xs = []
    for sub in path:
        xs += crossings_y(sub, y)
    return (min(xs) + max(xs)) / 2 if xs else None


# ---------------------------------------------------------------- wordmarks
def film_wordmark(track_ls=0):
    """The existing wordmark: Fraunces 144/400 roman 'Social' + italic 'Stream' (Chrome's own kerning)."""
    rom, ita = glyphs("rom"), glyphs("ita")
    els = [(p, "ink") for p, g in rom]
    last = rom[-1][1]
    x0 = last["x"] + last["adv"] - track_ls
    els += [(translate(p, x0, 0), "acc") for p, g in ita]
    return els


def a_wordmark():
    """A: the i of Social is set in Fraunces Italic (and the accent colour)."""
    rom, ita = glyphs("rom"), glyphs("ita")
    it_i = [p for p, g in glyphs("ita_i") if g["ch"] == "i"][0]
    els = []
    xh = -220  # mid x-height (x-height is ~444 units at this size)
    for p, g in rom:
        if g["ch"] == "i":
            stem_r = [s for s in p if bbox([s])[3] > -10]       # stem subpath (touches the baseline)
            stem_i = [s for s in it_i if bbox([s])[3] > -10]
            dx = stem_centre(stem_r, xh) - stem_centre(stem_i, xh)
            els.append((translate(it_i, dx - 4, 0), "acc"))
        else:
            els.append((p, "ink"))
    last = rom[-1][1]
    x0 = last["x"] + last["adv"] - 12      # a touch tighter at the l|S hinge than the film
    els += [(translate(p, x0, 0), "acc") for p, g in ita]
    return els


def jakarta_wordmark():
    """D: 'socialstream' in Plus Jakarta Sans 600; the i's dot becomes a leaning tile (the symbol's gesture)."""
    els = []
    track = -8
    for k, (p, g) in enumerate(glyphs("jak600")):
        p = translate(p, track * k, 0)
        if g["ch"] == "i":
            subs = sorted(p, key=lambda s: bbox([s])[1])
            dot, stem = subs[0], subs[1:]
            x0, y0, x1, y1 = bbox([dot])
            w = (x1 - x0) * 0.82
            h = w * 16 / 9 * 0.62
            cx, cy = (x0 + x1) / 2, y1
            tile = rrect(cx - w / 2, cy - h, w, h, w * 0.22, smooth=1.1)
            tile = rotate(tile, D_LEAN_DEG, cx, cy)
            els.append((stem, "ink"))
            els.append((tile, "acc"))
        else:
            els.append((p, "ink"))
    return els


# ---------------------------------------------------------------- symbols
def a_symbol():
    p = glyphs("ita_i72")[0][0] if "ita_i72" in G else glyphs("ita_i36")[0][0]
    return [(p, "ink")]


def b_symbol():
    """B: the italic S passes through a 9:16 reel; where they overlap, it turns inside out (even-odd)."""
    # The reel is a little taller than the S, so the bowls stay inside with a clear margin and only the
    # top terminal (right edge) and the swash (left edge) break out: every crossing is near-perpendicular.
    S = glyphs("ita_S36")[0][0]
    x0, y0, x1, y1 = bbox(S)
    sh = 170
    S = scale(S, sh / (y1 - y0))
    x0, y0, x1, y1 = bbox(S)
    S = translate(S, 128 - (x0 + x1) / 2, 128 - (y0 + y1) / 2)
    tw = 0.66 * sh
    th = tw * 16 / 9
    tile = rrect(128 - tw / 2, 128 - th / 2, tw, th, 16, smooth=1.2)
    return [(tile + S, "ink", "evenodd")]


def c_symbol_path():
    rom = parse(G["rom_S72"]["glyphs"][0]["d"])
    ita = parse(G["ita_S72b"]["glyphs"][0]["d"])
    return hybrid_S(rom, ita, 0.40, 0.60, bridge_k=0.38, dx_extra=40)


def c_symbol():
    return [(c_symbol_path(), "ink")]


def d_tiles(w=50, g=12, r=7):
    """D: a 3x2 feed of 9:16 reels; the top-right one leans out at the italic angle."""
    h = w * 16 / 9
    cols, rows = 3, 2
    W, H = cols * w + (cols - 1) * g, rows * h + (rows - 1) * g
    x0, y0 = 128 - W / 2, 128 - H / 2
    upright, lean = [], []
    for j in range(rows):
        for i in range(cols):
            t = rrect(x0 + i * (w + g), y0 + j * (h + g), w, h, r, smooth=1.15)
            if (i, j) == (2, 0):
                # tips over its bottom-right corner, out of the grid (never into the tile below)
                lean += rotate(t, D_LEAN_DEG, x0 + i * (w + g) + w, y0 + h)
            else:
                upright += t
    return upright, lean


def d_symbol():
    up, ln = d_tiles()
    return [(up + ln, "ink")]


# ---------------------------------------------------------------- lockups
def b_lockup():
    word = film_wordmark()
    # symbol at ~1.55 x cap height, its centre on the cap-height band
    cap = 711.0
    sym = b_symbol()[0][0]
    sx0, sy0, sx1, sy1 = bbox(sym)
    s = cap * 1.55 / (sy1 - sy0)
    sym = scale(sym, s)
    sx0, sy0, sx1, sy1 = bbox(sym)
    wx0 = bbox_many([p for p, c in word])[0]
    gap = cap * 0.42
    sym = translate(sym, wx0 - gap - sx1, -cap / 2 - (sy0 + sy1) / 2)
    return [(sym, "ink", "evenodd")] + [(p, c) for p, c in word]


def c_lockup():
    """C: one S starts both words: its upright half begins 'Social', its italic half begins 'Stream'."""
    rom, ita = glyphs("rom"), glyphs("ita")
    ocial = [(p, g) for p, g in rom[1:]]
    tream = [(p, g) for p, g in ita[1:]]
    Sp = c_symbol_path()
    x0, y0, x1, y1 = bbox(Sp)
    l_top = bbox(rom[-1][0])[1]                    # top of the 'l' (ascender), negative
    asc = -l_top
    lead = 900.0                                    # line spacing at text size
    Hs = lead + asc                                  # S spans from the l top (line 1) to baseline 2
    s = Hs / (y1 - y0)
    Sp = scale(Sp, s)
    x0, y0, x1, y1 = bbox(Sp)
    Sp = translate(Sp, -x0, -y1)                     # S: left at 0, baseline (bottom) at 0
    base2, base1 = 0.0, -lead
    # split the S where its style changes, so the halves can carry the two word colours
    mid = base1 + 30
    top_half, _ = cut_y(Sp[0], mid, "above")
    bot_half, _ = cut_y(Sp[0], mid, "below")
    xh = 444.0
    gap = xh * 0.16

    def right_edge(path, ya, yb, n=24):
        xs = []
        for k in range(n + 1):
            yy = ya + (yb - ya) * k / n
            cr = []
            for sub in path:
                cr += crossings_y(sub, yy)
            if cr:
                xs.append(max(cr))
        return max(xs)
    # line 1 sits in the x-height band above base1; line 2 in the band above base2
    r1 = right_edge(Sp, base1 - xh, base1)
    r2 = right_edge(Sp, base2 - xh, base2)
    o0 = bbox(ocial[0][0])[0]
    t0 = bbox(tream[0][0])[0]
    els = [([top_half], "ink"), ([bot_half], "acc")]
    els += [(translate(p, r1 + gap - o0, base1), "ink") for p, g in ocial]
    els += [(translate(p, r2 + gap * 1.1 - t0, base2), "acc") for p, g in tream]
    return els


def d_lockup():
    word = jakarta_wordmark()
    up, ln = d_tiles()
    sym = up + ln
    sx0, sy0, sx1, sy1 = bbox(sym)
    asc = 757.0   # Jakarta ascender at this size (l height)
    s = asc * 1.18 / (sy1 - sy0)
    up, ln = scale(up, s), scale(ln, s)
    sx0, sy0, sx1, sy1 = bbox(up + ln)
    wx0 = bbox_many([p for p, c in word])[0]
    gap = 300
    dx, dy = wx0 - gap - sx1, -asc / 2 - (sy0 + sy1) / 2 + 30
    return [(translate(up, dx, dy), "ink"), (translate(ln, dx, dy), "acc")] + word


# ---------------------------------------------------------------- writers
def colour(key, scheme):
    return {"light": {"ink": INK, "acc": ACC}, "black": {"ink": "#000000", "acc": "#000000"},
            "cream": {"ink": CREAM, "acc": CREAM}, "night": {"ink": CREAM, "acc": ACC}}[scheme][key]


def write_symbol(name, parts, title, path, scheme="black", pad=0.08):
    paths = [p[0] for p in parts]
    fitted, m = fit(paths, 256, pad)
    els = []
    for (orig, *rest), fp in zip(parts, fitted):
        key = rest[0] if rest else "ink"
        rule = rest[1] if len(rest) > 1 else None
        els.append(el(fp, colour(key, scheme), rule))
    open(path, "w").write(svg(els, (0, 0, 256, 256), title))


def write_lockup(parts, title, path, scheme="light", H=256, pad=0.14):
    paths = [p[0] for p in parts]
    x0, y0, x1, y1 = bbox_many(paths)
    s = H * (1 - 2 * pad) / (y1 - y0)
    padx = H * pad
    W = (x1 - x0) * s + 2 * padx
    m = (s, 0, 0, s, padx - s * x0, H * pad - s * y0)
    els = []
    for part in parts:
        p, key = part[0], part[1]
        rule = part[2] if len(part) > 2 else None
        els.append(el(tf(p, m), colour(key, scheme), rule))
    W = math.ceil(W)
    open(path, "w").write(svg(els, (0, 0, W, H), title))
    return W


def main():
    for d in ("concepts", "test", "colour"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    concepts = {
        "a": ("SocialStream concept A: the italic i (avatar)", a_symbol(), "SocialStream concept A: wordmark", [(p, c) for p, c in a_wordmark()]),
        "b": ("SocialStream concept B: S through the reel", b_symbol(), "SocialStream concept B: lockup", b_lockup()),
        "c": ("SocialStream concept C: one S, upright then italic", c_symbol(), "SocialStream concept C: stacked lockup", c_lockup()),
        "d": ("SocialStream concept D: the reel that leans out", d_symbol(), "SocialStream concept D: lockup", d_lockup()),
    }
    for k, (st, sp, lt, lp) in concepts.items():
        write_symbol(k, sp, st, os.path.join(OUT, "concepts", f"{k}-symbol.svg"), "black", pad=0.1 if k != "a" else 0.08)
        w = write_lockup(lp, lt, os.path.join(OUT, "concepts", f"{k}-lockup.svg"), "light")
        write_symbol(k, sp, st, os.path.join(OUT, "test", f"{k}-symbol-cream.svg"), "cream", pad=0.1 if k != "a" else 0.08)
        write_lockup(lp, lt, os.path.join(OUT, "test", f"{k}-lockup-night.svg"), "night")
        print(k, "lockup width", w)
    # colour hint for the recommendation (A): film palette on night blue
    st, sp, lt, lp = concepts["a"]
    write_lockup(lp, "SocialStream concept A in the film palette", os.path.join(OUT, "colour", "a-lockup-night.svg"), "night")
    parts = [(p, "acc") for p, *_ in sp]
    write_symbol("a", parts, "SocialStream concept A avatar in the film palette", os.path.join(OUT, "colour", "a-symbol-night.svg"), "night")


if __name__ == "__main__":
    main()
