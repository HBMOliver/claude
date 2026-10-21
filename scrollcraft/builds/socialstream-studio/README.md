# SocialStream: Studio (preview, four palettes)

Reel first, then a material the cursor lights, a lens over the feed, and nine
posts that become one picture. Premium sans throughout (Inter Tight for
display, Inter for text). One page, four palettes: `#oxblood` (default),
`#cream`, `#black`, `#dusk`, switched from the pill at the bottom left or by
the link's hash. Why and what: [BRIEF.md](BRIEF.md).

Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build
step. Hungarian by default, English through the HU/EN switch (remembered in
`localStorage`).

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4530
```

## How the page works

- **Versions.** `TONES` maps each palette to a dark or light tone per section
  (`data-tone`), and the CSS takes every colour from that tone's tokens
  (`--d-*` / `--l-*`, redefined per `:root[data-v]`). `MAT` holds each
  palette's material (kind and three colours) for the shader.
- **Reel.** `assets/reel-1080.mp4` (16:9) or `reel-720.mp4` (9:16, on portrait
  screens), fetched only after `load`, paused off screen. The `.cue` elements carry
  `data-t="start end"` in seconds; one rAF loop switches them on the video's
  clock, counts the numbers inside their window and dims the film behind them.
  On fine pointers the cursor is replaced by the play/pause disc.
- **Depth hero.** A pinned act (1.4 viewport-heights). The canvas runs one
  fragment shader: a height field (satin folds, plaster relief or brushed
  streaks), normals by finite differences, lit by a point light at the cursor
  (smoothed; it drifts on its own after 2.6 s idle). Satin redraws at 30 fps,
  plaster and metal only when the light or scroll moves. The word's sheen and
  Olivér's drop shadow read the same light. Falls back to a CSS gradient
  without WebGL.
- **Lens.** Two identical grids; the top one (their work) is clipped to a
  circle at the pointer, the bottom one is the same photos greyed and blurred
  under old-age captions.
- **Takeover.** A pinned act (3 viewport-heights). Each tile's arrival window
  is keyed to its posting number; scattered tiles add a pointer offset. The
  grid reports how many tiles are home as `data-sc-verify-state`, and the hero
  reports its depth step, so the harness can see the motion.
- **Bar.** Wordmark, HU/EN, the audit link; it takes its colours from the
  section underneath.

## Reel

`video/reel-16x9.json` and `video/reel-9x16.json` are `cut.swift` edits (same
13 segments and timings in both, so one set of cues serves both cuts):

    GRADE=neutral ../socialstream-split/video/cut reel-16x9.json 1920 1080 3000000 reel-1080.mp4 stills/
    GRADE=neutral ../socialstream-split/video/cut reel-9x16.json 720 1280 1500000 reel-720.mp4 stills/

The 16:9 feed wall is rendered first with the stream compositor and dropped in
as a `raw` (already graded) shot:

    ../socialstream-maison/video/stream wall-16x9.json 1920 1080 9000000 wall-16x9.mp4 0.043,0.043,0.047 stills/

Sources, all theirs: "DMC Promo video.mp4" (FlyX Tenerife), "INTRO-FINAL.mp4"
and "0. rész.mp4" (Gyenis András), the 4K studio recording, "Flyx AD 1/2", and
András's reels for the wall. Every in-point was checked frame by frame so no
window crosses into another shot, a source's own caption or a title card.
`GRADE=neutral` (new in `cut.swift`): firmer filmic curve, 10% less
saturation, a hint of cool in the shadows, no vignette.

## Olivér's voice: a script to record

About 25 seconds, spoken calmly, one line per beat of the reel. Record on a
phone in a quiet room. Lines 1 to 4 and 6 match the words already on screen;
line 5 runs under the numbers.

1. "A social media meghalt."
2. "Az érdeklődés vette át a helyét."
3. "A feed már nem azt mutatja, kit követsz. Hanem azt, ami érdekel."
4. "Videó, social, hirdetés. Egy rendszerben."
5. "Nem ígéretek. Számok."
6. "Mi ebben a korban győzünk."

## Verification (this preview)

- scroll-craft harness at 1440x900, 390x844 and reduced motion: no dead scroll,
  no console errors (the one aborted request is the reel download cancelled
  when the harness closes the page).
- `lab/shots.mjs`: every section in all four palettes on desktop and phone with
  the pointer placed, so the light, the lens and the tilt are in the shots; no
  console errors, no horizontal overflow, WebGL running, the right reel per
  viewport. EN switch: nothing left untranslated, headings with styled spans
  restore on the way back.
- Not verified on a real phone or in Safari; the WebGL material has only been
  seen in Chrome.
