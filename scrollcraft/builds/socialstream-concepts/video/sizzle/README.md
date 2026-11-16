# The SocialStream sizzle (draft 6, 2026-11-16)

After seeing the v6 draft (`../film-v6/`), the founder sent Social Chain's 2026 sizzle as the film they had in mind
("i want it more like that"): ours said nothing and did not grab attention. They want the feeling of achievement
that comes from its motion graphics (phones coming up, comments, texts, counted numbers) and a story with words.
This film takes that grammar and tells SocialStream's own story with the site's own lines (`../../content.mjs`),
in SocialStream's type and colours, not Social Chain's look.

**Draft 4** was planned first (`SPEC.md`: what the reference does, the film's numbers, the shots, what is honest)
after the founder's "too much andras at the beginning, i think we can still do better" and "study the socialchain
video better". `REVIEW.md` is its review. 49.40 s, wide, with sound.

**Draft 5**: the founder liked draft 4; it adds the two smartwatch ads they found, makes the "their words" stack
the clients' reviews only, and adds the English cut (`wide-en/`; every line lives in `TEXT` in `build.py`).

**Draft 6**: the founder on draft 5: "its a bit too fast paste, also in english version convert the forints to
euros". 59.40 s. The hook and the three client worlds keep their length; the claim after the drop holds two bars
and comes a line at a time, "how we work" gets three bars, the big results six beats each, and the reviews land
one a second (`SPEC.md`, PACE and the shots). The beat was measured again on the track's kick drum: drafts 4 and 5
hit a quarter of a second before each kick, this one on it, and the film ends where the track ends. The English
cut shows euros; `SPEC.md` (Honesty) has every conversion and its rate.

## Files

- `SPEC.md`, `REVIEW.md`: the plan and the review.
- `clips.py <photos-exports> <prof-enzo-reels>`: cuts `assets/clips/` (phones, cards, the turn), `assets/wall/`
  (16 playing reels with their freeze frames, and stills, each with a grey copy), `assets/pol/` (polaroids) and copies
  `assets/audio/` (Mixkit music and effects). None of these are in git.
- `build.py`: writes the HyperFrames projects `wide/` (Hungarian) and `wide-en/` (English), or the one named on
  the command line (one composition per scene; the logo's build comes from the
  logo kit's `make_motion.py`, format `film-open-wide`).
- `common.css`: the type and the objects (wall, phone, reel card, comment, heart, polaroid, counter).

## Run

```sh
python3 -I clips.py <photos-exports-folder> <prof-enzo-folder>
python3 build.py
for p in wide wide-en; do (cd $p && npx --yes hyperframes@0.9.40 check && npx --yes hyperframes@0.9.40 render -q delivery -o ../master-$p.mp4); done
```

Measure the render's sound (`npx hyperframes audio <file> --json`): the mix level changed between renders (see
`REVIEW.md`), so bring it to about -14 LUFS when encoding. A review copy sent through the app must stay under
30 MiB: about 3.3 Mbps of video for these 59 s.

# Earlier drafts

## Draft 3 (42.56 s): the results, each its own idea

The founder found draft 2 "much better but where the best results are quite boring": four results in one layout.
Now each has its own picture and move, and its own wipe (diagonal from the right, from the left, up, an iris):
79 M Ft counts up while the week's days (H K Sze Cs P Szo V) light up one by one ("egy hét alatt"); 81× starts from
one coin ("1 Ft") and bursts into a 9 x 9 grid of 81 ("81 Ft") with a coins sound; 23× slams into the middle with
"Ünnepi kampány · több mint 8M Ft bevétel" counting under it; about 5 700 sign-ups count up while dots fill the frame
and "105 Ft / jelentkező" stamps in. The clients' quotes stay, earlier, so they can be read. -13.8 LUFS, -1.0 dBTP.

## Draft 2 (42.56 s, with sound)

Cut to "What About Action" (Mixkit, free licence, from their CapCut folder; 121 bpm): the film starts 55.975 s into
the track, near the end of its breakdown, so the problem plays over the quiet part and the drop lands on the turn to
colour (7.28 s); every later scene lands on a beat counted from the drop (`b(k)` in build.py). Effects (Mixkit, same
folder): a whoosh on each wipe (two takes), pops on the cards and numbers, a shutter on the behind-the-scenes cards, a
sub hit on the drop, one cinematic impact on the logo. Measured, not heard: -14.1 LUFS, true peak -1.1 dBTP. The audio
files are not in git (the licence does not allow handing them on); `clips.sh` copies them. The FlyX scene has four
comments now ("Enjoyable half hour. Friendly staff." added) and the quotes are shorter excerpts.

## Beats of draft 1 (39.04 s, wide, Hungarian, silent)

| Time | Beat | On screen |
|---|---|---|
| 0.00-3.04 | Open | The reel wall flies in; the logo builds itself (the kit's `film-end-wide` format) |
| 2.72-9.44 | Problem, then the claim | "Posztolsz. Hirdetsz. Mégsem jönnek a vevők?" beside two grey phones scrolling an empty feed; "A social media meghalt." (strike); the ground floods with colour, the phones play real reels: "Az érdeklődés vette át a helyét." |
| 9.12-12.32 | Mi gyártjuk a videót. | Gyenis András's podcast reels rise in phones; behind-the-scenes cards pop |
| 12.00-15.68 | Mi futtatjuk a hirdetést. | FlyX Tenerife's reels in phones; "69K megtekintés egy reelen" counts up; three real Facebook comments pop |
| 15.36-17.12 | És mi mérjük, mit hozott. | Words only, on night |
| 16.80-30.56 | Four results | 79 M Ft (hall builder), 81× ROAS (door webshop), 23× ROAS (watch webshop), 105 Ft a sign-up with about 5 700 sign-ups (webinar): each number counts up beside the site's object for it, with that client's own words |
| 30.24-34.24 | Voices | Three client quotes pile up; 300M+ Ft managed since 2022; Prof Enzo's 149K-view reel and 33K followers |
| 33.92-39.04 | Close | "Videók, amiket végignéznek. Hirdetések, amik megtérülnek." over the reel wall; the logo, "Interest media ügynökség" |

Every scene comes in over the last with a diagonal wipe. Numbers count in fixed-width digits with motion blur off.

## Sources and honesty

- Lines, results and quotes: the site's copy, word for word (quotes cut with "…" where shortened).
- Comments and reach: FlyX Tenerife's and Prof Enzo's Facebook pages, read on 2026-11-15 in the founder's signed-in
  browser. Comments show their words only, not who wrote them. The "69K" and "149K" are each page's top reel; the
  phones play other reels of theirs (`assets/clips/`, from the reels on this Mac), so the counts sit on a pill, not on
  a phone.
- Footage: their clients' reels (FlyX Tenerife, Gyenis András), the wall stills from `../film-v6/` and the site's
  result objects. András's reels' stock inserts are not used.

## Run

```sh
python3 build.py      # writes wide/
cd wide && npx --yes hyperframes@0.9.40 check && npx --yes hyperframes@0.9.40 render -q delivery -o ../master-wide.mp4
```

`assets/clips/` is not in git: `sh clips.sh` cuts the phone reels from `~/Movies/CapCut/` and copies the wall stills.
