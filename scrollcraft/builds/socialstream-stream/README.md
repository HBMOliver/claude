# SocialStream: Stream

An ordinary one-page site with one living figure. A stream of exactly 10 000
vertical cards runs between the section grounds and the text. At the top it is
the client's own brand film (each card a tile of the playing frame); the film
breaks into a wall of small screens and pours down the page. In the middle it
draws every number in units: 10 000 followers of which 40 light up, a crowd
round one post, scattered cards falling into lines, 1 forint becoming 81, 79
million, 1 becoming 23, about 5 700 registrants. At the end it comes together
as the name. Everything else is a plain website: a menu, sections, a form.

Why this shape, in the client's words and the references they sent, is in
`BRIEF.md`.

Static: `index.html`, `stream.js` (the stream), `ss.js` (language, helpers, the
film, the audit hand-off), `scrollcraft.css`, `scrollcraft.js`, `assets/`. No
build step. Hungarian by default, English through the HU/EN switch. The brand
film's system: near-black, warm white, dusty blue `#7fa1c4`, a steel-blue field
`#7697b4` and cream `#f1eee6`; Plus Jakarta Sans, an italic Fraunces accent,
Fraunces figures.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4550
```

## How the page works

- **Layers.** Every section paints its own ground. The stream's canvas is fixed
  above the grounds (`z-index: 1`) and every section's content sits above the
  canvas (`.wrap`, `z-index: 2`), so cards pass behind the words. In the shader
  each card takes the ink of the field it is over, so it flips from light to
  dark exactly on a section's edge.
- **Formations.** `stream.js` draws all 10 000 cards in one WebGL call. A
  formation is a position, scale and alpha per card, either inside a figure's
  own box or in the background at the card's own depth (small and faint far
  away, large and soft close to the eye). `Stream.make` lays them out: `tiles`
  (the film), `field` (the background), `grid`, `disc`, `scatter`, `lines`,
  `blocks` (a counted number of cards), `points` (the wordmark, sampled from the
  brand's letters on an even lattice).
- **The timeline is in the markup.** Each `<i class="k" data-k="grid"
  data-fig="#fig-grid" data-into="dur mode transit sag">` is a marker: while the
  middle of the screen is inside it, the stream holds that formation in that
  figure's box; between two markers the scroll mixes one into the next. A
  marker can instead follow its figure (`data-auto`, `data-auto-m` on phones).
  `reach(name)` and `hold(name)` in the page script turn the same state into
  the counts, strikes and bars in the text.
- **The film.** Full screen, nothing over it. On the first scroll the video
  element steps aside and the cards draw the playing frame as tiles (the video
  is their texture), shrink into a wall of small screens and release. A phone
  that refuses autoplay gets the poster, and the tiles show the poster.
- **The claim.** A pinned stage with three layers: "A social media meghalt."
  at the back, seven tall cards rising at their own rates in the middle (the
  people, a still life, three real figures), "Az érdeklődés vette át a helyét."
  landing on top. All of it is CSS driven by the act's `--sc-p`.
- **Law I, the peak.** Pinned. The count runs to 10 000 as the cards fill a
  125 by 80 grid, the number is struck, 40 cards light up and the rest go dim.
- **Results.** Each number counts as its figure assembles: one card is one
  forint, one million forints or one registrant, and each figure says so.
- **Without the stream.** With no WebGL the page is whole: figures are left
  out, counts and text are unchanged, the name is set as type. Reduced motion
  keeps the pictures and drops the travel: formations cross-fade in place.

## Checks

Run from a folder with `playwright-core`.

- `lab/shots.mjs <out> <w> <h> [m] [positions]`: screenshots by scroll position
  and a contact sheet.
- `lab/func.mjs <out>`: the states of every scene, the services list, the form
  (validation, the composed email), the English switch, reduced motion, the
  page with WebGL refused, and a phone (vertical cut, tap to pause).
- `lab/phones.mjs <url> <out> <profile> [perf]`: nine sizes from 320 by 568 to
  1440 by 900 (a phone on its side, two iPads): text cut at the edge, text
  under 11.5px, small or covered tap targets, inputs under 16px; `perf` loads
  on a throttled phone.

Last run: no page errors, no horizontal overflow at any of the nine sizes; on a
throttled phone (4× CPU, slow 4G) the film starts at about 3.6 s. The scripted
scroll reports 30 frames a second in headless Chrome while the main thread is
over 90% idle, so that number is the headless compositor reading the canvas
back, not the page; frame rate on a real phone is not verified here.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html`; `assets/` is published next
to it.
