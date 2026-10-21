# SocialStream: Noir (the split stage, restyled)

The split-stage flagship in a quiet register: ivory paper for the dead age of
social media, warm black for the living age of interest media, the brand's own
Fraunces and Jakarta on both sides, and nothing moving in the divider but the
divider itself. What changed and why: [BRIEF.md](BRIEF.md). How the page works
(the river D(y), the marker, the dwell-time interest reveal, the collapse) is
unchanged from [the split build's README](../socialstream-split/README.md).

Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build
step. Hungarian by default, English through the HU/EN switch.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4522
```

## How it was made

`index.html` is the split build's page with the fonts swapped, a Noir override
block appended to its styles (palette, type, notice, buttons, peak cards), the
tile layer and phone bands hidden (`NO_TILES` in the river script, so no tile
is built or drawn), and the hero reel pointed at the stream film rendered on
black (`film-ink-1080.mp4` on desktop, `film-ink-720.mp4` on phones). The
split's real numbers, verbatim testimonials and copy are untouched.

The peak's two photo cards use Maison's warm-graded loop posters
(`t-pirate.jpg` is `loop-pirate.jpg`, `t-jump.jpg` is `loop-dance.jpg`) in
place of the split's petrol-graded tiles.

## Before launch

- The form hands off to the visitor's mail app (mailto to
  hello@socialstream.hu) with a copy fallback; it sends nothing by itself.
- `tools/artifact.mjs` packages the page for a claude.ai Artifact into `dist/`.

## Verification (this build)

- scroll-craft harness at 1440x900, 390x844 and reduced motion: no dead scroll,
  no console errors, every cue over media clears 4.5:1 at its worst frame.
- The split build's functional pass run against this page
  (`URL=http://localhost:4522/ node ../socialstream-split/lab/func.mjs`, from a
  folder with playwright-core installed): dwell, peak cards and chips, follow,
  carry into the form, validation, the mailto hand-off, EN with nothing
  untranslated, no overflow, the 720 ink film on phones, no stream bands.
- Not verified on a real phone or in Safari.
