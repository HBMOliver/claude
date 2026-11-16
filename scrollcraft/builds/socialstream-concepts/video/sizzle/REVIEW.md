# Review of drafts 4 to 6 (2026-11-16)

## Draft 6

The founder on draft 5: "its a bit too fast paste, also in english version convert the forints to euros".

**The calls I made.**

- *Pace.* The track has exactly 96 kicks between its drop and its end, so time given to one part is taken from
  another. Kept as they were: the hook (0-9.28 s) and the three client worlds (4 s each). Slowed: the claim after the
  drop now holds two bars and comes a line at a time (it was readable for little over a second); "how we work" has
  three bars, 1.5 s a phrase (was 1 s); 79 M Ft, 23× and ≈5 700 have six beats each (3 s, was 2 s) and build over
  their first beats before they hold; the reviews land one a second (was two a second), the first under "Nekik.",
  and the full stack holds 2.2 s. 81× and 300M+ stay at 2 s. Inside the worlds the events are spaced out: FlyX's
  comments land a beat apart and then stay 1.5-2.5 s (in draft 5 the third was on screen for 1.1 s), Prof Enzo's four
  counts come as two pairs, the productions' tags as one wave. 59.40 s (was 49.40).
- *Sync.* Measuring the track's kick drum showed drafts 4 and 5 were cut to a grid a quarter of a second early: in
  draft 5's render the effects of the turn peak at 9.28-9.32 s and the track's first kick comes at 9.50 s, and every
  later hit sat on the off-beat. Draft 6 enters the track 0.224 s later and uses the measured beat (0.49587 s), so
  every hit is on its kick, and an effect that belongs to a beat is placed on the kick itself.
- *The ending.* The film now ends where the track ends: its last kick is beat 95, the logo lands on beat 96 with
  the cinematic hit, in the track's own ring-out. (Draft 5 faded the music out under the logo.)
- *Euros.* Every figure at the ECB rate of 13 November 2026 (365.6 Ft): revenue and budget rounded down (€216K,
  over €21K, €820K+), costs rounded up (€1,650, €0.29); `SPEC.md`, Honesty, has each pair. The first render used
  a cautious 400 Ft for revenue and budget (€197K, over €20K, €750K+); shown both, the founder chose the current
  rate ("Use today's rate"), and the English cut was rendered again (draft 6b, below). The English site still
  shows forints.
- *Not asked for, and done anyway.* The sync and the ending above. The comment cards in FlyX's world are marked
  "Komment" only (they said "Komment · FlyX Tenerife" three times under a headline that already names FlyX).
  The V89 ad's tile on the wall of reels ran into the brand's shop page (its logo, and a line with "35.000 FT"),
  small but readable, at the bottom of the frame in the hook and under the logo at the end; the tile now shows
  the gift box and the watch only (the ad's 3.0-7.6 s, slowed to the wall's 8 s).

**Measured.** `hyperframes check`: no errors in either cut. 1485 frames, 59.40 s. Both masters: -14.7 LUFS, true
peak -1.2 dBTP; the review copies carry the masters' sound untouched (23.4 and 23.3 MiB, video 3.4 Mbps). In the
rendered film the kick's low-band rise is within 3 ms of the film's beat at each of the 17 beats sampled from 1
to 95; at the drop the kick's click falls at 9.27-9.29 s; the logo's hit at 56.88 s. A search of the English
project's files finds no "Ft" (in the footage, the reels keep their own Hungarian captions). The Hungarian words
are draft 5's in every scene but one: the "Komment" label above.

**Looked at.** 27 Hungarian and 12 English stills at 640-960 px (listed in `SPEC.md`, QA) and, from the rendered
master, strips of frames across the drop, the wipe into FlyX, the polaroids leaving, the door into the numbers,
the stack stepping up, the wipe into the promise and the logo's hit; six frames of the hook and two of the close
from the final render, with the recut tile. **Not watched at speed, not on a phone, and not heard by anyone**:
the sound was measured only.

**Draft 6b (English only).** The euros at the 13 November rate. Four lines of the project changed (the chip in
`how`, the counters' targets in `r1`, `r3` and `m300`). `hyperframes check`: the same as draft 6 (no errors, the
same three craft warnings). 1485 frames, 59.40 s. The sound stream is byte-identical to draft 6's English master,
so its loudness and sync measurements stand. Frame by frame against that master the picture differs only at
28.20-29.64 s, 31.28-33.96 s, 36.56-38.92 s and 42.04-43.88 s: the four numbers. Looked at, from the render: the
chip, €216K mid-count and held, the pill mid-count and held (and enlarged from the project), €820K+ mid-count and
held. Review copy: `drafts/sizzle-draft6b-wide-en.mp4` (23.3 MiB). Not watched at speed and not heard, as before.

