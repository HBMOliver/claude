# SocialStream: Exhibition

The site opens on the client's own brand film, full screen, then becomes a
gallery at night where the cursor is the light. After the reel come the title
wall and seven rooms: the relics of the old age in vitrines, their work hung
salon style with museum labels, the services as a floor directory, the four
case still lifes with brass plaques, portraits with name plates, a guestbook of
testimonials, and the desk, where the audit is an admission ticket. A switch in
the bar turns the gallery lights on. One of three structurally different
designs (with [socialstream-edit](../socialstream-edit/) and
[socialstream-feed](../socialstream-feed/)) made after the client turned down
socialstream-studio.

Static: `index.html`, `ss.js` (language, helpers, the film and the audit
hand-off, shared with the other two designs), `scrollcraft.css`,
`scrollcraft.js`, `assets/`. No build step. Hungarian by default, English
through the HU/EN switch (remembered in `localStorage`). Charcoal walls, ivory
mats, brass; Instrument Sans.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4542
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
  the film is a light source, so it sits above the dark, and over it the cursor
  is its disc rather than the light.
- **The light.** `.night` is one fixed radial gradient over the page; a rAF
  loop eases its centre toward the pointer (`--x`, `--y`, radius `--r`). Until
  the visitor moves, it rests at the centre. On touch screens it is a torch
  fixed at the centre and the rooms scroll through it. "Villany" fades the dark
  out.
- **Rooms.** Every room is a flow act with `data-sc-in` reveals. The FlyX ad in
  room II plays while it is in view. The plaques count once when first seen.
- **The ticket.** Checks name, email and company, then opens a mailto to
  hello@socialstream.hu carrying every field and the ticked interests, says
  what happened, and offers "Szöveg másolása" in case no mail app opened. The
  address is always visible with a copy button.

## Checks

`lab/shots.mjs <outdir> <w> <h> [m]` (run from a folder with `playwright-core`,
e.g. `../socialstream-split`) walks the rooms with the pointer, submits the
ticket empty and full, reads the composed email from the clipboard, turns the
lights on, switches to English and prints page errors, untranslated text,
overflow and page height. Last run: no errors, nothing untranslated, no
overflow at 1440×900, 1024×728 and 390×844; about 14 viewport heights on
desktop.

## Publishing

`node tools/artifact.mjs` writes `dist/index.html` (the stylesheet and scripts
inlined, `<html>`/`<head>`/`<body>` stripped for the claude.ai Artifact host);
`assets/` is published next to it.
