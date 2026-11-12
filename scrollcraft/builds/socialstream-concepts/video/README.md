# The brand film's title card, re-cut with the G2 logo (2026-11-12)

The founder asked for it for Aurora Mix, the page that goes live on socialstream.hu.

The first re-cut (`b1ae71e`) put the logo on a plain Night card. The founder liked it but found it "a bit short"
and missed "the background of the previous where all the videos flew in". This version puts the logo back over the
film's moving reel wall, with a longer opening.

## The source

Both cuts of the client's brand film carried the old Fraunces "Social Stream" title, with "Interest media
ügynökség" under it, baked into the moving reel wall.
- Both cuts: 16:9 1920x1080 and vertical 1080x1920, 25 fps, 750 frames, 30 s, silent.
- The title shows at the start and at the end, blur-in and blur-out ghosts included: source frames about 19–88 and
  680–746.
- It can't be lifted out, so a soft Night band through the middle of the frame covers it. The wall keeps playing
  above and below the band.

## The new film: 798 frames, 31.92 s, both cuts on the same frames

`titlecard.html` draws three layers in Night `#05070F`: the band, a full-frame card, and the logo kit's stacked
dark lockup, unchanged. `recut.mjs` builds the new timeline and lays the layers over it:

| New frames | What shows |
|---|---|
| 0–137 | The opening, 5.5 s (it was 3.6). The wall from the source's first frame (0–77) blends over 12 frames into the wall from the source's ending (680–739), so it keeps moving at its own speed. |
| 0–126 | The band and the lockup over the wall from the first frame, which is also the poster. The lockup pushes in 3 % and fades out from frame 110. |
| 118–141 | The card closes over the wall by 130, then dissolves into the claim's black ("A social media meghalt…"). |
| 142–717 | The film, untouched: source frame s now lands at s + 48. |
| 718–737 | The card dissolves in over "…győzünk." and opens onto the band and the wall. |
| 732–797 | The lockup fades in and holds to the last frame. |
| 790–797 | The wall blends into the source's first frame, so the loop back to frame 0 is seamless. |

- **Size:** the band and the lockup are shares of the frame's height around its centre, the same in both cuts.
  - The band is opaque over the middle 37 % of the height and feathered over another 10 % above and below.
  - The lockup is 28.125 % of the height.
  - On Aurora Mix the wide film settles into the upright card and hands over to the upright cut; with these
    rules, one band and one logo stay on screen.
- **Reused footage:** the opening reuses 2.4 s of the ending's wall, behind the band, about 26 s before that wall
  plays again.
- **WALL_FIRST=<frames, at most 18>:** lets the wall play alone that long before the band and the lockup come in.
  The poster then comes from frame 60. It is off by default.
- **Descriptor line:** "Interest media ügynökség" is off, because the kit defines no lockup with a line. `DESC=1`
  puts it back in Montserrat under the lockup.

## Checks (2026-11-12)

The colour check decodes each file in Chrome, at frame 40.
- **Old title:** on every frame where it sits behind the band (new 15–137 and 724–797), in both cuts, the
  brightest pixel in strips inside its box but outside the new logo is luma 22–23. That is Night; nothing leaks.
- **Frame mapping:** each stretch matches the source frames it maps to at 53–60 dB (top strip, clear of the band).
  A one-frame shift scores 26 dB.
- **Loop:** new frame 797's wall is the source's first frame (54 dB).
- **Colour:**
  - Night and Cream are within 1 level of the kit.
  - Stream Blue is within 2–5 levels, or 11 greyer in the 540 cut, where STREAM's thin strokes meet half-resolution
    4:2:0 colour.
  - The sources are tagged BT.601 (`bt470bg`), TV range. The overlay is composited in the film's own YUV by that
    matrix, and every output carries the same tag.
- **Black level:** the earlier 540 and vertical encodes (AVFoundation, tagged BT.709) had shadows about 13 levels
  lighter than the film. These match the original within 1–2 levels.
- **Pages:** the concepts lab passes 215/215. `lab/sitecheck.mjs` passes on the socialstream.hu folder.

On Aurora Mix the two cuts crossfade at 0.52–0.60 of the opening's `--q`. Until 2026-11-12 the wide film was
still finishing its shrink then (it ended at 0.66), so the two logos sat up to about 10 px and 1–3 % in size
apart, and anyone who paused mid-scroll saw a doubled logo. `kit.js` now ends the shrink at 0.56, so the cuts
sit on each other through the fade: the logo and the band coincide. The reel walls above and below the band
differ between the cuts, so they blend for that moment.

## Run

```bash
cd ../socialstream-split
H=<16:9 film> V=<vertical film> node ../socialstream-concepts/video/recut.mjs
```

It needs Google Chrome, ffmpeg and `playwright-core` (found in `../socialstream-split`). It writes to `out/`,
which is not committed:
- `hero-1080.mp4`, `hero-540.mp4`, `hero-v-720.mp4`: the site's three cuts, two-pass at the old bitrates (about
  2.1, 1.1 and 1.5 Mbps)
- `hero-poster.jpg`, `hero-v-poster.jpg`: the poster frame, from the composited film
- `socialstream-film-16x9.mp4`, `socialstream-film-9x16.mp4`: full-size, high-quality masters

Copy the five site files into `../assets`, then run `node lab/check.mjs`. Both cuts share one timeline, so they
stay in step for Aurora Mix's handover.
