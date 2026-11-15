# The brand film v5: "Through the phone" (2026-11-15)

The site's brand film, in Aurora Mix's look, with the logo animation as its opening. v4 (commit 2ba259b) remade the
client's film in the site's style; the founder then asked for "better motion graphics" and chose **Through the
phone**: one camera that keeps moving, every change of scene caused by something on screen, mostly a phone. v5
also brings in more of the team's own footage, and an English version for the site in English.

`SPEC.md` is the director's brief (look, motion rules, the shot list with times). It replaces the site's film files
(`../../assets/hero-1080.mp4`, `hero-540.mp4`, `hero-v-720.mp4`, the `-en` versions of the three, and the posters).

Two cuts on one clock in two languages: 25 fps, 885 frames, 35.4 s, silent (the site plays it muted).

| Time (s) | Shot | What happens |
|---|---|---|
| 0-3.25 | Open | Their reels fly in as a tilted wall; a night band runs through the middle and the logo builds itself on it |
| 3.25-3.95 | Dive | The camera dives into the logo's S (x260, log scale) and the wall falls behind |
| 3.85-8.85 | Claim | "A social media" comes at the camera word by word, a red-pink strike, "meghalt."; it flies past; "Az érdeklődés vette át a helyét." the same way |
| 8.9-11.3 | Stream | Their reels stand on a spiral around the camera's path and rush past as it flies on and brakes; the FlyX reel, furthest away, lands |
| 11.3-13.85 | FlyX | "FlyX Tenerife" beside the reel |
| 13.85-14.4 | Into the phone | The reel grows to the whole frame: we are inside the phone (story bars on top), on its flight over the sea |
| 14.75-19.55 | 81× ROAS, 79 M Ft | Swiped up like reels; the numbers roll like an odometer. Type only: no footage behind a result |
| 19.9-23.05 | Podcast & interjú | The frame shrinks back into a reel (the car interview) beside the title |
| 23.05-26.05 | Services | Six swipes, one every 0.5 s; the names roll beside it |
| 26.05-28.85 | 300 M Ft | The camera dives into the reel again while the number swipes in |
| 28.85-31.35 | Mi ebben a korban győzünk. | Word by word, held over 2 s |
| 31.75-32.55 | Back out | The frame shrinks and turns into the middle of the reel wall, which flies in around it |
| 32.55-35.4 | Close | The band and the logo; then the logo and the wall go, leaving the band: the first frame, so the loop has no jump |

English uses the site's own English copy (`../../content.mjs`): "Social media is dead." / "Interest has taken its
place." ... "In this era, we win." The site picks the language's film (`kit.js`: `-en` when the page is in English,
and it swaps the film at the same moment when the visitor switches).

## Files

- `scenes/`: one HyperFrames scene each, shared by all four projects (the tall layout is in their portrait media
  queries): `sky`, `open`, `claim`, `stream`, `flyx`, `feed` (the phone, from landing to the hand-over), `side`
  (podcast title, services), `wall` (back out into the wall), `close`.
- `common.css`, `common.js`: the type and parts; the clock, the camera, and `bake()` (below).
- `build.py`: the clock (`TM`), the footage table (`FOOT`), the words in both languages (`TEXT`), the phone's
  places, the reel spiral; it fills in the scenes, adds the logo animation (the logo kit's `tools/make_motion.py`,
  formats `film-wide` and `film-tall`, which end with the dive) and writes `wide/`, `tall/`, `wide-en/`, `tall-en/`.
  `python3 build.py wide-en` builds one.
- `clips.sh`: cuts `assets/clips/` (not in git) from the sources on this Mac; `encode.sh`: the site's files.

## Footage

All of it is the team's own work. No stock B-roll, no other brand as the subject, and nobody recognisable whose age
or consent isn't known: the Türkiye film was a youth exchange and Bridle Up Hope works with girls, so the people in
those reels are small in the frame, seen from behind, or the team.

| Where | Source |
|---|---|
| The FlyX reel (lands, fills the frame) | FlyX Reels (the owner, then the flight over the sea) |
| Podcast & interjú | the car interview, its clean part (the stock inserts left out) |
| Services | Videó: Bálint's showreel (the clapperboard); Social: the Latvia challenge crew carrying the tripod to the beach; Hirdetés: their FlyX ad; Weboldal: their own site, scrolled on a phone (`webclip.mjs`, in each language); Automatizáció and Stratégia: Bálint's showreel (code on a screen, a hand writing the plan) |
| The stream (14 reels) | Türkiye (their short film in Kemer, Oct 2025: dancing in the rain, a volunteer under the Taurus mountains, the bazaar from behind, the clean-up crew, a cat), Latvia (June 2025: the breakwater, gold-lit waves), Bridle Up Hope in Sóskút (a horse cantering, their film for the foundation before its captions start), Bálint (keys, microphone, animations), the Miskolc Plaza chess promo |
| The last reel, which becomes the wall's middle card | the sun going down over the Baltic (Latvia, 4K at 60 fps, slowed to 0.6×) |

