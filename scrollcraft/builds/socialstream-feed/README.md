# SocialStream: Feed (rev 2)

The site is a reels feed. It opens on the client's own 30-second brand film,
full screen; then nine posts snap one at a time, each set like the film's
title cards: the old age's post counted and struck, the second law on the
blue field, the third law on cream with the old rules crossed out, six
services and four results as carousels, the testimonials as comments, the
team as stories, a poll on who we work with, and the audit as a DM. Rev 2
keeps the concept and replaces the visuals: no clips beyond the brand film.

Static: `index.html`, `ss.js` (language, helpers, the film and the audit
hand-off), `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build step.
Hungarian by default, English through the HU/EN switch. The brand film's
system: near-black, warm white, dusty blue `#7fa1c4`, a steel-blue field
`#7697b4` and cream `#f1eee6`; Fraunces for figures and the italic accent,
Plus Jakarta Sans for everything else.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4541
```

## How the page works

- **Feed.** `html { scroll-snap-type: y mandatory }`; each `.post` holds a 9:16
  `.frame` sized in container-query units. The post on screen sets
  `body[data-post]` and `body[data-field]`, and the room around the phone
  takes its field (dark, blue, cream). Its line lights up word by word, as if
  spoken; counters, strikes and the watch bar run once on arrival and again
  on return.
- **Desktop.** A profile panel (stats, bio, highlights that jump) and an
  actions rail (like, the comments sheet, save to topics, audit). The phone
  leans a few degrees toward the cursor and settles.
- **Phones.** The post is the screen; the actions sit over it and step aside
  on the text-heavy posts and an open story.
- **DM audit.** `STEPS` asks for name, email (validated), brand, web, budget,
  goal and interests (pre-ticked from saved topics), then a message;
  `finish()` composes the email (`SS.compose`), opens the mailto and offers
  send and copy buttons.

## Checks

`lab/shots.mjs` walks the posts, a carousel, the comments sheet, a story, the
poll and the DM (run from a folder with `playwright-core`): no page errors, no
horizontal overflow at 1440×900, 1024×728 and 390×844. The design skill's
inspector still flags the posts' big captions (three or four lines inside a
9:16 frame), the room around the phone, and the profile hidden over the film;
all are the concept, not slips.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html`; `assets/` is published
next to it.
