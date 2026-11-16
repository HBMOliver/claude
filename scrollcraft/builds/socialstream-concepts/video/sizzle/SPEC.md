# SocialStream sizzle, drafts 4 to 6 (spec, 2026-11-16)

The founder on draft 3: "there is too much andras at the beginning, i think we can still do better ... bring your
most expert knowledge, plan it first then do the video", then "study the socialchain video better". This spec is
the plan the film was built from, with the numbers as built. Drafts 1-3 are in git history (README.md has their
notes); REVIEW.md is the review.

**Draft 5** (the founder: "otherwise i like the video"): the two smartwatch ads they found are in the wall and in the
productions row; the stack of "their words" is the clients' reviews only ("you are mixing client reviews with flyx
comments": FlyX's viewers' comments are about FlyX's videos, so they stay in FlyX's world); and an English cut
(`wide-en/`), every line the site's own English.

**Draft 6** (the founder: "its a bit too fast paste, also in english version convert the forints to euros"): the
clock after the drop is new (PACE and the shots below; 59.40 s instead of 49.40), every hit sits on the track's
kick (drafts 4 and 5 hit a quarter of a second before it), and the English cut shows euros (Honesty).

**Draft 6b** (English only, 2026-11-16): shown the euro figures on a cautious basis and at the current rate, the
founder chose the current rate ("Use today's rate"). The English cut was rendered again with €216K, over €21K and
€820K+ (Honesty); nothing else differs, and the Hungarian cut is draft 6's.

## What the reference does (Social Chain 2026 sizzle, 67.6 s, 124.5 bpm, read at 5 frames a second)

1. **Footage is the picture.** About 70 % of its screen time is three playing vertical videos at 60-90 % of the frame
   height. Ours was about 25 %, small and to one side.
2. **A new world every 3-5 s.** Black, white paper, a client's blue, green, lime, black, red, black, pink, white:
   each client gets its brand colour with its name tiled faintly behind. Ours stayed in one blue-violet-pink family.
3. **Two voices in type.** Lines are small and quiet, one or two words at a time at the centre, each replacing the
   last (4-5 % of the frame height). Numbers are giant (40-45 %). Ours set everything large, so nothing was loud.
4. **Numbers sit on moving work**, never on an empty field: 3000+ over a triptych, 33m beside a playing card.
5. **Proof looks like the platforms**: press clippings, floating hearts, a comment stack that types itself, speech
   bubbles. That is where the feeling of achievement comes from.
6. **The music has a shape**: 11 s of quiet build (logo, line, press), the drop on the first client work, a dip for
   the manifesto line, the loudest stretch on the numbers.
7. Inside every card the clip changes on the beat, so 3 s shows six pieces of work, not three.

## The film

