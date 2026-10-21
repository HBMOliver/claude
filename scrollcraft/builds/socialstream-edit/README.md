# SocialStream: Edit

The site opens on the client's own brand film, full screen, then becomes an
editing suite. One pinned act (9 viewport heights) holds a program monitor, an
inspector and a timeline, and scrolling moves the playhead through nine
chapters: the reel, the three laws, services, results, testimonials, the team
and the export. The export is the audit: a dialog with a render bar that hands
the application to email. One of three structurally different designs (with
[socialstream-feed](../socialstream-feed/) and
[socialstream-exhibit](../socialstream-exhibit/)) made after the client turned
down socialstream-studio.

Static: `index.html`, `ss.js` (language, helpers, the film and the audit
hand-off, shared with the other two designs), `scrollcraft.css`,
`scrollcraft.js`, `assets/`. No build step. Hungarian by default, English
through the HU/EN switch (remembered in `localStorage`). Matte graphite with a
brass accent; Inter Tight, Inter and JetBrains Mono.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4540
```

## How the page works

- **Film.** By client request the page opens on their own 30-second brand film,
  full screen: `hero-1080.mp4` (their file, 1920×1080, 25 fps, silent) or,
  where the frame is under about 1300 device pixels wide, `hero-540.mp4` (a
  960×540 copy at 1.1 Mbps made with the cut tool from socialstream-split). Its
  titles and numbers are in the film, so nothing is laid over it; they are
  Hungarian in either language. The frame is never cropped by more than 4% a
  side, and where that leaves bars a small canvas fed from the film fills them
  with its colour. `SS.reel` in `ss.js` drives it in all three designs. Here
  the transport bar runs its timecode and plays or pauses it (Space too), and
  the monitor picks the film up where the full-screen film left it.
- **Playhead.** The pinned `.suite` publishes `--sc-p`; `CH` lists the nine
  chapters and their share of the scroll. Inside a chapter a sub-progress steps
  through the services, the results and the quotes.
- **Monitor.** The film (`hero-1080.mp4`, or `hero-540.mp4` when the monitor is
  narrow) loads when the suite comes into view and plays muted. Each chapter
  lays a `.prog` overlay over it in container-query units, so it scales with
  the monitor. Law I counts to 10 000, strikes it, dims it, then the law
  arrives.
- **Timeline.** V1 is a 32-frame sprite of the film (`hero-strip.jpg`), T1
  holds the chapters as title clips (buttons that seek), A1 is a placeholder
  for Olivér's voice and says so. Hovering the timeline shows a preview frame,
  timecode and chapter; a click seeks; the arrow keys step chapters; Space
  plays the reel; over the monitor the cursor is a play/pause disc.
- **Export.** The audit form as an export dialog: it checks name, email and
  company, runs a short render bar, then opens a mailto to
  hello@socialstream.hu carrying every field. A copy button covers the case
  where no mail app opens; the address is always visible.
- **Phone.** The suite stacks (monitor, inspector, a one-column timeline); the
  timecode hides.

## Checks

`lab/shots.mjs <outdir> <w> <h> [m]` (run from a folder with `playwright-core`,
e.g. `../socialstream-split`) scrolls the suite, shoots each chapter and prints
page errors and horizontal overflow. Last run: no errors, no overflow, about
11.2 viewport heights on desktop and 12.3 on a 390 px phone.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html` (the stylesheet and scripts
inlined, `<html>`/`<head>`/`<body>` stripped for the claude.ai Artifact host);
`assets/` is published next to it.
