#!/usr/bin/env python3
"""Round 3: G as the base, with the phone tilted 15 degrees as in H.

  G2   the sliced phone tilted 15 degrees; the slice stays parallel to the shirt A's bar (15 degrees)
  G2a  the same phone tilted; the slice turns with it and ends up level
  G2c  the tilted phone without a slice (H's phone) next to G's wordmark
All three use E's wordmark (SOCIAL heavy with the sliced A, STREAM light).
Usage: python3 build_r3.py <out-folder>
"""
import os, sys
from logolib import *
from caps import phone_S, phone_S_sliced
from build import write_symbol, write_lockup
from build_r2 import e_word, lockup_with_symbol

OUT = sys.argv[1] if len(sys.argv) > 1 else "out_r3"
TILT = 15


def g2(slice_mode="parallel"):
    if slice_mode == "parallel":      # cut at 30 deg in the phone's own frame = 15 deg once the phone tilts
        p = phone_S_sliced(800, ang=30, gap=0.075, margin=0.08)
    elif slice_mode == "level":       # cut at 15 deg in the phone's frame = level once the phone tilts
        p = phone_S_sliced(800, ang=15, gap=0.075, margin=0.08)
    else:
        return phone_S(800, tilt=TILT)
    return rotate(p, TILT, 128, 128)


def main():
    for d in ("concepts", "test", "colour"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    concepts = {
        "g2": ("SocialStream G2: the sliced phone, tilted", "parallel"),
        "g2a": ("SocialStream G2a: tilted, level slice", "level"),
        "g2c": ("SocialStream G2c: tilted, no slice", "none"),
    }
    for k, (title, mode) in concepts.items():
        sym = g2(mode)
        parts = [(sym, "ink", "evenodd")]
        lock = lockup_with_symbol(sym, e_word(), h_factor=1.75, gap_factor=0.5)
        write_symbol(k, parts, title, os.path.join(OUT, "concepts", f"{k}-symbol.svg"), "black", pad=0.1)
        w = write_lockup(lock, title + " (lockup)", os.path.join(OUT, "concepts", f"{k}-lockup.svg"), "light")
        write_symbol(k, parts, title, os.path.join(OUT, "test", f"{k}-symbol-cream.svg"), "cream", pad=0.1)
        write_lockup(lock, title + " (lockup)", os.path.join(OUT, "test", f"{k}-lockup-night.svg"), "night")
        print(k, "lockup width", w)
    # colour version of the recommendation: SOCIAL cream, STREAM in the film blue, on night blue
    sym = g2("parallel")
    lock = lockup_with_symbol(sym, e_word(), h_factor=1.75, gap_factor=0.5)
    coloured = [lock[0]] + [(p, "ink" if i < 6 else "acc") for i, (p, c) in enumerate(lock[1:])]
    write_lockup(coloured, "SocialStream G2 in the film palette", os.path.join(OUT, "colour", "g2-lockup-night.svg"), "night")
    write_symbol("g2", [(sym, "ink", "evenodd")], "SocialStream G2 avatar in the film palette",
                 os.path.join(OUT, "colour", "g2-symbol-night.svg"), "night", pad=0.1)


if __name__ == "__main__":
    main()
