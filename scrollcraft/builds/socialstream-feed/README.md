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
- **Phones.** The film is its vertical cut, edge to edge (`hero-v-720.mp4`,
  720×1280 from the client's 1080×1920 file). The post is the screen; the
  actions sit over it and step aside on the text-heavy posts and an open
  story. Two quick taps like a post; a carousel shows the edge of its next
  card the first time it arrives. A tap on the film plays and pauses it, and a
  phone that refuses autoplay gets the poster and a play button; turning the
  phone swaps the cut. Posts use the dynamic viewport, so a collapsing
  toolbar never leaves a sliver of the next one. The comments sheet has a
  handle to pull it down and holds the feed still while open; a tap on a
  story's left third goes back; the feed stops snapping while the reply box
  has the keyboard. The browser's bar takes the post's colour. On its side a
  phone shows each post as a small phone under the bar, with the actions
  beside it. Every control is at least 40px tall on a touch screen.
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
all are the concept, not slips. `lab/phones.mjs` walks the page at nine
sizes (320×568 to 1440×900, a phone on its side, two iPads) and lists text
cut at the edge, text under 11.5px, small or covered tap targets and inputs
under 16px; with `perf` it loads on a throttled phone (4× CPU, slow 4G) and
times the film's first frame and the scroll.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html`; `assets/` is published
next to it.
