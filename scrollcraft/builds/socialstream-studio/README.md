# SocialStream: Studio (four palettes)

Reel first; a material the cursor lights behind Olivér; the three laws as
three set pieces (a struck-out follower count, a lens over the feed, nine
posts that become one picture); services lit by the cursor; four case studies;
the testimonials on a rail you drag; the people; who we work with; the audit.
Premium sans throughout (Inter Tight for display, Inter for text). One page,
four palettes: `#oxblood` (default), `#cream`, `#black`, `#dusk`, switched from
the pill at the bottom left or by the link's hash, until the client picks one.
Why and what: [BRIEF.md](BRIEF.md).

Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build
step. Hungarian by default, English through the HU/EN switch (remembered in
`localStorage`).

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4530
```

## How the page works

- **Palettes.** `TONES` maps each palette to a dark or light tone per section
  (`data-tone`), and the CSS takes every colour from that tone's tokens
  (`--d-*` / `--l-*`, redefined per `:root[data-v]`). `MAT` holds each
  palette's material for the shader. Picking one palette later means deleting
  the other three entries and the pill.
- **Reel.** `assets/reel-1080.mp4` (16:9) or `reel-720.mp4` (9:16, on portrait
  screens), fetched only after `load`, paused off screen. The `.cue` elements
  carry `data-t="start end"` in seconds; one rAF loop switches them on the
  video's clock, counts the numbers inside their window and dims the film
  behind them. On fine pointers the cursor becomes a disc that plays or pauses
  the film (and says "Húzd" over the testimonial rail).
- **Depth hero.** A pinned act (1.4 viewport-heights). One fragment shader: a
  height field (satin folds, plaster relief or brushed streaks), normals by
  finite differences, a point light at the cursor (smoothed; it drifts on its
  own after 2.6 s idle). Satin redraws at 30 fps, plaster and metal only when
  the light or scroll moves. The word's sheen and Olivér's drop shadow read the
  same light; a scrim in the section's own ground keeps the copy legible.
- **Law I.** A pinned act (2 viewport-heights): the count runs 0 to 10 000 over
  the first quarter, a line strikes it at a third, then the number dims, rises
  and the law arrives (all from `--sc-p` in CSS; the count in `l1Tick`).
- **Law II, the lens.** Two identical grids; the top one (their work) is
  clipped to a circle at the pointer, the bottom one is the same photos greyed
  and blurred under old-age captions. It follows a finger on phones and
  wanders on its own when idle.
- **Law III, the takeover.** A pinned act (3 viewport-heights). Each tile's
  arrival window is keyed to its posting number; scattered tiles add a pointer
  offset.
- **Services.** A bento whose tiles each draw a glow and a lit edge at the
  cursor (`--x`, `--y`, `--o` per tile, measured in one pass per move). The
  video tile loads `svc-video.mp4` on first sight and plays only on screen.
- **Results, people.** `[data-tilt]` cards and portraits lean toward the
  cursor; the case cards link to the live case studies on socialstream.hu.
- **Testimonials.** A scroll-snapped rail; mouse drag scrolls it, the arrow
  buttons step one card.
- **The audit.** Checks name, email and company, then opens the visitor's mail
  app with a mailto to hello@socialstream.hu carrying every field and the
  ticked interests, says what happened, and offers "Szöveg másolása" in case no
  mail app opened. The address is always visible with a copy button.
- **Bar.** Wordmark, four anchors on wide screens, HU/EN, the audit link; it
  takes its colours from the section beneath.

The harness sees the motion through `data-sc-verify-state`: the hero reports
its depth step, Law I its progress step, the takeover how many tiles are home.

## Reel

`video/reel-16x9.json` and `video/reel-9x16.json` are `cut.swift` edits (same
13 segments and timings in both, so one set of cues serves both cuts):

    GRADE=neutral ../socialstream-split/video/cut reel-16x9.json 1920 1080 3000000 reel-1080.mp4 stills/
    GRADE=neutral ../socialstream-split/video/cut reel-9x16.json 720 1280 1500000 reel-720.mp4 stills/

The 16:9 feed wall is rendered first with the stream compositor and dropped in
as a `raw` (already graded) shot:

    ../socialstream-maison/video/stream wall-16x9.json 1920 1080 9000000 wall-16x9.mp4 0.043,0.043,0.047 stills/

`video/svc-video.json` is the service tile's loop (their FlyX ad, as delivered).
Sources, all theirs: "DMC Promo video.mp4" (FlyX Tenerife), "INTRO-FINAL.mp4"
and "0. rész.mp4" (Gyenis András), the 4K studio recording, "Flyx AD 1/2", and
András's reels for the wall. Every in-point was checked frame by frame so no
window crosses into another shot, a source's own caption or a title card.
`GRADE=neutral`: firmer filmic curve, 10% less saturation, a hint of cool in
the shadows, no vignette.

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

## Copy notes

- Numbers are only the real ones: 81× ROAS, 79M Ft in a week, 23× holiday ROAS
  with 8M+ Ft, 105 Ft per registrant (~5700 from 600K Ft), 300M+ Ft managed,
  since 2022, Tenerife and Budapest, at most two new partners a month. "10 000
  követő, 40 kedvelés" is their own illustration of the old age, not a result.
- Testimonials are the cream site's six, word for word; their gondolatjel is
  the Hungarian en dash (–). No em dash anywhere in visible copy.

## Before launch

- The form hands off to the visitor's mail app; it sends nothing by itself.
  Connect it to a form backend or CRM for production.
- Pick the palette, then drop the other three from `TONES`, `MAT`, the
  `:root[data-v]` blocks and the pill.
- `tools/artifact.mjs` packages the page for a claude.ai Artifact into `dist/`.

## Verification (this build)

- scroll-craft harness at 1440x900, 390x844 and reduced motion: no dead scroll,
  no console errors (the one aborted request is the reel download cancelled
  when the harness closes the page).
- `lab/shots.mjs`: every section with the pointer placed (light, lens, glow,
  tilt, drag), all four palettes on desktop and oxblood on a phone; no console
  errors, no horizontal overflow.
- `lab/func.mjs`: palette by hash, every palette's section tones, the drag rail
  (moves and snaps, disc says "Húzd"), arrow buttons, form validation (empty
  and bad email), the composed email with budget, goal and interests, copy of
  the body and the address, EN with nothing left untranslated (chips and the
  count's thousands separator included), the phone reel and nav.
- The reel was checked frame by frame at every cue.
- Not verified on a real phone or in Safari; the WebGL material has only been
  seen in Chrome.
