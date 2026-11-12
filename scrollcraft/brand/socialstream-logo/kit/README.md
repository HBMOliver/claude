# SocialStream logo kit (direction G2)

A bold S on a 9:16 phone that leans in at 15°; its foot is sliced off at the same 15° as the A in SOCIAL.
Every cut and lean in the logo is 15°. The wordmark grows out of the team's shirt: SOCIAL heavy, STREAM light.

**Start here:** `guide/socialstream-logo-guide.pdf` (one page: versions, clear space, sizes, colours, type,
don'ts, which file) and `presentation/board.html` (slides as PNGs in `presentation/slides/`).

## Which file for what

| Use | File |
|---|---|
| Website header (light page / dark page) | `source/socialstream-logo-horizontal-light.svg` / `-dark.svg`; under 250 px wide use `socialstream-logo-horizontal-small-*.svg` |
| Favicon and app icons | everything in `web/`; paste `web/head-snippet.html` into the page `<head>` |
| Instagram, TikTok, Facebook profile picture | `social/socialstream-avatar-night-1080.png` (or `-cream-`) |
| Corner mark on reels | `source/socialstream-symbol-corner.svg` or `digital/socialstream-symbol-corner-256.png` (cream phone, night S: readable on bright frames too) |
| End card on reels | `social/socialstream-stacked-night-1080.png` |
| Shirts, merch | stacked or symbol, one colour: `print/socialstream-logo-stacked-white.pdf` on dark fabric |
| Embroidery under 40 mm | `source/socialstream-symbol-small-*.svg` (its slice stays above 1.5 mm) |
| Printer (cards, signs) | `print/*.pdf` (vector) + the colour table below |
| Decks, documents | `digital/*.png` (transparent, 512–2400 px) |

## Folders

- `source/` SVG masters, light and dark: horizontal (and its small-size cut), stacked, wordmark (one and two
  lines), symbol (and its small-size cut), the two-colour corner mark for video and the two-colour favicon
  drawing. Light = Night + Deep Stream (for cream/white grounds); dark = Cream + Stream Blue (for night blue
  and dark photos), drawn with the heavier S and wider slice.
- `digital/` transparent PNGs of every colour master and one-colour SVGs (+ PNGs of the symbol): black and
  night (`mono-05070f`) from the light drawing, white and cream (`mono-f1eee6`) from the dark drawing.
- `web/` `favicon.ico`, `favicon.svg`, 16/32/48 px favicons, `apple-touch-icon.png`, `icon-192/512.png`,
  `maskable-512.png`, `site.webmanifest`, `head-snippet.html`, the app-icon and square SVGs.
- `social/` 1080 px profile pictures on night and on cream (circle-safe), and a stacked square.
- `print/` vector PDFs (no images, no fonts) of the horizontal, stacked and symbol versions in light, dark,
  black and white. They are RGB: the printer converts or assigns CMYK/spot colours.
- `presentation/` the final board (`board.html`, `spec.json`, `slides/`).
- `guide/` the one-page guide as HTML, PNG and A4 PDF.
- `tests/` the audit report and the preview test sheet of the final symbol and its small cut.

## Colour

| Name | HEX | RGB | CMYK* | Use |
|---|---|---|---|---|
| Night | #05070F | 5 7 15 | 67 53 0 94 | dark grounds; the logo on light grounds |
| Cream | #F1EEE6 | 241 238 230 | 0 1 5 5 | the logo on dark grounds; light grounds |
| Stream Blue | #7FA1C4 | 127 161 196 | 35 18 0 23 | STREAM on dark grounds (the brand film's blue; 7.5 : 1 on Night) |
| Deep Stream | #40658C | 64 101 140 | 54 28 0 45 | STREAM on light grounds (5.2 : 1 on Cream, 6.1 : 1 on white) |

\* Plain conversions from RGB, not profiled: have the printer proof them. Pantone matches are not set; pick
them from a physical guide at the first print job.

## Type

Montserrat for headlines (ExtraBold caps for statements, Light for the second voice) and Plus Jakarta Sans for
body text; both SIL Open Font License. The logo's letters are custom outlines based on Montserrat, so the logo
cannot be typed: the A is sliced once at 15°, both S's have their terminals re-cut at 75° (parallel to the
tilted phone's sides), and the M's diagonals sit at exactly 60°.

## Design notes

- **The 15° rule.** The A's bar, the phone's slice, the phone's tilt and the S terminals (15° off vertical)
  all follow one angle; that is what makes the parts read as one mark.
- **Optical corrections.** The S sits 3 % of the phone's height above centre, so it is centred in the area
  above the slice. The reversed (dark) drawing uses a heavier S and a wider slice, so it does not look thinner
  on night blue. Spacing was evened by eye (C·I, O·C, T·R, R·E and A·M tightened).
- **Small sizes.** Below 32 px use the small cut of the phone (bigger S, wider slice), and below 250 px wide the
  small-cut horizontal lockup; below 140 px use the phone alone. Browser tabs get a two-colour drawing (night
  phone, cream S) so the favicon reads on light and dark tab bars; app icons use the cream small cut on Night.
- **Video.** The see-through S disappears on bright frames, so video gets a two-colour corner mark (cream
  phone, night S).

| Minimum size | Screen | Print |
|---|---|---|
| Horizontal | 250 px wide (small cut from 140 px) | 60 mm (small cut from 35 mm) |
| Stacked | 100 px wide | 25 mm |
| Phone | 32 px tall (small cut from 16 px) | 8 mm (small cut from 5 mm) |

## Tests

- `svg_audit.py` on every SVG in the kit: 92–100, no failures. The only remaining note is the anchor count of
  the stacked lockups (letter outlines). Report: `tests/audit.txt`.
- Corner mark on six of the team's reel frames, dark to bright (`tests/corner-on-reels.png`): the see-through
  phone fails on the brightest frames, the two-colour corner mark reads on all of them.
- Lockups rendered at their real minimum widths on cream and night blue: STREAM still reads at 140 px; the
  primary phone's slice fades below about 250 px wide, hence the small-cut horizontal.
- Preview sheet of the final symbol and small cut (`tests/preview.html`, `tests/preview-full.png`): size ladder,
  16/32/48 px pixel test, one colour, reversed, blur, mirror, 180°, favicon, app icon, round avatar, header.
- Earlier rounds checked distinctness against social-category logos and S app icons (`../round-2/`,
  `../round-3/`).

## Open items

- **Trademark:** no clearance can be guaranteed here. Before launch, run a professional search (HIPO for
  Hungary, EUIPO and TMview for the EU, which also covers Spain) and a reverse image search.
- **Print:** match Pantone colours and proof CMYK at the first print job.
- **Shirts:** sample the embroidery or screen print at the real size before an order.
- **Film and sites:** the brand film's title card and the website builds still show the Fraunces wordmark; swap
  in the new logo and favicon when they are next edited.

## Rebuild

```bash
cd ../tools
python3 build_kit.py ../kit          # masters in kit/source
python3 make_guide.py ../kit         # guide HTML; render with render_page.py
python3 pdf_export.py ../kit/print 180 ../kit/source/socialstream-logo-horizontal-light.svg
```
One-colour files, PNGs and web icons come from the logo-design skill's `export_variants.py` and
`render_png.py`; the board from its `presentation_board.py` (run with neutral placeholder names).
