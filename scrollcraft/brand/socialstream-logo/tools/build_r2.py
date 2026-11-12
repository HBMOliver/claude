#!/usr/bin/env python3
"""Round 2: concepts built on the shirt wordmark (Montserrat caps) and the bold phone S.

  E  Your shirt, refined     SOCIAL 800 + STREAM 400, the A sliced once at 15 degrees
  F  The weight moves        flipped: SOCIAL light, STREAM bold, the slice moves into STREAM's A
  G  S on the phone          the bold S on a 9:16 phone/reel tile, its foot sliced off like the A + E's wordmark
  H  Leaning in              the same phone tilted 15 degrees + SOCIAL upright, STREAM italic
Usage: python3 build_r2.py <out-folder>
"""
import math, os, sys
from logolib import *
from caps import letters, sliced_A, wordmark, phone_S, phone_S_sliced
from build import write_symbol, write_lockup, colour, INK, ACC, CREAM, NIGHT

OUT = sys.argv[1] if len(sys.argv) > 1 else "out_r2"

E_W = [800] * 6 + [400] * 6
E_T = [-12] * 6 + [18] * 6
F_W = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850]


def nearest(w):
    return min((100, 200, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900), key=lambda v: abs(v - w))


def e_word():
    return wordmark(E_W, track=E_T, word_gap=70, slice_at=4)


F_W2 = [300] * 6 + [800] * 6
F_T = [18] * 6 + [-12] * 6


def f_word():
    return wordmark(F_W2, track=F_T, word_gap=70, slice_at=10)


def h_word():
    return wordmark([800] * 6 + [400] * 6, track=[-12] * 6 + [10] * 6, word_gap=60, italic_from=6, ital_run="mi400")


def stacked(weights, track, slice_at=None, line_gap=0.30, italic_from=None, ital_run=None):
    """Two lines, SOCIAL over STREAM, justified to the same width."""
    one = wordmark(weights, track=track, slice_at=slice_at, italic_from=italic_from, ital_run=ital_run)
    top, bot = one[:6], one[6:]
    tb, bb = bbox_many([p for p, c in top]), bbox_many([p for p, c in bot])
    cap = tb[3] - tb[1]
    # move the second line under the first, left edges aligned
    bot = [(translate(p, tb[0] - bb[0], cap * (1 + line_gap)), c) for p, c in bot]
    # justify: spread the narrower line's letters so both lines end at the same x
    tb, bb = bbox_many([p for p, c in top]), bbox_many([p for p, c in bot])
    wt, wb = tb[2] - tb[0], bb[2] - bb[0]
    if wt < wb:
        extra = (wb - wt) / 5
        top = [(translate(p, extra * i, 0), c) for i, (p, c) in enumerate(top)]
    else:
        extra = (wt - wb) / 5
        bot = [(translate(p, extra * i, 0), c) for i, (p, c) in enumerate(bot)]
    return top + bot


def phone(tilt=0.0):
    return phone_S(800, tilt=tilt)


def phone_cut():
    return phone_S_sliced(800, gap=0.075, margin=0.08)


def lockup_with_symbol(sym, word, rule="evenodd", h_factor=1.55, gap_factor=0.42):
    cap = 700.0
    sx0, sy0, sx1, sy1 = bbox(sym)
    s = cap * h_factor / (sy1 - sy0)
    sym = scale(sym, s)
    sx0, sy0, sx1, sy1 = bbox(sym)
    wx0 = bbox_many([p for p, c in word])[0]
    sym = translate(sym, wx0 - cap * gap_factor - sx1, -cap / 2 - (sy0 + sy1) / 2)
    return [(sym, "ink", rule)] + list(word)


def main():
    for d in ("concepts", "test", "colour"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    concepts = {
        "e": ("SocialStream concept E: shirt wordmark, stacked", [(p, c) for p, c in stacked(E_W, E_T, slice_at=4)],
              "SocialStream concept E: shirt wordmark, refined", e_word()),
        "f": ("SocialStream concept F: the weight moves, stacked", [(p, c) for p, c in stacked(F_W2, F_T, slice_at=10)],
              "SocialStream concept F: the weight moves", f_word()),
        "g": ("SocialStream concept G: S on the phone", [(phone_cut(), "ink", "evenodd")],
              "SocialStream concept G: lockup", lockup_with_symbol(phone_cut(), e_word())),
        "h": ("SocialStream concept H: the phone leans in", [(phone(15), "ink", "evenodd")],
              "SocialStream concept H: lockup", lockup_with_symbol(phone(15), h_word(), h_factor=1.75, gap_factor=0.5)),
    }
    for k, (st, sp, lt, lp) in concepts.items():
        pad = 0.1 if k in "gh" else 0.12
        write_symbol(k, sp, st, os.path.join(OUT, "concepts", f"{k}-symbol.svg"), "black", pad=pad)
        w = write_lockup(lp, lt, os.path.join(OUT, "concepts", f"{k}-lockup.svg"), "light")
        write_symbol(k, sp, st, os.path.join(OUT, "test", f"{k}-symbol-cream.svg"), "cream", pad=pad)
        write_lockup(lp, lt, os.path.join(OUT, "test", f"{k}-lockup-night.svg"), "night")
        print(k, "lockup width", w)
    # colour hint for G: SOCIAL cream, STREAM in the film blue, on night blue
    st, sp, lt, lp = concepts["g"]
    coloured = [lp[0]] + [(p, "ink" if i < 6 else "acc") for i, (p, c) in enumerate(lp[1:])]
    write_lockup(coloured, "SocialStream concept G in the film palette", os.path.join(OUT, "colour", "g-lockup-night.svg"), "night")
    write_symbol("g", sp, "SocialStream concept G avatar in the film palette", os.path.join(OUT, "colour", "g-symbol-night.svg"), "night")


if __name__ == "__main__":
    main()
