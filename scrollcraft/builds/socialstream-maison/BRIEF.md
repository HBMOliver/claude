# BRIEF: SocialStream Maison (luxury direction A)

**Why this build exists.** The client saw the split-stage flagship and said it
was an interesting concept they did not like: they want SocialStream to feel
like a luxury, high-end brand, and the earlier cream site
(`socialstream-site`) looked better. They asked for three designs: two that
take the cream site up to high-end luxury (this is one, `socialstream-journal`
is the other) and one that restyles the split concept (`socialstream-split-noir`).
For the hero they asked for something in the spirit of Social Chain's
feed-of-videos hero, but made unique and more theirs.

Brand stays **SocialStream**, and so does their message: *A social media
meghalt. Az érdeklődés vette át a helyét.* Copy is theirs from the cream site,
word for word where it existed.

## The eight topics

1. **Vibe**: a fashion house's site, not an agency's. One cream ground, a great
   deal of space, Fraunces at light weights, one dusty blue, hairline rules,
   nothing that blinks for attention. References: a maison's lookbook page, a
   gallery wall label, a hotel's night-time reception.
2. **Journey**: film → the manifesto → one wide photograph → three laws → their
   work, which plays when you stop on it → six services → numbers and client
   words → the founder and the team → who we work with → the audit, at night.
3. **Energy**: composed open, calm read, one wide breath, conviction, play,
   relief, trust, warmth, respect, then a quiet decision.
4. **Feeling and the one moment**: see the curve. The moment is the thumb stop.
5. **What no other site does**: the page answers you stopping. While you scroll,
   their work is six stills; the card you stop on comes alive, the way an
   interest feed rewards the thing you paused on.
6. **Range**: quiet luxury. Fraunces + Plus Jakarta Sans on cream, ink and one
   dusty blue (the client's own palette, taken further apart).
7. **One world or scenes**: one ground for the whole page. Sections are separated
   by space and hairlines; the only change of ground is the night audit.
8. **Assets**: the FlyX Tenerife iPhone footage ("Internal Promo Material"),
   studio portraits of Olivér, David and Lidi, the founder portrait from the
   cream site. No generated imagery.

## Grammar

**Maison** (named new). An all-flow page on one ground with no pins and no
scrub: a looping film opener, then quiet spreads, then one night section that
holds the application. None of the eight grammars fits. Filmic one-shot needs
pinned scrub acts and a spotlight close, and the client asked for calm.
Chaptered editorial forbids media above the fold, and here the film is the
first impression. Gallery forbids the argument this page makes. Split stage is
the build they turned down. Live surface, continuous world, typographic poster
and cutlist are all louder than "luxury".

**Bans held**: no pinned type acts, no scrub, no drift, no spotlight, no magnet,
no counters that loop, no autoplaying sound, no carousel.

**Nav**: a centred masthead, not a menu: HU/EN on the left, the serif wordmark
in the middle, one text link ("Ingyenes audit") on the right. No anchors: a
maison's page is read top to bottom, and the bar's only job is the name and the
one action.

## Feeling curve

| # | Act | Feeling | What causes it |
|---|---|---|---|
| 1 | Film | Intrigue | Their own footage moves like a feed, stops, and one moment blooms to full frame; the four manifesto lines arrive with the blooms |
| 2 | Manifesto | Clarity | "A social media meghalt. Az érdeklődés vette át a helyét." in two calm columns, ending on "A stream maradt. Ami benne folyik, az változott." |
| 3 | Photograph | Breath | FlyX auditorium, full bleed, one caption |
| 4 | Laws | Conviction | Three numbered laws side by side |
| 5 | Thumb stop | Delight | The card you stop on plays |
| 6 | Services | Relief | Six services as a quiet list beside a sticky lead |
| 7 | Results | Trust | Four real numbers counted once, three clients in their own words |
| 8 | People | Warmth | Olivér's story beside his portrait, then the team |
| 9 | Fit | Respect | Who we work with and who we don't; two partners a month |
| 10 | Audit | Decision | The only dark section: the question and the application |

No two adjacent acts share a feeling.

**The moment**, as a visitor would say it: *"I stopped scrolling and the video I
stopped on started playing."* Act 5, placed after the laws so it lands as proof
of them.

**Tell-someone sentence**: *It's the agency site that looks like a fashion
house, and their work only plays when you stop on it.*

## Signature move

**The thumb stop.** Six 9:16 cards of their work stay still while the page
moves. 380 ms after scrolling stops, the card nearest the centre of the screen
plays its loop, lifts slightly and its dot turns blue; a live line says what you
are watching. Scroll again and it stills at once. A click plays any card by
hand. Under reduced motion nothing plays by itself; the cards still play on
click. Loops load only when first played.

## Fingerprint gate

Against every row in `scrollcraft/FINGERPRINTS.md`, dimensions in order:
grammar, nav, hero, act sequence, close, signature.

| Row | Differs on | Count |
|---|---|---|
| hb-social | all six | 6/6 |
| socialstream rev 2 | grammar, hero, sequence, signature. Shares a fixed bar with wordmark, HU/EN and the audit, and a dark close with the question and the scarcity line | 4/6 |
| socialstream-site | grammar, hero, sequence, signature. Shares the fixed bar and a dark form close | 4/6 |
| socialstream-cobalt | all six (its close is a paper form ending on a wall-to-wall wordmark) | 6/6 |
| socialstream-split | all six | 6/6 |

Passes: at least 4 of 6 against each row. The fixed bar and the dark form close
are now worn by three builds of this brand and should count as taken.

## Score

| Beat | Device | Why |
|---|---|---|
| Film | `flow`, film on its own clock, lines switched by `data-beats` | A film to watch, not to scrub |
| Manifesto | `flow` + `in` | A read |
| Photograph | `flow` | Space |
| Laws | `flow` + `in` stagger | Three equal statements |
| Thumb stop | `flow` + bespoke JS | The signature needs the page to be still, not pinned |
| Services | `flow`, sticky lead | A list to scan |
| Results | `flow` + `in` + `count` once | Real figures |
| People | `flow` + `in` | Faces |
| Fit | `flow` + `in` | Two honest lists |
| Audit | `flow`, night ground | An input, not a button island |

About 12.7 viewport-heights on desktop, 16.4 on a phone, 10 acts, all flow.

## Hero film

The stream film, made for these three builds from their FlyX footage: 26
vertical cards drift up like a feed; four times per 24 s loop the feed stops and
one card blooms to full frame and plays (23_IMG_0871, b148_IMG_0474,
b216_IMG_6214, 37_IMG_1193 on desktop; the phone cut swaps in two shots that
hold a vertical frame). Rendered on the page's own cream, so the cards appear to
float on the page. The film carries no text: the four manifesto lines are live
HU/EN HTML over a soft scrim, switched on the film's clock. Desktop gets the
16:9 cut, phones the 9:16 cut. Recipe in `video/`.
