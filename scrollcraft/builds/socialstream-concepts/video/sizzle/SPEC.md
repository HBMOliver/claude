# SocialStream sizzle, drafts 4 and 5 (spec, 2026-11-16)

The founder on draft 3: "there is too much andras at the beginning, i think we can still do better ... bring your
most expert knowledge, plan it first then do the video", then "study the socialchain video better". This spec is
the plan the film was built from, with the numbers as built. Drafts 1-3 are in git history (README.md has their
notes); REVIEW.md is the review.

**Draft 5** (the founder: "otherwise i like the video"): the two smartwatch ads they found are in the wall and in the
productions row; the stack of "their words" is the clients' reviews only ("you are mixing client reviews with flyx
comments": FlyX's viewers' comments are about FlyX's videos, so they stay in FlyX's world); and an English cut
(`wide-en/`), every line the site's own English.

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
TIME:    49.40 s x 25 = 1235 frames. Music "What About Action" (Mixkit), 121 bpm, entered at 53.975 s: its
         breakdown carries the hook and its drop lands at 9.28 s. Beat = 0.4952 s = 12.38 frames; every beat is
         computed from the drop, b(k) = round((9.28 + 0.4952 k) x 25) / 25. Layouts change on the bar (4 beats).
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
| 8.80-11.28 | b-1..b4 | The turn | The middle card comes back in colour, grows, and on the drop it is the whole frame: the FlyX cinema from behind, heads against the bright screen. "Az érdeklődés vette át a helyét." | riser, drop, low hit, crowd |
| 11.28-15.24 | b4-b12 | FlyX Tenerife | Orange world. "69K megtekintés egy reelen" counts up; three phones fan out, their clips change on b8; three real comments type on; hearts rise; a slow push | whoosh, pops |
| 15.24-19.20 | b12-b20 | Prof Enzo | Green world. Three reels fill the height; the plays count over them and become "1M+" on b14; chips 149K, 122K, 105K, 82K pop; "33K követő" | wind, pops |
| 19.20-23.16 | b20-b28 | Productions | Polaroids of the team at work pile over the frame and scatter; violet world: five reel cards (Latvia, Up To Youth, the V89 smartwatch ad in the middle, the creator's smartwatch ad, a podcast; three of them change on b26 to Latvia, Miskolc and Sóskút), tags pop: Forgatás, Vágás, Feliratozás, Reels, Podcast & interjú | shutters, pops |
| 23.16-27.12 | b28-b36 | How | Night. "Mi gyártjuk a videót," (reel cards ring it) / "mi futtatjuk a hirdetést," (Meta, TikTok, Google, Reels) / "és mi mérjük," (81×, 79M Ft, 23×, 105 Ft) / "mit hozott." and the camera goes through it | wind, pops |
| 27.12-29.08 | b36-b40 | 79 M Ft | Blue. The week's seven days light up as the number climbs; "bevétel egy hét alatt" | whoosh, pop |
| 29.08-31.08 | b40-b44 | 81× ROAS | Red-pink. One "1 Ft" coin, then 81 burst out | coins |
| 31.08-33.04 | b44-b48 | 23× ROAS | White. The number slams in ink; "több mint 8M Ft bevétel"; the watch drops in | low hit |
| 33.04-35.04 | b48-b52 | ≈5 700 | Violet. Dots fill the frame as sign-ups count; "105 Ft egy jelentkező" stamps on b49 | low hit |
| 35.04-37.00 | b52-b56 | 300M+ Ft | Night. The widest number of the film; "2022 óta" above it, "kezelt büdzsé" under it | whoosh, pop |
| 37.00-42.96 | b56-b68 | Their words | "Ne nekünk higgy." / "Nekik."; then six cards stack up the frame, one a beat from b59 to b64, typing themselves: the six clients' reviews from the site; quotation marks drift at the sides; the stack holds two seconds | pops |
| 42.96-46.92 | b68-b76 | Promise | The wall is alive again and pulls back: "Videók, amiket végignéznek." / "Hirdetések, amik megtérülnek." | whoosh |
| 46.92-49.40 | b76 | Logo | The logo on the wall, "Interest media ügynökség" | impact |

## Honesty

- Every line is the site's own (`../../content.mjs`); quotes are cut with "…" only.
- 69K: FlyX Tenerife's most-played reel on Facebook. 149K, 122K, 105K, 82K, 33K followers: Prof Enzo's Facebook page.
  **1M+** is the sum of the play counts Facebook shows on Prof Enzo's 30 newest reels (1.03 million, read
  2026-11-15); it is my arithmetic, so the founder must confirm it before the film is published.
- Comments are real, shown without names or pictures. Counts sit beside the phones, never on one, because the
  reels on this Mac cannot be matched to their counts.
- Prof Enzo's reels are the client's own published videos (downloaded by the site session); the one with a film
  clip and a fast-food sign, and the shot of an oil bottle, are left out.
- The Latvia, Up To Youth, Miskolc Plaza and Sóskút clips are the ones the site session put on the site as
  "Részletek a videóinkból"; they are shown unnamed, as the team's videos. The Latvia captions are the words spoken.
- FlyX's guests appear only from behind (the turn) or as adults in a published reel inside a phone.
- FlyX's viewers' comments are shown in FlyX's world only. "Ne nekünk higgy. Nekik." is followed by the clients'
  reviews of SocialStream and nothing else.
- The smartwatch ads (ZS&M Smart: a creator's ad and the Valentine's Day ad for the V89) are shown as the team's
  videos, unnamed. They are not placed beside the "Karóra webshop" result: whether that client is this brand has
  not been confirmed, and the site keeps that client unnamed.
- English: the site's own English for every line it has; new strings are plain labels ("views on one reel",
  "views", "followers", "Comment", the days of the week).

## QA

Frames checked: 0.0 (a full wall, not black), 4.8 (problem readable over the wall), 7.6 (all cards grey), 8.9-9.4
(the card's growth, no seam), 10.5 (claim readable on footage), 13.2, 14.9 (FlyX: comments readable, clips
changed), 16.1, 19.2 (Prof Enzo: number readable over footage), 20.0 (polaroids cover the frame), 22.0 (cards and
tags), each "how" phrase, each result at its hold, 40.5 (stack: four cards readable), 44, 46 (promise on the wall),
49.0 (logo).
