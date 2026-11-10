# SocialStream: Stream, in colour

Three colour versions of [Stream](../socialstream-stream/README.md), which
stays as it is. The same ordinary one-page site with one living figure, a
stream of exactly 10 000 vertical cards between the section grounds and the
text, but here the cards are posts: the nearer ones carry frames from the
agency's own client videos. The page has pictures of its own as well: a phone
that leaves the Following tab for the For You feed, two running rows of frames,
a small scene for each service, a still life beside each result.

Why, in the client's words: [BRIEF.md](BRIEF.md).

Static: `index.html`, `stream.js`, `ss.js`, `scrollcraft.css`, `scrollcraft.js`,
`assets/`. No build step. Hungarian by default, English through the HU/EN switch.

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4551
```

Then `http://localhost:4551/?look=riviera`, `?look=dusk` or `?look=paper`
(no look given: riviera).

## The three looks

A look is `data-look` on the root, set by the first script in the head from
`window.__LOOK` (fixed when published) or `?look=`. In the stylesheet a look is
three things:

1. Its colours, named once, and its shape decisions (`--r` radius, `--frame`
   the edge every picture gets, `--lift` what holds a card off the page,
   `--hw` headline weight, `--w1..--w4` four swatches with their inks).
2. Which field each section stands on: one rule per field, listing sections.
   A field restates everything on it: `--bg --fg --fg2 --fg3`, the accent word
   (`--em`, `--hl`), small accent text (`--tag`), drawings (`--line`), a panel
   (`--card`), and the stream's four colours there (`--s0..--s3`).
3. How the accent word looks: a tilted block (riviera), a gradient (dusk), a
   wavy rule (paper).

To add a look, copy one block and change it. To drop two, delete their blocks
and the two names in the head script and in `tools/artifact.mjs`.

## How the page works (what is new against Stream)

- **Fields and the bar.** `layout()` reads every `[data-field]` section's
  computed colours once: the stream's palette, the bar's ink and ground, the
  browser's theme colour. Nothing about colour is in the script. Each section
  also gets `--prev`, the field before it, which its round top corners show.
- **Pictures in the stream.** `assets/atlas.jpg` is 8 × 4 pictures, each 9:16
  like a card. A formation flags a card as a picture by adding 4 to its alpha
  (2 is the accent). Which picture is the card's own dice. A picture card is
  never soft or see-through: it grows and shrinks where a plain card would
  fade. Background cards are pictures from one depth up (`PIC_Z`), in every
  formation, and those keep to the page's margin (`pgap`, from `gutter()`), so
  a post is never under the text. Small cards take the field's ink or one of
  its two extra colours; `multi: 1` lets a figure's cards do the same.
- **Markers.** As in Stream, plus mode 9 in `data-into` (no travel: out in
  place, in in place) and `data-into-m` for phones, used where flying cards
  would cross text.
- **The phone** (`phoneTick`). The section's own travel is the clock: the
  Following feed slides out, the For You feed slides in, then five posts, one
  tag each, a heart per post. On a phone screen its own position is the clock.
- **The work rows** (`railTick`). Two rows of 24 frames, each written twice so
  the row has no end, moved by time and by the scroll in opposite directions.
- **Services.** `DRAW` holds one scene per service; pictures in it wait for the
  film like all others (`pic()`), then for their place on the page. On a phone
  the panel sticks under the bar and the list passes beneath it.
- **Headlines.** Every `.h-l[data-sc-in]` is split into words that rise out of
  their own line; punctuation after an accent word stays with it.

## Pictures

`p01.jpg` to `p24.jpg` are frames from finished client videos on the client's
own machine (FlyX Tenerife ads, the "Buddies" spot, Gyenis András reels), taken
at 486 × 864. Chosen for a clear caption and a presenter or a place; left out:
children in the foreground, guest reviews, end cards with prices, stock B-roll.
The script that cut them and built the atlas is not in the repo; to redo it,
take frames with `ffmpeg -ss <t> -i <video> -frames:v 1`, then paste 32 tiles of
180 × 320 into one 1440 × 1280 JPEG, row by row.

## Checks

Run from a folder with `playwright-core` (`../socialstream-split`):

```bash
LOOK=riviera node ../socialstream-colour/lab/func.mjs /tmp/out
Q='?look=dusk' node ../socialstream-colour/lab/shots.mjs /tmp/shots 1440 900
node ../socialstream-colour/lab/phones.mjs "http://localhost:4551/?look=paper" /tmp/audit i15
```

- `func.mjs`: every scene's state, the phone's feed, the rows, the services,
  the form, English, reduced motion, no WebGL, a phone. Passes in all three.
- `phones.mjs`: nine screen sizes, no errors, no sideways overflow, no cut
  text (run on riviera; the looks share one layout). On a throttled phone the
  film starts at 3.8 s, as in Stream.
- Text contrast was measured per look; small accent text was moved off yellow
  on blue and white on violet because of it.
- Not checked: real phones, and the published pages themselves (they are
  private until shared, so only the owner's browser can open them).

## Publishing

```bash
node tools/artifact.mjs            # dist/riviera, dist/dusk, dist/paper
```

Each `dist/<look>/index.html` is published as its own Artifact with `assets/`
beside it. Publishing the same file again keeps the link.

- Riviera: https://claude.ai/artifact/GR54VhMmGNH2u4dTf5txFQ
- Dusk: https://claude.ai/artifact/FP8h51VQk1dMJnc5jX2cwk
- Paper: https://claude.ai/artifact/U25ix1XNEVjh8iekHPWBka
