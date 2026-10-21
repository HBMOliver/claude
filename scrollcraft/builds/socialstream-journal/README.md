# SocialStream: Journal (luxury direction B)

The cream site as a printed issue. A cover with the "Social / Stream" masthead
and the stream film as its cover photograph, a contents rail with roman
chapter numbers, essays, plates, letters, and a reply card at the back. One
social gesture survives: the save. What the reader saves comes with them to
the reply card.

Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `site.js` (shared
with Maison), `assets/`. No build step. Hungarian by default, English through
the HU/EN switch (`data-en` attributes, remembered in `localStorage`, or
`?lang=en`). Brief, feeling curve and fingerprint gate: [BRIEF.md](BRIEF.md).

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4521
```

## How the page works

- **The cover film** (`site.js`): the 9:16 stream film inside a feathered frame,
  with the four cover lines (`.beat`) switched on the film's clock from the
  video's `data-beats`. Fetched after `load`, paused off screen, pause/play
  button, starts paused under reduced motion. 1080 wide on desktop, 720 under
  900 px.
- **The contents rail** (1100 px and up) marks the chapter in view
  (`aria-current`); under 1100 px a sticky top bar carries the wordmark and
  HU/EN.
- **Saves** (inline script): `.save[data-save][data-topic]` on the three laws,
  six services and four figures. Saves are kept in `sessionStorage` (`ss-saved`)
  for this tab only. The tray (`#tray`) stays hidden until the first save, then
  shows the count; opening it lists the saved titles with remove buttons and
  "Viszem az auditba". A save adds its topic to the reply card's interests and
  a note says so; removing one takes away only the topics no remaining save
  holds, so a topic ticked by hand stays ticked. Figures are listed by their
  final value and client ("105 Ft, Egészségügyi webinár"), not by whatever the
  counter shows mid-count.
- **The reply card** checks name, email and company, then opens the visitor's
  mail app with a mailto to hello@socialstream.hu carrying every field, the
  ticked interests and the saved titles, and offers "Szöveg másolása" in case
  no mail app opened.

## Copy notes

- Numbers are only the real ones: 81× ROAS, 79M Ft in a week, 23× holiday ROAS
  with 8M+ Ft, 105 Ft per registrant (~5700 from 600K Ft), 300M+ Ft managed,
  since 2022, Tenerife and Budapest, at most two new partners a month.
- The four letters are the cream site's testimonials word for word (Péter,
  Rita, the watch webshop, János). Their gondolatjel is the Hungarian en dash
  (–); there is no em dash in any visible copy.
- New copy for this build: the issue line, contents titles, chapter kickers,
  "A régi korban lájkoltál. Az új korban mentesz.", the save labels and tray
  text, plate captions, "Így néz ki az érdeklődés.".

## Before launch

- The reply card hands off to the visitor's mail app; it sends nothing by
  itself. Connect it to a form backend or CRM for production.
- `tools/artifact.mjs` packages the page for a claude.ai Artifact into `dist/`.

## Verification (this build)

- scroll-craft harness at 1440x900, 390x844 and reduced motion: no dead
  scroll, no console errors; the film's beat is reported while the cover is on
  screen.
- `lab/func.mjs`: film per viewport and a cover line in HU and EN, the rail's
  current chapter, tray hidden until the first save, three saves → count,
  labels, form interests and note; a hand-ticked topic surviving a language
  switch and an un-save; tray remove and carry; validation; the composed email
  with saved titles; saves surviving a reload; no untranslated text in EN; no
  horizontal overflow at either size; phone rail/top bar.
- Not verified on a real phone or in Safari.