**Draft 6c (both cuts).** Prof Enzo's number is the founder's: 9,828,876 views on Meta's dashboard for the page,
shown as "9,8M+" / "9.8M+" (`SPEC.md`, Honesty), counted up in tenths of a million and landing on the same kick
as "1M+" did. I changed the scene's eyebrow from "Facebook-reelek" / "Facebook reels" to "Facebook" without being
asked: the figure is the dashboard's "All views" (reels, posts and stories), so it cannot sit under the word
"reels". 1485 frames, 59.40 s in both cuts; the sound streams are byte-identical to the masters before; the
picture differs only at 17.20-21.68 s. `hyperframes check`: no errors; the same craft warnings as draft 6, and a
new `contrast_aa_failure` on the words of FlyX's comment cards at 16.5 s, which is the check's own error (it
measures their dark type against the film's night ground, not against the white card they sit on; the still at
16.5 s shows them as before, and that scene's file did not change). Masters: `master-wide-hu.mp4` and
`master-wide-en.mp4` in this folder (not in git); review copies `drafts/sizzle-draft6c-wide-hu.mp4` and
`-en.mp4`. Not watched at speed and not heard.

**The upright cut (1080 x 1920, Hungarian and English).** Asked for by the site session after the founder chose
the sizzle as the site's hero film ("Replace the hero film"): the site's card and phones need it upright, on the
wide cut's exact clock. The founder has not seen this layout; the site session shows it to them when it goes
live.

- *How it is built.* The same `build.py`, the same beat constants and the same scripts: a scene takes its upright
  positions inside its own function, and the five results are laid out again and keep the wide scene's script.
  After the change the wide projects are byte-identical (`git diff` on `wide/` and `wide-en/` is empty).
- *The calls I made.* A safe box, x 100-980 and y 230-1750, because the site fits the film with `object-fit:
  cover` and a phone's shape cuts up to 9 % off the sides or off the top and bottom (`SPEC.md`). Prof Enzo is a
  profile's grid of six reels instead of three tall ones; the productions are a collage round the smartwatch ad;
  the six reviews all stay in the frame; the turn has its own 9:16 window on the 4K cinema shot (the middle head
  and the sunlit cliff; nobody's face). "300M+ Ft" is too wide for the frame at any size worth having, so "Ft"
  starts the line under it.
- *Measured.* Both masters: 1080 x 1920, 1485 frames, 59.40 s, and a sound stream byte-identical to the wide
  masters'. The clock, on the built projects: identical timing in `index.html` and in 306 animation calls a
  language, but for Prof Enzo's three more cards (`SPEC.md`). The safe box holds at each scene's start; the
  results' 3 % push carries an eyebrow's first letter and the week's outer days up to 13 px past it by the end.
  `hyperframes check`: no errors in either. Warnings: the two reading-time lines the wide cut has
  (the last review; in English "what they bring in."), the "Komment" labels under the type floor (24 px), and
  three more on those labels ("on screen 0.12 s"), which is the check counting each typed word as a new line:
  the labels stay for as long as their cards.
- *Looked at.* Stills from the projects at a phone's width (360 px) and at 540 px with the safe box drawn on
  them, every scene in both languages (`SPEC.md`, QA), and 40 frames from the two renders, with the wipes,
  the counts in mid-run and the hits. **Not watched at speed, not on a phone, not in the site's card.**
- *Weakest shots.* (1) The hook's wall is four cards across instead of nine, so each card is nearly twice the
  size (see "The upright wall without FlyX's owner", below). (2)
  "How" is quiet: two lines and a small ring in a tall night frame. (3) The numbers are 250-400 px where the
  wide cut has 440-580: the frame is narrower. (4) In the site's card (about 360 px) the eyebrows, the tags and
  the "Komment" labels are texture, not text.
- *The loop.* The page loops the film from the logo to frame 0: the logo on the dimmed wall, then the bright
  wall without it, then the logo builds again. It reads as a restart, with the logo twice in five seconds; a
  softer join is to loop back to 3.2 s after the first play (`SPEC.md`). Not changed: that is the site's call.
- Masters: `master-tall-hu.mp4` and `master-tall-en.mp4` in this folder (not in git); review copies
  `drafts/sizzle-draft6c-upright-hu.mp4` and `-en.mp4` (the first render; `-draft6d-` after the change below).

**The upright wall without FlyX's owner (same day).** A correction first. I wrote here, and told the founder and
the site session, that in the wide frame FlyX's owner is "half out of it". That was wrong: I had taken the card
under the middle one (s04, a landscape) for his, without looking at the cards. Looked at one by one, he hosts
five of the wall's cards: the stills s01, s02 and s03, the playing w02 from its third second ("WATCH TILL THE
END", then "DO FLY X", the frame it freezes on), and the last second of w03 ("ALL IN 30 MINUTES", also the frame
it freezes on). In the wide cut the founder approved, w02 stands left of the middle card and s02 right of it,
both whole, w03 is two thirds in the frame, s01 a quarter, and w02's frozen frame is one of the six cards in the
"how" ring. So the wide cut shows him in more of the frame's cards than the upright one did; what the upright
frame changes is their size.

The site session asked for him to leave the upright wall (he is in a phone at 15 s, and `SPEC.md` bans a face
in more than one world; the wall and the ring are collages of reels, which is why that ban had not been applied
to them). Done in the upright cuts only: three stills of FlyX's cinema screen (s18 a sunset, s23 a helicopter, s27 a coast;
nobody's face; the team's own phone clips and their FlyX promo, filmed in the cinema, sources in `SPEC.md`) stand where w02, s02 and s01 stood, so that wall plays ten reels, not eleven; and the
edit suite (s21) takes w02's card in the ring. w03 stays: 5-8 % of that card is in the upright frame. Not
considered: the Miskolc promo beside the middle (its presenter is already in the ring and in the productions),
the smartwatch ad there (a black first second beside the logo), a Prof Enzo reel there (two beside each other).
The wide cut is unchanged and still shows him in those cards: taking him out there means rendering the two wide
masters again. Asked whether to do that, the founder answered "Leave the wide cut" (2026-11-16).

