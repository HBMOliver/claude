# Logo animation

`socialstream-logo-horizontal.mp4`: 1920 × 1080, 30 fps, 4.6 s, H.264, silent, on Night. The phone builds
itself (it appears, the S swipes up into it like the next reel, it leans in at 15°, its 15° cut opens), then
it settles into the horizontal lockup while the name streams out from behind it, and the A's cut opens like the
phone's. The last frame is `../source/socialstream-logo-horizontal-dark.svg`.

Use it as a sting or end card on 16:9 video (YouTube, presentations, the website). On an upright phone a 16:9
video is only 360–390 px wide, which puts the lockup at 216–234 px, below the kit's 250 px minimum; phone feeds
(Reels, TikTok, Stories) need the vertical and square versions, which are not made yet, and a larger lockup is
an option for this one (see `horizontal/REVIEW.md`).

## Edit or render again

The HyperFrames project is in `horizontal/` (storyboard: `horizontal/STORYBOARD.md`, review notes:
`horizontal/REVIEW.md`).

```bash
cd horizontal
npx --yes hyperframes@0.9.40 preview
npx --yes hyperframes@0.9.40 render -q delivery -o ../socialstream-logo-horizontal.mp4
```

The colours are variables (`night`, `cream`, `stream`). Timing and geometry come from
`../../tools/make_motion.py` (the beat clock is at the top); `python3 make_motion.py ../kit/motion/horizontal`
from `tools/` writes the project again and overwrites any edits made to it by hand or in the preview.