```text
GOAL:    a business owner who posts and advertises without buyers feels "these people make things people actually
         watch, and it pays", and remembers "social media is dead, interest took its place" and the logo.
OUTPUT:  HyperFrames, wide 1920 x 1080, 25 fps, with sound, in Hungarian (wide/) and English (wide-en/). (Tall after
         the verdict.)
TIME:    59.40 s x 25 = 1485 frames. Music "What About Action" (Mixkit), 121.0 bpm, measured on its kick drum
         (35-140 Hz, 2 ms steps; a line through the 96 kicks leaves 1.5 ms): the first kick after the breakdown
         is 63.479 s into the track and a beat is 0.49587 s = 12.40 frames. The film enters the track at
         54.199 s, so the breakdown carries the hook and that kick, the drop, lands at 9.28 s; every beat is
         computed from the drop, b(k) = round((9.28 + 0.49587 k) x 25) / 25. The track has 96 kicks after the
         drop (beats 0-95) and then rings out: the logo lands on beat 96. A sound that belongs to a beat is
         placed on the kick itself, not on the frame.
PACE:    (draft 6) After the drop the 96 beats are spent where there is something to read: the turn 8 (the
         claim, a line at a time), FlyX 8, Prof Enzo 8, productions 8, how 12, the results 6 + 4 + 6 + 6 + 4,
         their words 18, the promise 8. A line aims at 0.5 s + 0.3 s a word on screen; reviews land one a
         second; a result builds over its first beats and then holds while its world pushes in 3 %.
LOOK:    SocialStream's own, not the reference's: night #05070f with blue (66,92,255) and violet (136,78,255)
         light; ink #ffffff; accent red-pink #ff5272 on one thing per frame (a strike, a full stop, a heart).
         Narrator lines: Sora 700, 112-150 px, one phrase at a time at the centre, the stressed word in
         Instrument Serif italic. Numbers: Sora 700 digits 420-580 px with the unit in Instrument Serif italic.
         Labels: Inter 700, 28 px caps, tracking 0.16 em. Worlds: FlyX orange (#ff8a1f to #e0306f), Prof Enzo
         green (#16c172 to #075e63), productions violet (#4a22c8 to #1c0d58), results electric blue, red-pink,
         white #f3f5fb with ink #0b1030, violet; each client world has its name tiled at 7.5 % behind.
OBJECTS: the feed (a tilted wall of 9:16 cards, 300 x 533, 16 of them playing their reels); a phone (rounded body
         58 px, screen inset 12 px, an island); a reel card (rounded 40 px, no body); a polaroid (white frame
         16 px, 68 px foot); a comment (white card, radius 28-32 px, a grey disc, its source in small caps, words
         that type on); a heart (red-pink, 30-54 px, rising).
MOTION:  phones and cards arrive expo.out 0.7 s from below with 6-12 deg of turn; pops back.out(1.7) 0.4-0.45 s
         (scale and position only); words focus in 0.13 s and out 0.1 s; counters are fixed-width digits, written
         once a frame, motion blur off; wipes power3.inOut 0.32 s (diagonal right, diagonal left, up, iris); hits
         (1M+, the stamp, the logo) are 0 ms sets on the beat that then settle; in-card cuts are hard and on the
         bar. Render-time motion blur, shutter 120 deg.
BANNED:  numbers on an empty gradient with a small icon; four scenes in one layout; a face in more than one world
         (Gyenis András once, in one small card, after 21 s; FlyX's owner in one phone, once); whole sentences set
         as one block and left to sit; grey placeholder phones; a dark picture on the drop; anything that reads as
         Social Chain's look (thin grey sans with a pink bold word on black, its dust texture, its logo
         treatment); names or profile pictures of commenters; a count attached to a reel it was not measured on;
         Nike and RYZE spec ads; stock B-roll outside a client's published reel; children in the foreground;
         guests' faces at full frame.
```

## Shots (seconds; b = beat from the drop)

