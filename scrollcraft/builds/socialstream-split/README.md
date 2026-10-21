# SocialStream: split stage (flagship)

The whole page is two columns held in tension. Left, the dead old age: grey
paper, monochrome, EB Garamond, opening on a real Hungarian gyászjelentés for
social media (2004–2022). Right, the living new age: petrol ground, amber, Mona
Sans, their own footage. Between them runs the stream, a river of tiles that
bends further left with every section until the old side is gone.

Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build
step. Hungarian by default, English through the HU/EN switch (`data-en`
attributes, remembered in `localStorage`, or `?lang=en`). Brief, journey,
feeling curve and fingerprint gate: [BRIEF.md](BRIEF.md).

```bash
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4510
```

## How the page works

- **The divider is a function of document position.** Every section carries
  `data-split` (the old side's share of the width) and pinned sections
  `data-split-end`. The script builds `D(y)` from those: plateaus where a
  section's content sits, smoothstep bends in the gaps, linear sweeps inside
  pins (the collapse sets its own window with `data-sweep`). Each `.pair` lays
  its two columns out against its own split in CSS, so copy never meets the
  boundary. The grey ground is one fixed SVG path redrawn from `D` on scroll.
- **The stream is a conveyor.** Tiles ride `D`, move with the page and drift
  downstream when idle. A tile's cargo is chosen when it enters, from the era of
  the document position it entered at: old-age junk above the name passage
  (like counts, "10 000 követő", "Jó reggelt mindenkinek!"), their real work
  below it (graded FlyX stills, the real numbers, the team).
- **The marker** rides the river at the top of the viewport: both sides'
  labels for the current section and each side's share. It is the only nav.
- **The interest reveal (signature).** `data-topic` on sections and on the six
  service rows. Every 250 ms the script adds dwell time for elements that are on
  screen, lit (cue opacity counted), with the tab in front and the visitor
  active in the last 20 s; opening a service adds 6 s. Stored only in
  `sessionStorage`; nothing leaves the browser. At the peak the top three topics
  fly out of the stream as a feed with the measured seconds, the visitor can
  correct them, and "Viszem az auditba" writes them into the form. A visitor
  who scrolled past without reading is told so and asked to choose.
- **The collapse.** The river swings off the left edge, the last old line is
  pushed out with it, "Social" docks against "Stream", and the audit form takes
  the winning column with the stream still running at the edge.
- **Phones and narrow tablets (under 1080 px)** are art-directed separately:
  every act is flow, each pair stacks as an old block, a horizontal stream band
  and a new block, and the old blocks shrink section by section. The peak plays
  once on arrival instead of pinning.

## Hero video

`assets/hero-1080.mp4` (8.9 MB) and `assets/hero-720.mp4` (4.3 MB, phones):
9:16, 21.4 s, silent loop, 41 hard cuts with punch-ins and two 60 fps
slow-motion holds, one LUT for the grade (petrol shadows, amber highlights,
violet cinema screens pulled to teal). Cut on this Mac with AVFoundation
(`video/cut.swift` + `video/edl.json`, which records every in-point; HDR HLG is
tone-mapped to Rec.709 by the reader). Sources: FlyX Tenerife iPhone clips from
"Internal Promo Material", "interveiw 6.0 j.mp4" cropped below its burned-in
captions, one shot of "6. rész.mp4" cropped clear of its captions. Not used:
the Robert Greene video; 3995c626 (over the Drive connector's 10 MB download
limit); 33f99312 (464 px wide, too soft at 1080).

## Copy notes

- Numbers are only the real ones: 81× ROAS, 79M Ft in a week, 23× holiday ROAS
  with 8M+ Ft, 105 Ft per registrant (~5700 from 600K Ft), 300M+ Ft managed,
  since 2022, Tenerife and Budapest, at most two new partners a month.
- Testimonials are word for word, split at their own sentence break into a
  before half (dead side) and an after half (live side). Four of them contain a
  gondolatjel; it is set as the Hungarian en dash (–), the correct mark in
  Hungarian typography, so there is no em dash in any visible copy.
- New copy written for this build: the death notice, the old rules and vendor
  ledger, the marker labels, "Kövess minket!" and its reply, the peak lines,
  "Mi embereket ismerünk.", the collapse and audit headings.

## Before launch

- The form opens the visitor's mail app (mailto to hello@socialstream.hu) with
  everything filled in, and offers a copy fallback. It does not send anything by
  itself; connect it to a form backend or CRM for production.
- `data-sc-world` on the fixed ground is there so the harness keeps the grey
  ground in its contrast shots (it is the background behind every old-side line).

## Verification (this build)

`lab/func.mjs` (dwell, peak, chips, carry, validation, mailto hand-off, follow,
EN, phone reveal) plus the scroll-craft harness at 1440x900, 390x844 and reduced
motion, 58 frames each: no dead scroll, no console errors, law cues measured at
11.1:1 (old side) and 10.6:1 (new side). Not verified on a real phone.
