"""Turn the raspberry/rose parts of an image to another hue; cream, gold and greys stay as they are.

python3 tools/objects-recolour.py <target-hue-degrees> <s-mul> <v-mul> <out-dir> <image>...
Aurora Mix's objects (assets/*-mix.webp) are the renders recoloured with: 246 0.84 1.08 (measured on 2026-11-28 from
the assets: rose at hue 343-356 became 246, saturation x0.84, value x1.08; blue-purple instead of rose since
2026-11-15). The same script as that day's, kept here so new objects get the same colours.
"""
import sys, os
from PIL import Image


def weight(hd):
    """How much a hue counts as raspberry/rose: full from 318 to 6 degrees, fading out by 296 and 16."""
    if hd >= 318 or hd <= 6: return 1.0
    if 296 < hd < 318: return (hd - 296) / 22
    if 6 < hd < 16: return (16 - hd) / 10
    return 0.0


def recolour(src, dst, target, s_mul, v_mul):
    im = Image.open(src).convert("RGBA")
    alpha = im.getchannel("A")
    H, S, V = im.convert("RGB").convert("HSV").split()
    lut_h, lut_w = [], []
    for hb in range(256):
        hd = hb * 360 / 256
        w = weight(hd)
        src_h = hd + 360 if hd <= 16 else hd
        nh = (src_h + w * (target - src_h)) % 360
        lut_h.append(int(round(nh * 256 / 360)) % 256)
        lut_w.append(int(round(255 * w)))
    W = H.point(lut_w)
    H2 = H.point(lut_h)
    S2 = Image.composite(S.point(lambda v: min(255, int(v * s_mul))), S, W)
    V2 = Image.composite(V.point(lambda v: min(255, int(v * v_mul))), V, W)
    out = Image.merge("HSV", (H2, S2, V2)).convert("RGB").convert("RGBA")
    out.putalpha(alpha)
    ext = os.path.splitext(dst)[1].lower()
    out.save(dst, quality=90, method=6) if ext == ".webp" else out.save(dst)


if __name__ == "__main__":
    target, s_mul, v_mul, outdir = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    os.makedirs(outdir, exist_ok=True)
    for f in sys.argv[5:]:
        recolour(f, os.path.join(outdir, os.path.basename(f)), target, s_mul, v_mul)
    print("recoloured", len(sys.argv) - 5)
