# SocialStream: Daylight

The fourth version, asked for after the three templates: lighter and calmer, in
the manner of mastermind.com, more openly a sales page, and with all-new copy.
White page, warm mist sections, one dark band for the results; the brand film in
a frame under the headline instead of full screen.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4553
```

Then `http://localhost:4553/`. No build step. Hungarian by default, English
through the HU/EN switch.

## Files

- `index.html`: the page, both languages (`data-en`, or `data-l="hu"/"en"` twins
  where the text carries markup).
- `daylight.css`: tokens, components, breakpoints (1080, 760, 380), reduced motion.
- `daylight.js`: arrivals, counters, the film (desktop cut by frame width, the
  vertical cut on phones, pause button, paused off-screen), the scroll states
  (bar shadow, frame rise, the four steps), the testimonial wall, the form.
- `ss.js`: language, the mailto hand-off, copy buttons (shared with earlier builds).
- `COPY.md`: the copy in both languages and the facts each line rests on.
- `tools/artifact.mjs`: packages the page (or a first-screen option) as one file in `dist/`.
- `heroes/`, `heroes.css`, `heroes.js`, `tools/heroes.mjs`, `hero-*.html`: the first-screen options (below).
- `lab/func.mjs`: 33 checks without looking (film, counters, steps, wall, team
  photos, form, English, reduced motion, phone). `lab/shots.mjs`: screenshots.
  Both run from a folder that has `playwright-core` (`../socialstream-split`).

## First-screen options

Asked for after "i dont like the hero section" (2026-11-11): three different first screens on
the same page, each its own link. `index.html` keeps the original first screen. The user then
kept Cinema and Capsule and asked for the original concept back, so those two carry the claim.

- Cinema (`hero-cinema.html`): the brand film fills the first screen, edge to edge; the claim
  ("A social media meghalt. Az érdeklődés vette át a helyét."), the promise, the button and the
  ticks sit on a dark strip under it; the lead follows as a large statement.
  https://claude.ai/artifact/9aegizUPHNFQKC189MGnyn
- Glow (`hero-glow.html`): a dark stage with soft rose and amber light; the film below the
  headline opens from an inset frame to the full width as it comes up, and its colours spill on
  the stage around it; the light page rises over it as a sheet.
  https://claude.ai/artifact/NwJHqsqEVWCkLZ9M6Bg3VV
- Capsule (`hero-capsule.html`): the claim in big left-aligned type with the film playing in a
  capsule beside "érdeklődés"; scrolling grows it until it takes the place of the whole screen.
  It falls back to the film under the type with reduced motion or on a screen too short for it.
  https://claude.ai/artifact/4XxESCorvniksmAGCYWmVv

Edit `heroes/<name>.html`, `heroes.css` and `heroes.js`, then `node tools/heroes.mjs` writes the
three pages next to `index.html`, and `node tools/artifact.mjs hero-<name>` packages one into
`dist/<name>/`. `lab/heroes.mjs` runs 65 checks on them (`BASE=` for another address), and
`URL=http://localhost:4553/hero-<name>.html node lab/func.mjs` runs the page's own 33.

## Pictures

- `i-*` (services), `o-*` (result objects), `a-*` (who it is for), `silk-*`,
  `glass`: generated with ElevenLabs (Seedream 5.5), trimmed to WebP. `silk-2` came
  back on white; its background was taken out with the Vision framework's subject
  mask plus a white-to-alpha edge.
- `team-*`: the team photos from `../socialstream-colour/assets`, cut out with the
  Vision framework on the Mac (nothing uploaded), colour-matched, set on a soft
  mist-to-blush backdrop and framed so every face is the same size.
- `hero-*`: the brand film and its posters, as in the other builds.