| Time | Beat | Shot | What happens | Sound |
|---|---|---|---|---|
| 0.00-3.00 | | The feed | The wall of their reels, 16 of them playing, settles and drifts; the logo builds itself in its middle and goes | music (breakdown) |
| 3.32-6.64 | b-12..-8 | Problem | One phrase at a time at the centre: "Posztolsz." / "Hirdetsz." / "Mégsem jönnek a vevők?"; the wall dims | |
| 6.80-8.72 | b-5..-4 | Diagnosis | "A social media" is struck through; on 7.28 "meghalt." and every card freezes and turns grey, from the middle outwards | low hit |
| 8.80-13.24 | b-1..b8 | The turn | The middle card comes back in colour, grows, and on the drop it is the whole frame: the FlyX cinema from behind, heads against the bright screen. "Az érdeklődés" lands on the drop, "vette át a helyét." two beats later; the picture pushes in for two bars | riser, drop, low hit, crowd |
| 13.24-17.20 | b8-b16 | FlyX Tenerife | Orange world. "69K megtekintés egy reelen" counts up; three phones fan out, their clips change on b12; three real comments type on, a beat apart (b10, b11, b12), and stay; hearts rise; a slow push | whoosh, pops |
| 17.20-21.20 | b16-b24 | Prof Enzo | Green world. Three reels fill the height; the plays count over them and become "1M+" on b18; "33K követő" on b19; the chips come two at a time: 149K and 122K on b20, 105K and 82K on b22 | wind, pops |
| 21.20-25.16 | b24-b32 | Productions | Polaroids of the team at work pile over the frame and scatter; violet world: five reel cards (Latvia, Up To Youth, the V89 smartwatch ad in the middle, the creator's smartwatch ad, a podcast; three of them change on b30 to Latvia, Miskolc and Sóskút); the tags come as one wave on b28: Forgatás, Vágás, Feliratozás, Reels, Podcast & interjú | shutters, pop |
| 25.16-31.08 | b32-b44 | How | Night. Four phrases, three beats each: "Mi gyártjuk a videót," (reel cards ring it) / "mi futtatjuk a hirdetést," (Meta, TikTok, Google, Reels) / "és mi mérjük," (81×, 79M Ft, 23×, 105 Ft) / "mit hozott." and the camera goes through it | wind, pops |
| 31.08-34.08 | b44-b50 | 79 M Ft | Blue. The week's seven days light up as the number climbs; the seventh and the whole number land on b47; "bevétel egy hét alatt"; it holds 1.5 s | whoosh, pop |
| 34.08-36.04 | b50-b54 | 81× ROAS | Red-pink. One "1 Ft" coin, then 81 burst out | coins |
| 36.04-39.04 | b54-b60 | 23× ROAS | White. The number slams in ink on b54; "több mint 8M Ft bevétel" on b55; the watch drops in on b56; it holds 2 s | low hit, pops |
| 39.04-42.00 | b60-b66 | ≈5 700 | Violet. Dots fill the frame as sign-ups count; "105 Ft egy jelentkező" stamps on b62 and holds 1.7 s | pop, low hit |
| 42.00-44.00 | b66-b70 | 300M+ Ft | Night. The widest number of the film; "2022 óta" above it, "kezelt büdzsé" under it | whoosh, pop |
| 44.00-52.92 | b70-b88 | Their words | "Ne nekünk higgy." (b70) / "Nekik." (b72); six cards stack up the frame, one every two beats from b73 to b83 (the first under "Nekik."), typing themselves: the six clients' reviews from the site; quotation marks drift at the sides; the stack holds 2.2 s | pops |
| 52.92-56.88 | b88-b96 | Promise | The wall is alive again and pulls back: "Videók, amiket végignéznek." / "Hirdetések, amik megtérülnek.", a bar each; the track's last kick is b95 | whoosh |
| 56.88-59.40 | b96 | Logo | The logo on the wall where the next kick would be, in the track's ring-out; "Interest media ügynökség" a quarter of a second later | impact |

## Honesty

- Every line is the site's own (`../../content.mjs`); quotes are cut with "…" only.
- 69K: FlyX Tenerife's most-played reel on Facebook. 149K, 122K, 105K, 82K, 33K followers: Prof Enzo's Facebook page.
  **1M+** is the sum of the play counts Facebook shows on Prof Enzo's 30 newest reels (1.03 million, read
  2026-11-15); it is my arithmetic, so the founder must confirm it before the film is published.
- Comments are real, shown without names or pictures, each marked "Komment" in FlyX's own world. Counts sit
  beside the phones, never on one, because the reels on this Mac cannot be matched to their counts.
- Prof Enzo's reels are the client's own published videos (downloaded by the site session); the one with a film
  clip and a fast-food sign, and the shot of an oil bottle, are left out.
- The Latvia, Up To Youth, Miskolc Plaza and Sóskút clips are the ones the site session put on the site as
  "Részletek a videóinkból"; they are shown unnamed, as the team's videos. The Latvia captions are the words spoken.
- FlyX's guests appear only from behind (the turn) or as adults in a published reel inside a phone.
- FlyX's viewers' comments are shown in FlyX's world only. "Ne nekünk higgy. Nekik." is followed by the clients'
  reviews of SocialStream and nothing else.
