# Logo animation

The phone builds itself (it appears, the S swipes up into it like the next reel, it leans in at 15°, its 15°
cut opens), then it settles into the logo while the name comes out of it, and the A's cut opens like the
phone's. 4.6 s, 30 fps, H.264, silent, on Night; each one ends exactly on the kit's dark master.

| File | Size | Use | Last frame |
|---|---|---|---|
| `socialstream-logo-horizontal.mp4` | 1920 × 1080 | sting or end card on 16:9 video (YouTube, presentations, the website) | `../source/socialstream-logo-horizontal-dark.svg` |
| `socialstream-logo-vertical.mp4` | 1080 × 1920 | end card on Reels, TikTok and Stories | `../source/socialstream-logo-stacked-dark.svg` |
| `socialstream-logo-square.mp4` | 1080 × 1080 | feed posts | `../source/socialstream-logo-stacked-dark.svg` |

In the horizontal the name streams out of the phone's side; in the vertical and square (the stacked logo)
SOCIAL drops out from under the phone and STREAM from under SOCIAL. On an upright phone a 16:9 video is only
360–390 px wide, so the horizontal logo shows at 216–234 px there, below the kit's 250 px minimum: use the
vertical or square file on phones (see `horizontal/REVIEW.md` for the other option).

The first frame of each is plain Night, so pick the last frame as the cover image.

## Edit or render again

Each size is a HyperFrames project in its own folder (`horizontal/`, `vertical/`, `square/`, each with a
`STORYBOARD.md` and `REVIEW.md`).

```bash
cd vertical
npx --yes hyperframes@0.9.40 preview
npx --yes hyperframes@0.9.40 render -q delivery -o ../socialstream-logo-vertical.mp4
```

The colours are variables (`night`, `cream`, `stream`). Timing and geometry come from
`../../tools/make_motion.py` (the beat clock and the three formats are at the top); `python3 make_motion.py all`
from `tools/` writes the three projects again and overwrites any edits made to them by hand or in the preview.
