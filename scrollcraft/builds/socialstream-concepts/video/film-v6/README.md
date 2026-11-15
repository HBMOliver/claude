# The brand film v6: "Through the phone", reworked (draft, 2026-11-15)

v5 (`../film/`, live on socialstream.hu as v8) reworked after the founder found it too empty and dark, its footage
weak, its motion not premium and the film too long. `SPEC.md` is the brief and the shot list. The new-idea
storylines are in `../film-new/STORYLINES.md`.

What changed from v5: 22.52 s instead of 35.4; full-frame 4K footage (the FlyX cinema from their promo, Gyenis
András's arena, the Baltic sunset) and full colour fields instead of small cards on night blue; no face in more than
one beat; numbers land and stay still (no odometer); a short motion-blur shutter; the film opens on the reel wall
with the finished logo, which is also its last frame.

Status: a draft. Only `wide/` (Hungarian) is built and rendered, for the founder's verdict. Nothing on the site
changes until they approve it: `../../assets/hero-*` are still v5's.

## Files

- `build.py`: writes the HyperFrames projects (`wide/`, and later `tall/`, `wide-en/`, `tall-en/`) from `scenes/`,
  `common.css`, `common.js` (v5's) and the logo kit's `make_motion.py` (format `film-end-wide` / `film-end-tall`: the
  logo build without a dive). It also cuts the opening wall's middle card from the sunset (`assets/tiles/mid-*.jpg`).
- `clips.sh`: cuts `assets/clips/` and the wall's stills `assets/tiles/` from the sources on this Mac (the Photos
  originals folder is its argument); the six service reels come from `../film/assets/clips/`.
- `scenes/`: `open` (wall, logo, dive), `feed` (the slides inside the phone), `close` (back out into the wall).

## Run

```sh
sh clips.sh <photos-originals-folder>
python3 build.py wide
cd wide && npx --yes hyperframes@0.9.40 check && npx --yes hyperframes@0.9.40 render -q delivery -o ../master-wide.mp4
```

Still to do once the founder approves the draft: the tall cut (`t-crowd`, `t-screen`, `t-sunset` clips and the
portrait layout checked frame by frame), the English cuts, then `../film/encode.sh` into the site's `hero-*` files.
