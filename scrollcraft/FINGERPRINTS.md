# Fingerprints

Every site you build with **scroll-craft** gets one row here, appended after it
ships. The registry exists so your next build can prove it is a different page
rather than a re-skin of one you already made.

This file is **yours**. It starts empty on purpose: the gate is about not
repeating *yourself*, so it has nothing to say until you have built something.

The rules and the gate live in the skill's
`references/uniqueness.md`. Short version:

**A new build must differ from EVERY row below on at least 4 of the 6
dimensions.** Four against each row individually, not four on average across the
table. If a planned build fails, change the plan. Never edit a row to make room
for it.

The six dimensions are: **grammar**, **nav treatment**, **hero device**,
**act-sequence shape**, **close pattern**, **signature move**.

Dimension 6 is free, because a signature move is unique by definition. So the
gate really asks for three more out of the remaining five, and a build that
changes only grammar and world will fail it.

---

## The registry

| Build | Grammar | Nav treatment | Hero device | Act-sequence shape | Close pattern | Signature move | World | Port |
|---|---|---|---|---|---|---|---|---|
| hb-social (HB Marketing /social) | Typographic poster | No bar; wordmark in hero composition; fixed bilingual HU/EN switch is the only chrome | Pinned 4-plane typographic depth: rendered satin plate, 27vw "Atelier", scrimmed copy, stroked 78vh ampersand, each at its own scroll + pointer rate | pin(1.25) > flow+in > flow+reveal wipe > pin custom (3.2, peak) > flow details index > flow reveal staircase > flow close; 7 acts, hard grounds oxblood/bone, no drift | Inverted quiet close: smallest type, CTA as underlined Bodoni line on oxblood with satin rising from the bottom edge | Grid takeover: nine scattered tiles fly home in Instagram publishing order and lock into one composed picture | Procedural oxblood satin (numpy-lit heightfield), Bodoni Moda + Hanken Grotesk | 4500 |
| socialstream (rev 2 of hb-social) | Chaptered editorial (client's own I./II./III. chapters), bent for a fixed bar | Fixed paper bar: wordmark, 4 anchors, HU/EN, Ingyenes audit | Pinned photographic depth: wall plate, 22vw italic 'érdeklődés' behind a rembg cutout of the founder, claim in front, pointer + scroll rates | pin(1.35) > marquee > flow+in > flow reveal laws on dark linen > pin custom (3.0, peak) > flow index > pan rail with scrubbed counts (3.2) > flow mosaic > native snap rail > flow team > flow founder > flow close; 12 acts | Dark linen close: big question, cream pill CTA, visible address, scarcity line, footer inside | Grid takeover reused by client request, recast as the third law (old-age scatter to new-age system) | Client brand: cream, ink, dusty blue; Fraunces + Plus Jakarta Sans; real portraits | 4501 |

*(empty: your first build has nothing to clear, so build whatever the interview
points at. From the second onwards, this table is the constraint.)*

---

## What is taken

Add a bullet here whenever a build claims something a later build should avoid
reusing: a grammar, a nav treatment, a close pattern, a signature move, an
act-count-and-length band. The shared columns are what the next build inherits
as a constraint, so writing them down is the whole point.

Nothing is taken yet.

---

## Appending a row

After shipping, add one line to the table and one bullet to **What is taken** if
the build claimed something new. Fill every column. Say what the build shares
with existing rows.

Rows are append-only. A build that has been superseded stays in the table,
because the space it occupies is still occupied.

---

## Worked example

The skill's author kept a registry of twelve builds across eight page grammars.
If you want to see what a filled-in table looks like, and which shapes tend to
collide, read `EXAMPLES.md` in the scroll-craft repository. Treat it as
illustration only: those rows are somebody else's builds and they do **not**
constrain yours.
