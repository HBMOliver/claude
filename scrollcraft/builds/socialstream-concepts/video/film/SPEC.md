# Brand film v5: "Through the phone" (spec)

The founder asked for better motion graphics and chose "Through the phone": one camera that keeps moving, and
every change of scene caused by something on screen, mostly a phone. v5 also brings in more of the team's own
footage (Türkiye, Latvia, Bridle Up Hope in Sóskút, Bálint's showreel).

```text
GOAL:    by the end the viewer has been carried through SocialStream's work like scrolling a feed, and remembers
         "social media is dead, interest took its place" and the logo.
OUTPUT:  HyperFrames, two cuts on one clock: wide 1920 x 1080 and tall 1080 x 1920, 25 fps, silent (the site plays
         it muted, looping, and crossfades from the wide cut to the tall one); each in Hungarian and in English (the
         site's English mode plays the English film), so four projects with the same motion.
TIME:    35.4 s x 25 = 885 frames. The last frame must equal frame 0 (the loop).
LOOK:    the site's (Aurora Mix): ground #05070f with four drifting lights (blue 66,92,255 / violet 136,78,255 /
         red-pink 255,64,104 / sky 56,160,255); ink #eef1f8; accent red-pink #ff5272, at most one accent per frame
         (a strike, a ×, a full stop, a dot). Display: Sora 700, tracking -4.5 %; accent word: Instrument Serif
         italic; small type: Inter 600/700. Phones: 9:16 reel cards, radius 28 px at 400 px wide, 1.5 px white ring
         at 16 %, shadow 0 50 100 -40 black 85 %, violet glow 0 0 120 -30 (120,104,255) 55 %.
OBJECTS: the logo (the kit's G2 animation: tilted phone with the S swiping in); the reel (a phone card playing
         their footage, with a story bar); the feed (inside the phone: full-frame slides that swipe up like reels).
MOTION:  arrivals expo.out / power4.out 0.5-0.7 s; camera pushes and card growth power3.inOut 0.55-0.7 s; zoom
         through power2.in on a log scale 0.7 s; exits power3.in, 40-50 % shorter than entrances; swipes
         power3.inOut 0.38 s; words 70 ms apart; text dead still once landed.
BANNED:  the defaults (everything centred, everything fading in, slide-up on every element, titles that drift,
         three cards in a row, a title over dimmed footage, the logo in a corner, glow orbs and particles);
         stock B-roll; children in the foreground; another brand as the subject (Nike end card, RYZE ads);
         footage behind a result that belongs to a different client than the result.
```

## Shots (absolute seconds; both cuts)

| Time | Shot | Hero move | Hand-off |
|---|---|---|---|
| 0.00-3.25 | Open | reel wall flies in from the centre on the night band; the logo builds itself (kit animation) | logo complete at 3.0 (poster) |
| 3.25-3.95 | Dive | the camera dives into the logo's S (scale x260 about the phone centre, log scale, power2.in); wall pushes 1 → 1.25 and fades | we land in the night |
| 3.85-6.55 | Claim A | "A social media" arrives from depth word by word (scale 0.42 → 1 about the frame centre, blur 12 → 0); 4.62 the red-pink strike cuts "social media"; 5.0 "meghalt." drops in (serif italic) | 6.55 the line flies past the camera (x3.2, blur 18, 0.4 s) |
| 6.80-8.85 | Claim B | "Az érdeklődés vette át a helyét." arrives from depth the same way | 8.85 flies past; the reels come |
| 8.90-11.30 | Stream | 14 reels of their footage stand on a widening spiral around the camera's path and pass it one after another (perspective, focal 1000 px); the camera flies 6000 px and brakes (power2.out) | the FlyX reel, furthest away, lands |
| 11.30-13.85 | FlyX | the FlyX reel stands (wide: left; tall: lower middle); "FlyX" letter by letter, "Tenerife" comes into focus | 13.85 the camera dives into the reel |
| 13.85-14.40 | Into the phone | the reel grows to the frame (power3.inOut 0.55 s), radius 28 → 0; the title blurs 15 px and goes | inside the phone: the FlyX reel's flight over the sea full-frame, story bars on top |
| 14.75-17.15 | 81× ROAS | swipe up; "81" rolls like an odometer, × in red-pink; "legjobb eredmény", "Ajtó webshop · Google PMax" | swipe |
| 17.15-19.55 | 79 M Ft | swipe; "79" rolls; "M Ft" serif italic; "bevétel egy hét alatt", "B2B Meta kampány" | swipe to the podcast reel |
| 19.90-20.60 | Out of the phone | the full frame shrinks into a reel (wide: right; tall: lower middle) | Podcast & interjú beside it |
| 20.60-23.05 | Podcast | the reel plays; title and "Gyártás · Vágás · Feliratozás", line by line into focus | the reel starts swiping |
| 23.05-26.05 | Services | six swipes, one every 0.5 s (Videó, Social, Hirdetés, Weboldal, Automatizáció, Stratégia); the names roll beside it | 26.05 the camera dives into the reel |
| 26.05-28.85 | 300 M Ft | the reel grows to the frame while the 300 M Ft slide swipes in; "kezelt hirdetési büdzsé", "2022 óta az új korban" | swipe |
| 28.85-31.35 | Win | "Mi ebben a korban győzünk." per word, full stop in red-pink; holds over 2 s | swipe to the last reel |
| 31.75-32.55 | Back out | the full frame shrinks and turns -10° into the middle of the reel wall, which flies in around it | it is one reel of the wall |
| 32.55-35.40 | Close | night band and dimming come up, the logo (kit lockup) fades in on the band, holds, goes; the wall goes | band alone = frame 0 |

English (the site's own English copy): "Social media is dead." / "Interest has taken its place." / Experience centre · Social & video /
best result · Door webshop · Google PMax / revenue in one week · B2B Meta campaign / Podcast & interview · Production · Editing ·
Subtitles / Video, Social, Ads, Website, Automation, Strategy / ad budget managed · In the new era since 2022 / "In this era, we win."

The three results are type only, on the site's ground: no footage behind a number, so no client's footage stands
for another client's result.

Transitions used: zoom through (logo → claim), fly past (claim lines), object becomes the world (into the phone,
twice), swipe (inside the phone), carry across (out of the phone, back into the wall).

## Footage map

| Slot | Clip | Source |
|---|---|---|
| hero | ph-flyx | FlyX Reels 0-6.7 s |
| pod | ph-pod | the car interview 28-32.3 s |
| services | ph-svc-video / social / ads / web / auto / strat | Bálint 31 s; Latvia IMG_1672; Flyx AD 1; their site (webclip.mjs); Bálint 10.2 s; Bálint 8 s |
| last | ph-last-wide / ph-last-tall | Latvia IMG_1737 (sunset), slowed to 0.6× |
| stream | st-01 ... st-14 | Türkiye (rain dance, volunteer, cat, bazaar, clean-up crew), Latvia (breakwater, waves), Bridle Up Hope (canter, film opening), Bálint (keys, mic, animations), chess promo |

## QA frames

0 and 884 (identical), 75 (logo complete, poster), 92 (mid-dive), 105 (claim A arriving), 140 (strike done),
160 (claim A held), 208 (claim B held), 230-270 (stream), 322 (FlyX), 352 (mid-dive into the phone), 408 (81×),
465 (79 M Ft), 506 (out of the phone), 545 (Podcast), 583 / 608 / 633 (services), 658 (into the reel), 695 (300 M Ft),
755 (Win), 802 (back into the wall), 840 (logo on the band).
