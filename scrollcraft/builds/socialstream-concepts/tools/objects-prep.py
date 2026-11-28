"""Trim generated object renders to their subject and save them for the page as WebP.

python3 tools/objects-prep.py <src-dir> <out-dir> <name>[:<side>[:<pad>]] ...
Reads <src-dir>/<name>.png (with a transparent background) and writes <out-dir>/<name>.webp: cropped to the subject
with <pad> of its longest side around it (default 0.06), centred on a square canvas so every object sits the same way
in its card, scaled down to <side> px (default 400, the case cards' objects). The same steps as the 2026-11-11 prep of
the o-, i- and a- objects (assets/), kept here so new ones match.
"""
import sys, os
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for job in sys.argv[3:]:
    name, *rest = job.split(':')
    side = int(rest[0]) if rest else 400
    pad = float(rest[1]) if len(rest) > 1 else 0.06
    im = Image.open(os.path.join(src, name + '.png')).convert('RGBA')
    a = im.getchannel('A')
    # a faint haze is left round some subjects; anything this transparent is dropped. A cut-out from Vision keeps its
    # body at 250-254, not 255, so anything nearly opaque is made fully so.
    a = a.point(lambda v: 0 if v < 24 else 255 if v > 240 else v)
    im.putalpha(a)
    box = a.getbbox()
    if pad:
        w, h = box[2] - box[0], box[3] - box[1]; p = int(max(w, h) * pad)
        box = (max(0, box[0] - p), max(0, box[1] - p), min(im.width, box[2] + p), min(im.height, box[3] + p))
    im = im.crop(box)
    s = max(im.size); sq = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2)); im = sq
    k = side / max(im.size)
    if k < 1: im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    p = os.path.join(out, name + '.webp'); im.save(p, 'WEBP', quality=84, method=6)
    print(name, im.size, os.path.getsize(p) // 1024, 'KB')
