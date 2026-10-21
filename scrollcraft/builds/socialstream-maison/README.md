# SocialStream: Maison (luxury direction A)

The cream site taken up to a fashion house's register. One cream ground,
Fraunces at light weights, a dusty blue used sparingly, a lot of space. It
opens on the stream film (their FlyX footage moving like a feed that stops and
blooms one moment to full frame) and ends on the only dark section, the audit
application.

Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `site.js`,
`assets/`. No build step. Hungarian by default, English through the HU/EN
switch (`data-en` attributes, remembered in `localStorage`, or `?lang=en`).
Brief, feeling curve and fingerprint gate: [BRIEF.md](BRIEF.md).

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4520
```

## How the page works

- **The film** (`site.js`, shared with Journal). The video has no text; its
  `data-beats` lists the four bloom windows and the script switches the four
  manifesto lines (`.beat`) and the scrim on the film's own clock, so the lines
  are live text in both languages. The clip is fetched only after the page's
  `load` event (a media fetch holds `load`, and the poster is the film's first
  frame, so nothing is lost). It pauses when scrolled off screen, has a
  pause/play button, and under reduced motion starts paused on the poster with
  the first line showing. Phones (under 820 px) get the 9:16 cut.
- **The thumb stop** (inline script). Six 9:16 cards stay still while the page
  scrolls. 380 ms after scrolling stops, the card nearest the centre plays its
  loop, lifts, and `#stopNow` says what is playing; any scroll stills it again.
  A click on a card plays it by hand. Under reduced motion only clicks play.
  Loops (about 450 KB each) load on first play.
- **Counters** count once to the real figure when they enter view (skipped
  under reduced motion).
- **The form** checks name, email and company, then opens the visitor's mail
  app with a mailto to hello@socialstream.hu carrying every field and the
  ticked interests, shows what happened, and offers "Szöveg másolása" to copy
  the text in case no mail app opened.

## Copy notes

- Numbers are only the real ones: 81× ROAS, 79M Ft in a week, 23× holiday ROAS
  with 8M+ Ft, 105 Ft per registrant (~5700 from 600K Ft), 300M+ Ft managed,
  since 2022, Tenerife and Budapest, at most two new partners a month.
- Testimonials are word for word from the cream site. Their gondolatjel is set
  as the Hungarian en dash (–); there is no em dash in any visible copy.
- New copy for this build: the thumb-stop heading and line ("Amin megáll a
  hüvelykujj." / "Görgess, aztán állj meg."), the card captions, the "Most ezt
  nézed:" line and the photograph caption.

## Before launch

- The form hands off to the visitor's mail app; it sends nothing by itself.
  Connect it to a form backend or CRM for production.
- `tools/artifact.mjs` packages the page for a claude.ai Artifact (inlines the
  engine and `site.js`, renames the title) into `dist/`.

## Verification (this build)

- scroll-craft harness at 1440x900 (56 frames), 390x844 and reduced motion: no
  dead scroll, no console errors. The film's beat is reported to the harness as
  custom state while the film is on screen (declared a hold, since the film runs
  on its own clock), so the shots confirm the film plays and the lines change.
- `lab/func.mjs`: film source and playback per viewport, a line on screen in HU
  and EN, the thumb stop (one live card after a stop, none while moving, click
  to play), film paused off screen, form validation, the composed email, no
  untranslated text in EN, no horizontal overflow at either size.
- Not verified on a real phone or in Safari.
