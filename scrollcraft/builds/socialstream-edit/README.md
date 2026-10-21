# SocialStream: Edit (rev 2)

The site is an editing suite. It opens on the client's own 30-second brand
film in full-screen preview; the first half screen of scroll leaves full
screen, the film docks into the program monitor and the inspector and the
timeline slide in. From there the scroll is the playhead through nine
chapters: the film, the three laws, services, results, testimonials, the team
and the export, which is the audit form. Rev 2 keeps the concept and replaces
the visuals: no footage beyond the brand film, every chapter a title card set
like the film's own.

Static: `index.html`, `ss.js` (language, helpers, the film and the audit
hand-off), `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build step.
Hungarian by default, English through the HU/EN switch. The brand film's
system: near-black, warm white, dusty blue `#7fa1c4`, a steel-blue field
`#7697b4` and cream `#f1eee6`; Fraunces for figures and the italic accent,
Plus Jakarta Sans for everything else.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4540
```

## How the page works

- **Leaving full screen.** The suite is one pinned act (10 viewport heights).
  Over the first 5% of it, `dockTick` moves the monitor from a full-stage rect
  (never cropped by more than 4% a side) to its slot with one transform, and
  `--chrome` fades the panels in. On phones the bars around the film glow with
  its colour (a 64×36 canvas fed from the film).
- **Title cards.** Each chapter is a `.card` in the monitor, sized in
  container-query units: Law I counts to 10 000 and strikes it, Law II fills a
  watch bar on the blue field, Law III strikes the old rules on cream, services
  are six drawings made in SVG, results are serif figures beside the case
  stills, testimonials run as subtitles, the team is the founder and three
  portraits, the export fills a render bar. Lines rise out of masks, in order.
- **Inspector.** The chapter's words; services, results and testimonials are
  lists that jump the playhead.
- **Timeline.** Titles, video (the film's own frames in `hero-strip.jpg`) and an
  honest empty audio track. Hover shows a live preview of the card under the
  cursor; click seeks; drag the playhead to scrub. On phones the playhead
  stays in the middle and the clips slide under it (a swipe scrubs). Arrow
  keys step chapters; Space plays the film.
- **Export.** On cream: name, email and company are checked, a render bar
  fills, then a mailto to hello@socialstream.hu carries every field, with a
  copy button in case no mail app opens.

## Checks

`lab/shots.mjs` is the scroll-through used in review (run from a folder with
`playwright-core`): no page errors, no horizontal overflow at 1440×900,
1024×728 and 390×844; about 12 viewport heights. The design skill's inspector
still flags the timeline's row rules, the title living in the app bar, and
few pictures (they are revealed one chapter at a time); all three are the
concept, not slips.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html`; `assets/` is published
next to it.
