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
- `tools/artifact.mjs`: packages the page as one file in `dist/daylight/`.
- `lab/func.mjs`: 22 checks without looking (film, counters, steps, wall, team
  photos, form, English, reduced motion, phone). `lab/shots.mjs`: screenshots.
  Both run from a folder that has `playwright-core` (`../socialstream-split`).

## Pictures

- `i-*` (services), `o-*` (result objects), `a-*` (who it is for), `silk-*`,
  `glass`: generated with ElevenLabs (Seedream 5.5), trimmed to WebP. `silk-2` came
  back on white; its background was taken out with the Vision framework's subject
  mask plus a white-to-alpha edge.
- `team-*`: the team photos from `../socialstream-colour/assets`, cut out with the
  Vision framework on the Mac (nothing uploaded), colour-matched, set on a soft
  mist-to-blush backdrop and framed so every face is the same size.
- `hero-*`: the brand film and its posters, as in the other builds.