Measured: both new masters 1080 x 1920, 1485 frames, the same sound stream; against the first upright masters
the picture differs only where the wall or the ring is on screen. Looked at: 0.0, 0.5, 1.2, 2.4, 3.6, 5.8, 7.9,
9.0, 25.8, 53.4, 56.0 and 59.36 s from the project, and frames from the renders.

**Weakest shots.** (1) The turn is one shot for four seconds: a breath after the hook, by design; if it reads as
slow it can go back to one bar and the bar can go to 81× and 300M+. (2) 81× and 300M+ still pass in 2 s each.
(3) Once five reviews are in, the oldest card is cut by the top of the frame as it leaves. (4) The last review is
readable for 2.1 s, and the English "what they bring in." for 1.1 s before the camera goes through it. (5) The
music stops by itself a beat before the logo; whether the effect carries that moment has to be heard. (6) The
film does not loop seamlessly. (7) In the English cut the 1 of €216K stands a little apart from its neighbours: a
counter's digits sit in equal boxes (the 1 of €197K did the same).

**Warnings kept on purpose.** `line_unread` (the check's rule: 0.5 s + 0.3 s a word): draft 5 as committed has 13 such
lines in Hungarian and 15 in English; draft 6 has 2 in each. Left: the last review (2.1 s against a floor of 2.2 s in
Hungarian, 2.4 s in English); in English "what they bring in." (1.1 s against 1.3 s); in Hungarian the eyebrow over 79
M Ft (the giant digits' line box overlaps the eyebrow's box; the glyphs do not, as the still shows).
`text_below_floor`: the three "Komment" labels in FlyX's world (22 px; the names on the review cards are 28 px now).
`duplicate_media_discovery_risk` on the wall's repeated stills outside the frame.

**To confirm with the founder.** Whether the English site should show euros too (the basis is settled: the
founder chose the 13 November rate on 2026-11-16; Prof Enzo's number is theirs since draft 6c); the music track; whether the Latvia and Up To Youth speakers may appear; whether the smartwatch
brand is the watch webshop of the 23× result.

## Drafts 4 and 5

**The calls I made.** One device carries the claim: the feed (a wall of their reels) dies on "meghalt." and one card
comes back and takes the frame on the music's drop. Three client worlds in three layouts (phones and comments; a
triptych under a giant number; a polaroid pile that clears to a row of cards) instead of one layout three times.
Results each with its own picture and ground, one of them white. The clients' quotes moved out of the results into
one stack. The turn opens on the FlyX cinema seen from behind (bright, and nobody's face) after the first render
showed the laughing guests as a dark frame on the drop. Gyenis András is one small card of five; FlyX's owner is in
one phone, once.

**Not built.** Storylines A-C in `../film-new/STORYLINES.md` and film v6 (`../film-v6/`) are parked: the founder
chose the Social Chain grammar. The tall cut and the site's files wait for the verdict.

**Measured then.** 1235 frames, 49.40 s; review copies at -14.5 LUFS and -1.0 dBTP. The note that "the drop steps
+10 dB at 9.2-9.4 s, on the turn" was wrong: that step was the film's own effects; the track's kick came at 9.50 s
(see draft 6, Sync). The first render of draft 4 came out at -21 LUFS while the low hits rang for 6 s each;
limiting them to 2 s brought it back, so the renderer's mix level depends on overlapping tails: measure every
render.

**Draft 5.** The founder liked draft 4 ("otherwise i like the video") and asked for three things, all done: the two
smartwatch ads they found (in the wall, and in the productions row with the V89 ad as its middle card); the
stack after "Ne nekünk higgy. Nekik." holds the six clients' reviews only (their note: client reviews were mixed
with FlyX comments); the English cut. The reels inside the phones keep their Hungarian captions.