- The smartwatch ads (ZS&M Smart: a creator's ad and the Valentine's Day ad for the V89) are shown as the team's
  videos, with no label of ours; the V89 ad's own caption names the watch ("EGY V89-ES OKOSÓRÁVAL"). The ad's last
  third is the brand's shop page (its logo, prices in Ft): no card shows it (the wall's tile takes 3.0-7.6 s of the
  ad; in drafts 4 and 5 that tile ran into the page). The ads are not placed beside the "Karóra webshop" result:
  whether that client is this brand has not been confirmed, and the site keeps that client unnamed.
- English: the site's own English for every line it has; new strings are plain labels ("views on one reel",
  "views", "followers", "Comment", the days of the week).
- **Money in the English cut is in euros** (the founder: "in english version convert the forints to euros"); the
  English site still shows forints. Every figure is converted at one rate, the ECB reference rate of 2026-11-13,
  365.6 Ft to the euro (the latest published on 2026-11-16, when the founder chose it: "Use today's rate"):
  revenue and budget rounded down, costs rounded up. The first render of draft 6 used a cautious 400 Ft for
  revenue and budget (weaker than every yearly average of the ECB rate since 2022: 391, 382, 395, 398, 368) and
  read €197K, over €20K and €750K+; the founder was shown both and chose the current rate.

  | Hungarian | English | How |
  |---|---|---|
  | 79 M Ft bevétel egy hét alatt | €216K revenue in one week | 79,000,000 / 365.6 = 216,083 |
  | több mint 8 M Ft bevétel | over €21K in revenue | 8,000,000 / 365.6 = 21,882 |
  | 300M+ Ft kezelt büdzsé | €820K+ budget managed | 300,000,000 / 365.6 = 820,569 |
  | ≈5 700 jelentkező 600K Ft-ból | ≈5,700 registrants from €1,650 | 600,000 / 365.6 = 1,641, rounded up |
  | 105 Ft egy jelentkező | €0.29 per registrant | 105 / 365.6 = 0.287, rounded up; 1,650 / 5,700 = 0.29 |
  | 1 Ft → 81 Ft | €1 → €81 | a ratio, no rate |

  These are forint results at one day's rate, not what each campaign earned in euros when it ran: in 2022-2025
  the forint was weaker (yearly averages 382-398 Ft), so the same forints were fewer euros then (79 M Ft at 395
  Ft is €200K). The rounding leaves little room: €216K holds while the rate is at or under 365.74 Ft, €820K+ at
  or under 365.85 Ft, "over €21K" up to 380.9 Ft. Convert again if the cut is published after the forint has
  weakened.

## QA

Frames checked in draft 6 (Hungarian, 27 stills): 9.5 and 10.9 (the claim's two lines), 12.8 (still held), 15.0
and 16.6 (FlyX: comments, clips changed), 19.0 and 20.6 (Prof Enzo: 1M+, the chips), 22.0 (polaroids), 24.4 (cards
and tags), each "how" phrase, 32.0 and 33.6 (the week filling, then full), 35.4, 37.6 and 38.8 (23×), 40.9 (the
stamp), 43.2, 44.6, 45.7 ("Nekik." with the first review under it), 48.0 and 51.8 (the stack), 54, 56 (promise),
58.6 (logo). English (12 stills): the claim, FlyX, the euro chips, each result, the stack, the logo; a search of
the English project's files finds no "Ft". The hook (0-8.8 s) is built by the same code as in draft 5; from the
final render its frames at 0.0, 2.0, 4.8, 6.6, 7.8 and 8.9 s were looked at again, with the V89 tile recut.

Draft 6b (English): four lines of the project differ from draft 6 (the chip's text and three counters' targets).
Frame by frame against draft 6's English master (PSNR, 45 dB as the line) the render differs only at 28.20-29.64 s
(the chip), 31.28-33.96 s (€216K), 36.56-38.92 s (the pill) and 42.04-43.88 s (€820K+); its sound stream is
byte-identical. Stills from the render at 29.3, 32.0, 32.5, 33.6, 36.7, 38.6, 42.3 and 43.6 s were looked at, and
the pill enlarged from the project.

Sound checked on the renders (REVIEW.md): the kick against the picture at the drop and at a late beat, loudness,
true peak.
