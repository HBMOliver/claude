# The SocialStream sizzle (draft, 2026-11-15)

After seeing the v6 draft (`../film-v6/`), the founder sent Social Chain's 2026 sizzle as the film they had in mind
("i want it more like that"): ours said nothing and did not grab attention. They want the feeling of achievement
that comes from its motion graphics (phones coming up, comments, texts, counted numbers) and a story with words.
This film takes that grammar and tells SocialStream's own story with the site's own lines (`../../content.mjs`),
in SocialStream's type and colours, not Social Chain's look.

## Beats (39.04 s, wide, Hungarian, silent)

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
