# SocialStream: Feed

The site opens on the reel, full screen, then becomes a reels feed. Nine 9:16
posts snap one at a time after it: the old age's dead post, the three laws on
their footage, services and results as carousels, the testimonials as a
comments sheet, the team as stories, a poll on who we work with, and the audit
as a DM conversation with the agency's account. One of three structurally
different designs (with [socialstream-edit](../socialstream-edit/) and
[socialstream-exhibit](../socialstream-exhibit/)) made after the client turned
down socialstream-studio.

Static: `index.html`, `ss.js` (language, helpers, the reel and the audit
hand-off, shared with the other two designs), `scrollcraft.css`,
`scrollcraft.js`, `assets/`. No build step. Hungarian by default, English
through the HU/EN switch (remembered in `localStorage`). Black, white and a
caption yellow; Inter Tight and Inter.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4541
```

## How the page works

- **Reel.** By client request the page opens on the reel from
  socialstream-studio, full screen: `reel-1080.mp4` (16:9) or `reel-720.mp4`
  (9:16, on portrait screens), fetched after `load` and paused off screen, with
  the live HU/EN lines, client tags and counted numbers (`.rcue[data-t]`) on
  the film's clock and a cursor play/pause disc. `SS.reel` in `ss.js` drives it
  in all three designs. Here it is the first snap point; the profile panel and
  the actions rail arrive with the first post.
- **Feed.** `html { scroll-snap-type: y mandatory }`; each `.post` is a flow
  act with a 9:16 `.frame` (`--fh`). The post on screen sets `body[data-post]`
  and fills the story bars. Behind the frame on wide screens, the post's
  `data-amb` image is blurred into an ambient wall that drifts with the cursor.
- **Chrome.** On wide screens a profile panel (stats, bio, highlights that jump
  to posts) and an actions rail: like, the comments sheet (the testimonials,
  verbatim), save to topics, audit. On phones the rail sits over the post and
  steps aside on the text posts and an open story.
- **Captions.** `.cap` lines are split into words and the active word is
  highlighted on the clip's clock (`splitCaps` rebuilds them from `data-hu` /
  `data-en` when the language changes).
- **Clips.** `feed-*.mp4` (540×960) are cut from their FlyX and Gyenis András
  footage with `video/feed-*.json` and the cut tool from socialstream-split;
  every video loads only on its post and pauses off screen.
- **DM audit.** `STEPS` asks for name, email (validated), brand, web
  (skippable), budget, goal and interests (pre-ticked from saved topics), then
  a message; `finish()` composes the email (`SS.compose`), opens the mailto and
  offers send and copy buttons.

## Checks

`lab/shots.mjs <outdir> <w> <h> [m]` (run from a folder with `playwright-core`,
e.g. `../socialstream-split`) walks the posts, swipes a carousel, opens a
story, answers the poll and starts the DM, then prints page errors and
horizontal overflow. Last run: no errors, no overflow at 1440×900 and 390×844.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html` (the stylesheet and scripts
inlined, `<html>`/`<head>`/`<body>` stripped for the claude.ai Artifact host);
`assets/` is published next to it.
