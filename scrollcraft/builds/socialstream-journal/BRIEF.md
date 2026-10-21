# BRIEF: SocialStream Journal (luxury direction B)

**Why this build exists.** The client turned down the split-stage flagship as
not luxury enough and preferred the earlier cream site. Of the three designs
they asked for, this is the second that takes the cream site up to high-end
(`socialstream-maison` is the first; `socialstream-split-noir` restyles the
split). Their hero brief: something in the spirit of Social Chain's
feed-of-videos hero, made unique and more theirs.

Where Maison is a fashion house, the Journal is a printed issue: the agency's
argument set as a magazine they publish, with a cover, a contents page and a
reply card at the back.

## The eight topics

1. **Vibe**: a quarterly printed on good paper. Masthead type at 13rem, roman
   chapter numbers, plates with captions, letters from readers, a tear-off
   reply card. Fraunces + Plus Jakarta Sans on cream and paper, one dusty blue.
2. **Journey**: cover → manifesto spread → three laws as essays → plates of the
   work → services → numbers and letters → people → who we work with → the reply
   card.
3. **Energy**: recognition, clarity, conviction, wonder, relief, trust, warmth,
   respect, readiness.
4. **Feeling and the one moment**: see the curve. The moment is the reply card
   arriving with what you saved already ticked.
5. **What no other site does**: of every social gesture it keeps only one, the
   save. Laws, services and results each carry a quiet "Mentés"; saves collect
   in a tray and come with you to the reply card. The like is the old age; the
   save is the new one (their own law: what people keep is what interests
   them).
6. **Range**: luxury editorial, print.
7. **One world or scenes**: one paper world with a fixed contents rail; each
   chapter is a spread on the same ground, ruled off from the next.
8. **Assets**: the FlyX Tenerife footage (film and six graded plates), studio
   portraits, the founder portrait from the cream site. No generated imagery.

## Grammar

**Chaptered editorial** (uniqueness.md 2.2), bent in two places, both on
purpose: the contents rail is fixed rather than a margin folio, so the issue
can be navigated like one, and the cover carries the film as its cover photo
(2.2 asks for no media above the fold; a magazine cover is the one page where
the photograph is the point). Hard edges between chapters, media in its own
column with a caption, CTA as a card, no pins, no scrub, no spotlight, no
magnet.

**Nav**: the contents page is the nav. A rail on the left (1100 px and up)
carries the wordmark, the issue's contents in roman numerals with scroll spy,
the place line and HU/EN. Under 1100 px it becomes a sticky top bar with the
wordmark and HU/EN, and the chapters keep their own kickers ("iv. A munka").

## Feeling curve

| # | Act | Feeling | What causes it |
|---|---|---|---|
| 1 | Cover | Recognition | "Social / Stream" as a masthead, four cover lines switched on the film's clock, the cover photo is the moving stream film |
| 2 | Manifesto (ii) | Clarity | "A stream maradt. Ami benne folyik, az változott." and the argument, with the auditorium photograph |
| 3 | Laws (iii) | Conviction | Three numbered essays, each with a save |
| 4 | The work (iv) | Wonder | Six plates of their FlyX work, captioned like a gallery |
| 5 | Services (v) | Relief | Six services, each saveable |
| 6 | Numbers (vi) | Trust | Four counted figures, then four clients' letters |
| 7 | People (vii) | Warmth | Olivér's story, then the team |
| 8 | Fit | Respect | Who we work with and who we don't; two partners a month |
| 9 | Reply card (viii) | Readiness | The card already holds what you saved |

**The moment**, as a visitor would say it: *"I saved a few things while reading,
and at the end the reply card already had them ticked."*

**Tell-someone sentence**: *Their site is a magazine. You save what interests
you as you read, and the reply card at the back already knows.*

## Signature move

**Save, not like.** A save button on the three laws, the six services and the
four figures (13 in all), each tagged with a topic. Saves live only in this
tab's `sessionStorage`. The first save brings up a tray (count, list with
remove, "Viszem az auditba"). Every save adds its topic to the reply card's
interests; removing one takes away only the topics no other save still holds,
so anything the reader ticked by hand stays. The composed email lists the
saved titles ("Az oldalon mentettem: ...").

## Fingerprint gate

Dimensions in order: grammar, nav, hero, act sequence, close, signature.

| Row | Differs on | Count |
|---|---|---|
| hb-social | all six | 6/6 |
| socialstream rev 2 | nav, hero, sequence, close, signature. Shares chaptered editorial | 5/6 |
| socialstream-site | nav, hero, sequence, signature. Shares chaptered editorial and a form close carrying the visitor's own result | 4/6 |
| socialstream-cobalt | hero, sequence, close, signature. Shares a chaptered grammar and a fixed contents rail with scroll spy; its close ends on a wall-to-wall wordmark, this one on the card itself | 4/6 |
| socialstream-split | all six | 6/6 |
| socialstream-maison | grammar, nav, close, signature. Shares the stream film with live lines as the first screen, and an all-flow sequence of about ten acts | 4/6 |

Passes, narrowly against three rows. What it shares is now taken: a fixed
contents rail with scroll spy (with cobalt) and a close that carries the
visitor's own signal into the form (with the site and the split).

## Score

All `flow` + `in`, nine acts, about 14 viewport-heights on desktop and 17 on a
phone. Counts once on entry. The film runs on its own clock.

## Hero film

The 9:16 stream film from `../socialstream-maison/video/`, rendered on cream and
set as the cover photograph with feathered edges (a radial mask), 1080 wide on
desktop and 720 on phones.
