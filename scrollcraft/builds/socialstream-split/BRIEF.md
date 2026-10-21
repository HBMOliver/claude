# BRIEF: SocialStream, split stage (flagship)

**Concept decided by the client; execution authored under that direction.** The
client fixed the grammar (split stage), the two sides, the stream divider, the
section pairs, the signature move, the close and the mobile treatment, and asked
for a re-cut vertical hero video. Everything below that is not in their words is
marked as an authored decision.

Brand stays **SocialStream**. Core idea, theirs: *Social media is dead. Now it's
interest media.* Their own line that the whole page is built on:
*"A stream maradt. Ami benne folyik, az változott."*

## The eight topics

1. **Vibe** (authored from the brief): unique, luxury, not generic. A real
   Hungarian funeral notice set against a living vertical feed. Dry wit on the
   dead side, energy on the live side. References: a printed gyászjelentés card,
   a river seen from above, a phone feed at night.
2. **Journey** (client): hero split as a death notice for social media vs the
   living interest media; laws I-III as old rule vs new law; services as six
   vendors vs one strategy; results as "Nem ígéretek." vs "Számok." with each
   testimonial split into a before half and an after half; people; who we work
   with vs who we don't; the dwell-time reveal; the collapse; the audit form.
3. **Energy**: amused open, calm explanation, rising conviction through the laws,
   relief and trust through services and results, a held breath, the peak, warm
   people, a quiet self-selection, then the collapse and a still form.
4. **Feeling and the one moment**: see the curve below. The moment is the peak.
5. **What no other site does** (client): it measures what you lingered on,
   locally, and tells you what interests you, without you ever following it.
6. **Range**: luxury editorial on the dead side, premium-minimal energy on the
   live side. Two grounds that hold for the whole page.
7. **One world or scenes**: neither. Two sides held in tension, one river
   between them that keeps flowing.
8. **Assets**: their FlyX Tenerife iPhone footage (Internal Promo Material, ~100
   raw clips), "interveiw 6.0 j.mp4", "6. rész.mp4", studio portraits of Olivér,
   David and Lidi. No generated imagery is used anywhere on this page.

## Grammar

**Split stage** (uniqueness.md 2.7), chosen by the client and the right fit: the
whole argument is two-sided. Filmic, chaptered, live surface, continuous world,
typographic poster, gallery and cutlist all lose because none of them can hold
the old age and the new age on screen at the same time, which is the point.

Bans honoured: no full-bleed anything before the resolve, no centred page copy
(the funeral card is an object whose own typesetting is centred, as real notices
are), no corner-anchored hero, no symmetric close, no pan, no spotlight, no
magnet, no drift, no scrub. Both columns carry real content the whole way down.

**The divider is the chrome.** No bar. A marker rides the river at the top of
the viewport carrying the labels for both sides of the current section and the
argument's progress (each side's share of the width). HU/EN switch is the only
other chrome.

## The river (authored mechanics)

The divider is a function of document position, `D(y)`, built from each
section's `data-split`: plateaus where a section's content sits, smooth bends in
the gaps between sections, and linear sweeps inside pinned acts (so in a pin the
divider is driven by scroll while the stage holds). Every section's columns are
laid out against its own plateau, so text never meets the boundary. The grey
ground is one fixed SVG path drawn from `D`; the petrol ground is the page.

The stream is a conveyor of tiles riding `D`: tiles move with the page and drift
downstream when idle; each tile's cargo is chosen when it enters, by the era of
the document position it entered at. Near the top it carries old-age junk
(like counts, follower numbers, "Jó reggelt mindenkinek!"); from the name
passage down it carries their real work (graded stills from the FlyX shoots,
the real numbers, the team). That is "A stream maradt. Ami benne folyik, az
változott." made literal.

## Feeling curve