The Photos originals are exported unmodified into `turkiye/`, `latvia/` and `bridleup/` and passed to `clips.sh`.
In `turkiye/`: `copy_FCE53987-21D8-4AF3-8984-32930C2FC7FE.mov` (the finished short film),
`video-output-45BA08E3-4BA9-41AC-BF6E-29273178748E-1.mov`, `IMG_1075.MOV`. In `latvia/`: `IMG_1628.MOV`,
`IMG_1672.MOV`, `IMG_1737.MOV`, `IMG_1746.MOV`. In `bridleup/`: `IMG_2196.MOV`, `BU_hun_subt_20251101.mp4`.

Up To Youth Hungary and Prof Enzo Hungary (Instagram) are not in yet: Instagram profiles need a login, and their
files are not on this Mac. To add them, put their clips in `clips.sh`, point slots of `FOOT` in `build.py` at them
(the stream reels or a service), rebuild and render.

## Rebuild

```bash
sh clips.sh <photos-folder>      # once, from the sources on this Mac (see Footage)
node webclip.mjs                 # the website reel, with the concepts served on :4560 (from a folder with playwright-core)
python3 build.py
for p in wide tall wide-en tall-en; do (cd $p && npx --yes hyperframes@0.9.40 render -q delivery -o ../master-$p.mp4); done
sh encode.sh master-wide.mp4 master-tall.mp4 ../../assets
sh encode.sh master-wide-en.mp4 master-tall-en.mp4 ../../assets -en
```

Then `node tools/site.mjs` and the checks in `../../README.md` (Run).

## How the motion is made (and one gotcha)

- The camera moves (the stream's perspective, the phone growing into the frame and shrinking back, the turn into
  the wall) are functions of time in the scenes' scripts. The film player seeks nested timelines its own way, and
  code run from `onUpdate` or from `modifiers` is not run again on every frame there (a test showed the reels
  frozen at an old moment). So `bake()` in `common.js` calls each scene's drawing once per frame while the scene is
  set up and turns what it would set into ordinary tweens (one per run of steady motion, a set where a text value
  changes): the player seeks those like any other animation, and every frame gets exactly its drawn value. The
  logo's dive is written out the same way, one set per frame (`make_motion.py`, `dive_sets`).
- The phone is a full-frame layer cut to the phone's shape with `clip-path`, so it can grow into the frame and
  shrink back; footage inside it is scaled to cover the shape at every moment, keeping its focus point in view.
- Swipes are reels moving one card height, each slide seen through its own card-shaped window (`slw-`), so footage
  scaled larger than the card still moves as one card; the numbers are odometer columns as wide as their own digit
  (Sora's digit widths are in `build.py`).
- Motion blur is on at render time (`data-motion-blur="on"` on the root): the player then draws each frame through a
  canvas, and an SVG group with no `transform` attribute did not draw at all there (the logo was missing until its
  dive). The logo's camera groups therefore start with an identity transform (`make_motion.py`).

## Checked

- `npx hyperframes check` in all four projects: no errors. Warnings kept on purpose: no sound (the site plays it
  muted), the wall's repeated stills, the sky's lights reaching past the frame, and a "last line" guess that picks a
  service name (the film's last line is "Mi ebben a korban győzünk.", held over 2 s).
- Every swipe, four frames into each, in both cuts; the logo's build at 1, 2 and 3 s in all four site files; the
  stream, the dives and the hand-overs in contact sheets of the renders.
- The loop, last frame against the first, in all six site files: mean difference 0.15-0.2 levels, largest 6-8.
- The opening's crossfade: both cuts held at the same moment (3.0 s and 16.0 s) while the film shrinks into its card.
- The site: `lab/check.mjs` 49/49 on Mix (with the film following the language: English cuts after switching,
  Hungarian again after switching back) and 186/186 on the other four pages; the packaged socialstream.hu folder:
  49/49 and `lab/sitecheck.mjs` all 62 files (40.8 MB).
- Not checked: how it looks on a real phone, and nobody listened (there is no sound).
