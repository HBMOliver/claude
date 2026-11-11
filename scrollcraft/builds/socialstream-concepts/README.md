# SocialStream: four concepts

Four whole-page concepts for SocialStream, built from ideas in six Framer sites the client sent
(Talentank, Conversion, Cutflow, Marketia, Strivai, Scrolla). They share the words and the working
parts; each one has its own markup, structure and look.

| Concept | Lead reference | Look | Published |
|---|---|---|---|
| Pulse | Scrolla | White page, black rounded panels, one hot rose. Reel cards float round the claim. | https://claude.ai/artifact/D7G86aKgXU2nqcDZgQKA8e |
| Premiere | Talentank (Marketia for the giant running words) | Black and cinematic. The claim's two sentences sit above and below a wide film band. | https://claude.ai/artifact/F4yHZA3CbyoiQ7mN5ckVmT |
| Aurora | Conversion (Strivai for the horizon light and the glass) | Night blue with a moving aurora. Real results float on glass cards. | https://claude.ai/artifact/PtcSvRhunabu4nDLBXoL82 |
| Studio | Cutflow | Warm grey with white cards and one coral. The film plays like a story, with reels peeking out behind it. | https://claude.ai/artifact/2GpEg95SqLphnNoG937xu2 |

The published pages are private until they are shared from their Share menu.

## What every concept keeps

- **First screen:** the claim is the headline: "A social media meghalt. Az érdeklődés vette át a helyét."
  - "social media" is struck through the middle.
  - The free-audit button is beside it.
  - Tenerife and Budapest are not on it.
- **Language:** Hungarian first, with an EN switch.
- **Numbers:** only the real ones (see `content.mjs`).
- **Testimonials:** word for word.
- **Contact:** the audit form writes an email to hello@socialstream.hu, the same as in Daylight.
- **Business problems:** one for each service, in their own block before the services. Each one links
  to the service card that answers it (new, see COPY.md).
- **Motion when nobody scrolls:**
  - the brand film
  - running rows
  - floating objects
  - each concept's own loop
- **Cursor:** each concept has something on its first screen that follows the mouse, and its buttons
  pull toward a cursor that comes near.
  - Phones have no cursor, so their pages keep their own motion.
  - With reduced motion, nothing follows and nothing loops.

## Files

- `content.mjs`: every word in both languages. Each service carries its `pain`, the problem it answers.
- `parts.mjs`: shared markup (claim, film, reel, rail, form, questions, footer, `toSvc` link).
- `concepts/<name>.mjs`: each concept's own page.
- `base.css`: shared mechanics.
- `<name>.css`: each concept's look.
- `ss.js`: language, form helpers. Copied from Daylight.
- `kit.js`: the behaviour the concepts share:
  - arrivals and counters
  - the film
  - running rows
  - lighting words
  - scroll drift
  - the cursor light
  - `[data-follow]` followers and magnetic buttons
  - the menu
  - the audit form
- `build.mjs`: writes `pulse.html`, `premiere.html`, `aurora.html`, `studio.html`. It stops on an em dash
  in visible copy.
- `tools/artifact.mjs`: packages each page for claude.ai.
  - `dist/<name>/index.html` with styles and scripts inlined.
  - `dist/<name>/files.json`, the assets to publish with it.
  - `dist/<name>.html`, a local test wrapper.
- `lab/check.mjs`: checks each page on desktop and phone without looking at it:
  - first screen, strike line, film and its button
  - running rows, counters, the form, English
  - the problems and their links, cursor followers
  - reduced motion, no sideways scroll

## Run

```bash
node build.mjs
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4560
node lab/check.mjs
node tools/artifact.mjs
BASE=http://localhost:4560/dist/ node lab/check.mjs
```

The checks need `playwright-core` and Google Chrome. The fourth command packages the pages, and the
last one runs the same checks on the packaged pages.