| # | Act | Feeling | What causes it |
|---|---|---|---|
| 1 | Hero | Amused recognition | A real gyászjelentés for social media (2004–2022) beside a living vertical feed; the wordmark split by the river; "2022–" answers the dates |
| 2 | Name passage | Clarity | "Tíz évig az számított, hány követőd van" against today's feed; the river changes its cargo right here |
| 3 | Laws I-III | Conviction | Each old rule is struck through as its new law wipes in from the river; the divider steps left with each law |
| 4 | Services | Relief | Six vendors, six invoices, six reports vs one strategy you can open row by row |
| 5 | Results | Trust | Clients' own words, before on the dead side, after on the live side, with the real numbers |
| 6 | Peak | Being seen | "Ezt az oldalt nem követted. Mégis tudja, mi érdekel." Their own top topics leave the stream and become a feed |
| 7 | People | Warmth | The old age counted followers; here are three people with names and jobs |
| 8 | Fit | Respect | Who we don't work with, honestly, then who we do; two partners a month |
| 9 | Collapse | Resolve | The old column runs off the left edge and "Social" docks against "Stream" |
| 10 | Audit | Readiness | The form already carries the interests the page measured |

No two adjacent acts share a feeling.

**The peak**, as a visitor would say it: *"I never followed the page and at the
end it told me exactly what I'd been reading about, and it was right."* Act 6,
the largest span on the page (2.8 viewport-heights), after the results act,
which is flow and quieter.

**Authored silence**: the first ~12% of the peak's pin is deliberately near-empty
on the live side ("Kövess minket!" holds alone on the dead side) so the reveal
has something to arrive from. That is not dead scroll.

**Tell-someone sentence**: *It's the site where a funeral notice for social media
sits next to a living feed, and at the end the page tells you what you were
interested in, though you never followed it.*

## Signature move

**The interest reveal.** Topic-tagged sections (the six services) accumulate
dwell time in the visitor's browser only: visible on screen, tab in front, the
visitor active in the last 20 seconds, weighted by how much of the element is in
view, plus a bonus for opening a service. Nothing is sent anywhere; it lives in
`sessionStorage` and dies with the tab. At the peak, the top topics fly out of
the stream into a three-card feed with the measured seconds. The visitor can
correct it, and the result is written into the audit form. A visitor who
scrolled too fast is told so, honestly, and asked to choose.

## Fingerprint gate

Against every row in `scrollcraft/FINGERPRINTS.md`, dimensions in order:
grammar, nav, hero, act sequence, close, signature.

| Row | Differs on | Count |
|---|---|---|
| hb-social | grammar, hero, sequence, close, signature (nav shares "no bar + HU/EN switch") | 5/6 |
| socialstream rev 2 | all six | 6/6 |
| socialstream-site | all six (its close is also a form carrying a result, but the close pattern here is the collapse) | 6/6 |
| socialstream-cobalt | all six | 6/6 |

Passes: at least 4 of 6 against each row individually.

## Score

| Beat | Device | Why |
|---|---|---|
| Hero | `pin` 1.4 + independent planes + pointer depth | Establish 50/50 with both headlines readable; the dates beat lands on scroll |
| Name passage | `flow` + `in` | A read, not a show; the river does the work |
| Laws | `pin` 2.6 + `reveal` per side + struck rules | An argument; the balance tips once per law |
| Services | `flow` + working ledger | A surface to open, topic-tagged |
| Results | `flow` + `reveal` + `count` | Before halves and after halves wipe in from the river |
| Peak | `pin` 2.8 + bespoke JS | The signature; largest span |
| People | `flow` + `in` | Faces |
| Fit | `flow` + `in` | Two honest lists |
| Collapse | `pin` 1.5, divider driven by `--sc-p` | The resolve |
| Audit | `flow` (last act, holds) | An input, not a button island |

Total about 16 viewport-heights on desktop across 10 acts. This is a full site
with every real section the client has, so it runs long by design; no act is
filler. Mobile: hero, laws, people and fit become flow, the peak and the
collapse stay pinned and are recomposed as stacked blocks with horizontal
stream bands.

## Hero video

Re-cut as a 9:16, 21.4 s, silent loop of 41 hard cuts (punch-ins, two 60 fps
slow-motion holds), graded to the palette with one shared LUT: petrol shadows,
amber highlights, violet screens pulled to teal, filmic toe. Sources: FlyX
Tenerife clips (Internal Promo Material), "interveiw 6.0 j.mp4" cropped below
its burned-in captions, and one shot of "6. rész.mp4" cropped clear of its
captions. Robert Greene footage not used. Clip 3995c626 could not be fetched
(over the Drive connector's 10 MB limit); 33f99312 was checked and left out
(464x832 is too soft at 1080 wide). Headline is live HU/EN HTML on top.
Recipe in `video/`.
