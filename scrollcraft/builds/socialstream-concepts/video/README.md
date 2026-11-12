# The brand film's title card, re-cut with the G2 logo (2026-11-12)

The founder asked for it for Aurora Mix, the page that goes live on socialstream.hu.

## The source

Both cuts of the client's brand film carried the old Fraunces "Social Stream" title, with "Interest media
ügynökség" under it, baked into a moving reel mosaic.
- Both cuts: 16:9 1920x1080 and vertical 1080x1920, 25 fps, 750 frames, 30 s, silent.
- The title shows at the start and at the end, blur-in and blur-out ghosts included. In the vertical cut it
  covers frames about 19–88 and 680–746.
- It can't be lifted out of the mosaic, so a full-frame card covers those frames.

## The new title card

`titlecard.html` draws the logo kit's stacked dark lockup, unchanged, centred on Night `#05070F`.
`recut.mjs` lays it over both cuts on the same frames:

| Frames | What shows |
|---|---|
| 0–89 | The card, the logo already in place on the first frame, which is also the poster frame. It pushes in 2.5 % and fades out by frame 86. |
| 90–93 | The card dissolves into the claim's black ("A social media meghalt…"). |
| 94–669 | The film, untouched. |
| 670–675 | The card dissolves in over the claim's fade-out ("…győzünk."). |
| 684–749 | The logo fades in and holds to the last frame, so the loop back to frame 0 is seamless. |

- **Size:** the lockup's height is 28.125 % of the frame's height in both cuts. On Aurora Mix the wide film
  shrinks into the upright card and hands over to the upright cut; with matching sizes, one logo stays on screen.
- **Descriptor line:** "Interest media ügynökség" is off, because the kit defines no lockup with a line. `DESC=1`
  puts it back in Montserrat under the lockup.
- **Reel mosaic:** it only ever showed behind the old title, so it no longer appears. Bringing it back behind the
  logo needs the film's original edit project.

## Colour

The sources are tagged BT.601 (`bt470bg`), TV range.
- The card is composited in the film's own YUV, converted from RGB by that matrix.
- Every output is tagged `bt470bg`, like the source.

Measured in Chrome on 2026-11-12, decoding each file:
- **Night and Cream:** within 1 level of the kit in all three cuts.
- **Stream Blue:** within 2–4 levels in the 1080 and vertical cuts. In the 540 cut it is 11 levels greyer,
  because 4:2:0 colour is half resolution and STREAM's thin strokes are only a few pixels wide there.
- **Black level:** the earlier 540 and vertical encodes (made with AVFoundation, tagged BT.709) had shadows
  about 13 levels lighter than the film. The new ones match the original within 1–2 levels.
- **Frames 94–669:** identical to the film. The 1080 cut scores 49 dB against the original on them.
- **Loop seam:** frames 749 and 0 match at 64–67 dB.

On Aurora Mix the two cuts crossfade while the wide film is still finishing its shrink (opacity 0.52–0.60 of
the opening's `--q`). For about a tenth of a second of scrolling, the logos sit up to about 10 px and 1–3 % in
size apart. Moving that fade later in `mix.css` and `kit.js` would make them coincide exactly.

## Run

```bash
cd ../socialstream-split
H=<16:9 film> V=<vertical film> node ../socialstream-concepts/video/recut.mjs
```

It needs Google Chrome, ffmpeg and `playwright-core` (found in `../socialstream-split`). It writes to `out/`,
which is not committed:
- `hero-1080.mp4`, `hero-540.mp4`, `hero-v-720.mp4`: the site's three cuts, two-pass at the old bitrates (about
  2.1, 1.1 and 1.5 Mbps)
- `hero-poster.jpg`, `hero-v-poster.jpg`: frame 0
- `socialstream-film-16x9.mp4`, `socialstream-film-9x16.mp4`: full-size, high-quality masters

Copy the five site files into `../assets`, then run `node lab/check.mjs`. The film's timing is unchanged, so the
two cuts stay in step for Aurora Mix's handover.
