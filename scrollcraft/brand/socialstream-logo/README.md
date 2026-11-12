# SocialStream logo concepts, round 1

Four directions, shown before any logo kit is built. Start with `concepts.png` (greyscale on purpose) and
`colour-hint.png` (the recommendation in the brand film's palette). The brief, clichés and longlist are in
`brief.md`.

| | Concept | Structure | One-line idea |
|---|---|---|---|
| **A** | Italic i (recommended) | wordmark only; the i is the proposed avatar | The i of interest turns italic inside Social: interest has literally taken its place. |
| **B** | Through the reel | monogram symbol + the film wordmark | The S of Stream passes through a 9:16 reel and turns it inside out. |
| **C** | One S | stacked lockup sharing one S | One S starts both words: upright for Social, leaning into italic for Stream. |
| **D** | The one that leans | abstract symbol + sans wordmark | In a grid of reels, interest is the one that leans out (on the site, toward the cursor). |

## Files

- `concepts/` masters: `<x>-symbol.svg` (256 × 256, one colour) and `<x>-lockup.svg` (height 256, ink + accent).
  All letters are outlined paths; no live text, rasters, filters or masks.
- `test/` the same marks in cream / on night blue, for checking dark grounds.
- `colour/` concept A in the film palette (cream #f1eee6 and blue #7fa1c4 on night blue #05070f).
- `renders/` PNGs: 512 px symbols, lockups on cream and night blue, `test-dark-light.png`
  (every mark at 160 / 64 / 32 / 16 px on both grounds), `audit.txt`.
- `preview/` the skill's test sheet (`preview.html`; `preview-full.png` is a screenshot of it): size ladder,
  16/32/48 px pixel test, backgrounds, one colour, reversed, blur, mirror, 180°, favicon, app icon, avatar
  crop, header, card, and a shelf test against social-category logos.
- `tools/` the scripts that made everything, so round 2 and the kit can be rebuilt (see below).

## Test results

- **Audit (`svg_audit.py`).** Symbols: A 99, B 100, C 100, D 100. Lockups: A 83, B 84, C 84, D 98.
  The Fraunces lockups are flagged for outline complexity (that is type, not a mark) and for edges about
  1–2° off 105°. That is Fraunces Italic's own ~16° slant, kept on purpose rather than skewed to 15°.
  D, a geometric mark, uses a clean 15°.
- **Small sizes.** A's italic i and C's S stay legible at 16 px but get thin; B and D hold their shape, but
  B's break-out terminals and D's lean fade below about 32 px. In the kit, each gets a small-size cut.
- **Grounds.** All marks work black on cream and cream on night blue (`renders/test-dark-light.png`).
  The film blue #7fa1c4 has 7.5:1 contrast on night blue but only 2.3:1 on cream; light grounds need a
  deeper blue (about #45698c, 5:1). Deciding that is part of the kit.
- **Readings.** The mirrored and 180° views of all four show no unintended shapes (B never reads as a dollar
  sign). A's i turned 180° looks like "!", which is harmless. No concept puts two S's side by side (see the
  cultural check in `brief.md`).
- **Shelf.** Next to social-category logos (speech bubbles, birds, app glyphs) all four stand apart; D is
  the closest to a generic "grid" icon.
- **Familiarity.** Compared at equal size with the reference library's nearest marks: the grids of
  Microsoft, SendGrid, WP Engine and mParticle, Svelte's S, and the italics of PayPal and Forest Admin
  (`renders/familiarity-shelf.png`). None is close. The library is mostly tech brands, so this does not
  replace a trademark search.

## Risks, one per concept

- **A:** a lone i on an avatar can read as the "information" sign, it is an unmodified Fraunces glyph, and
  it is not the name's initial. C's S could serve as A's avatar instead.
- **B:** below about 32 px it becomes an S in a rounded tile, the container device that 41 % of the social
  category already uses, and a tall rounded tile can read as a phone.
- **C:** on its own the S passes for an ordinary serif S; the idea only shows in the stacked lockup.
- **D:** the closest to a stock grid icon, and its sans wordmark would no longer match the Fraunces title
  card in the brand film.

## How it was made

- Type: Fraunces (opsz 144, wght 400, roman and italic, the film's instance) and Plus Jakarta Sans 600.
  Both are under the SIL Open Font License 1.1, which allows logo use. The film's wordmark was matched by
  comparing against `scrollcraft/builds/socialstream-concepts/assets/hero-poster.jpg`.
- Outlines: `tools/glyphs.py` prints text with headless Chrome and reads the vector glyphs back from the PDF
  (Chrome writes variable fonts as Type 3 glyph procedures), so the marks use the exact Fraunces instance
  the sites load. The extracted outlines are kept in `tools/set1_out.json` and `tools/set2_out.json`.
- Drawn changes: A swaps the roman i for Fraunces Italic's i and tightens the l|S join; B is an even-odd
  overlap of the italic S and a 9:16 tile sized so every crossing is clean; C joins the top half of the
  roman S to the bottom half of the italic S with new spine curves (`tools/hybrid.py`); D is built from
  primitives, and its wordmark's tittle is a small leaning tile.
- Rebuild: `cd tools && python3 build.py ..` regenerates `concepts/`, `test/` and `colour/` from the stored
  outlines. Re-extracting outlines needs Chrome and network access to Google Fonts (and the Plus Jakarta
  Sans woff2 files at the path named in `set1-spec.json`).

## Open items

- Pick a direction (or a mix). Then the kit: refined geometry and optical corrections, small-size cut,
  light-ground colour, horizontal and stacked lockups, favicon / app icon / web icons, presentation board,
  one-page usage guide.
- Trademark: no clearance can be guaranteed here. Before launch, run a professional search in the HU/EU
  (EUIPO, HIPO) databases and a reverse image search.
