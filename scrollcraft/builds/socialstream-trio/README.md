# SocialStream: three templates

Three builds of the same site that differ in structure: **Orbit** (a centred
showcase with large shapes behind a phone), **Screen** (one phone that holds its
place while captions pass) and **Bento** (a board of tiles, then stacking cards).
Why three, in the client's words: [BRIEF.md](BRIEF.md).

Round 2 (2026-11-11): the three also look different now, not only move differently.
Each has its own fonts, light field, background motif, service pictures, people,
audit and footer, set in `look-orbit.css`, `look-screen.css` and `look-bento.css`:
Orbit is night glass (the only one with circles and 3D shapes), Screen is product
UI (a grid, crop marks, isometric renders, Space Grotesk and JetBrains Mono),
Bento is editorial warm (paper grain, folio lines, still-life photographs,
Instrument Serif and Inter Tight).

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4552
```

Then `http://localhost:4552/orbit.html`, `/screen.html`, `/bento.html`.
No build step. Hungarian by default, English through the HU/EN switch.

## Files

- `orbit.html`, `screen.html`, `bento.html`: each page holds its own layout, its
  own scroll logic and nothing else.
- `base.css`: what the three share. Palettes, type, the bar, the film, the
  background shapes, the phone, the service scenes, the drawn objects, the form.
- `tpl.js`: the content every page carries (services, results, voices, people,
  the audit, the footer), written into the page once with its English beside it,
  and the shared behaviour. A page calls `TPL.start()` last.
- `look-orbit.css`, `look-screen.css`, `look-bento.css`: each template's own look,
  loaded after `base.css`; the root carries `t-orbit`, `t-screen` or `t-bento`.
- `assets/so-*`, `ss-*`, `sb-*`: the six service pictures of Orbit (glass objects on
  lit discs), Screen (isometric renders) and Bento (still-life photographs), generated
  with ElevenLabs (Seedream 5.5).
- `assets/po-*`, `ps-*`: the team photos on Orbit's lilac and Screen's ice backdrop
  (cut out on the Mac with the Vision framework, same framing as the originals);
  Bento prints the originals in monochrome.
- `ss.js`: language, the film, the mailto hand-off (shared with earlier builds).
- `scrollcraft.js/.css`: the scroll engine. Only Orbit uses its pins; Screen and
  Bento hold their sections with `position: sticky` and read progress themselves.

## Palettes

A palette is one block of custom properties in `base.css`. Dusk is the default
(`:root`); `.p-lagoon` and `.p-ember` on `<body>` refill the same slots. To try
another template in another palette, change that one class. `--rose`, `--amber`,
`--violet` and `--teal` are four accent slots named after Dusk's colours; shapes,
drawn objects, scenes and the phone all read them, so nothing else needs editing.

A section takes a field class (`f-night`, `f-plum`, `f-glow`, `f-light`); `f-light`
is each palette's own light ground (lilac for Dusk, ice for Lagoon, stone for Ember,
set as `--lt` in the palette block), so no two templates share it. The bar
and the browser's theme colour are read from the field under the bar.

## Background shapes

`.shapes` is a layer inside a section; a `.shape` in it is placed with `--x`,
`--y`, `--s` and moves a little with the cursor and its own travel by `--d`.
Kinds: `sphere` (`v`, `t`, `a`), `torus` (`thin`), `pill` (`v`), `rings`,
`glowb` (`g1`..`g4`), `svg.ribbon`. Since round 2 only Orbit uses them. The rule: a solid shape may stand behind a
card, a phone or the form and lean out from it; it is never placed behind
running text. `main` clips sideways, so a shape or a turned card cannot widen
the page on a phone.

## Drawn objects

`TPL.obj('door' | 'hall' | 'watch' | 'webinar')` returns an SVG built from five
palette gradients. They stand where the case still lifes used to. Orbit shows them
solid; Screen draws them as lit teal lines; Bento leaves them out and lets the
numbers stand alone in its ledger.

## How each page moves

- **Orbit.** `.claim` is an engine pin (2.2 screens): the phone rises, the second
  sentence and the For You feed arrive together at 0.42, the notes at 0.6.
  `.law1` is a pin (2 screens): count to 0.36, strike, shrink, forty, the law.
  The ring, the rules and the fan run on how far their figure has travelled
  through the screen (`TPL.through`).
- **Screen.** Six `.cap` captions beside a sticky `.dock`. The caption nearest
  the reading line is the chapter (`data-ch` on `#story`); `MAP` says which of
  the four screens it shows; `u` is how far that caption has passed the line and
  drives the count, the like, the watch bar and the rules. On a phone the dock
  holds the top half and captions pass under it.
- **Bento.** `#board` is 2.3 screens tall with a sticky stage; each tile has a
  moment to rise (`RISE`) and the claim tile lands last. The board is sized in
  `--u` (the smaller of 1vw and 1.6vh), so it always fits one screen. On a phone
  the board is not held: it is laid out as it stands. `.scard` law cards are
  sticky with a gap below each; the gap is that card's reading time.

## Checks

Run from a folder with `playwright-core` (`../socialstream-split`):

```bash
node ../socialstream-trio/lab/func.mjs            # all three, or name them
URL=http://localhost:4552/bento.html node ../socialstream-trio/lab/shots.mjs /tmp/shots 1440 900
node ../socialstream-trio/lab/phones.mjs http://localhost:4552/orbit.html /tmp/audit i15
```

- `func.mjs`: 23, 24 and 22 checks; all pass. Each template's own scroll states,
  then services, results, voices, the form, English, reduced motion, a phone.
- `phones.mjs` on five sizes per template (320 to 1440 wide, and a phone on its
  side): no errors, nothing wider than the screen, no cut text.
- Text contrast measured per template; nothing under the line apart from text on
  gradients, which the tool cannot see and which is dark ink on a light gradient.
- Not checked: real phones, and the published pages themselves (private links).

## Publishing

```bash
node tools/artifact.mjs            # dist/orbit, dist/screen, dist/bento
```

Each `dist/<name>/index.html` is published with `assets/` beside it. Publishing
the same file again keeps the link.

- Orbit: https://claude.ai/artifact/6XLRG7wdbM4CQtVs5XLYFU
- Screen: https://claude.ai/artifact/2c4wb5FUNVGYSV9U5bnpuN
- Bento: https://claude.ai/artifact/JXfUUpavn6q7DDnKNapMZc
