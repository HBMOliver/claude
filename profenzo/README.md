# Profenzo Hungary – Prof Enzo rövidvideó-gyártás

> **Megjegyzés:** a repó nyilvános, ezért a stratégia, a formátum- és compliance-leírás, valamint a videónkénti szkriptek és gyártási csomagok (`FORMAT.md`, `STRATEGIA-*.md`, `videok/`) nincsenek gitben. Ezeket a csapat tömörített csomagban kapja meg. A gitben a renderelő motor és a karakterképek vannak.

| Mappa / fájl | Tartalom |
|---|---|
| [`FORMAT.md`](FORMAT.md) | A csatorna videóformátuma: karakter, hang, feliratok, dramaturgia, compliance |
| [`STRATEGIA-2026-11-18.md`](STRATEGIA-2026-11-18.md) | Prof Enzo tartalomstratégia: 60 témacím, 10 kész szkript, szabályok |
| `videok/NN-…/timeline.json` | Egy videó teljes terve: narráció, jelenetek, feliratszínek, SFX, TikTok-leírás, compliance |
| `videok/NN-…/gyartasi-csomag.md` | Ember által olvasható gyártási csomag: narráció, időkódos táblázat, leírás, hashtagek, ellenőrzés |
| `engine/` | Renderelő: HTML/canvas jelenetsablonok + Playwright + ffmpeg |
| `assets/` | Prof Enzo kivágott karakterképe és avatarja. A hangminta helyben van, gitbe nem kerül fel. |

## Videók
| # | Cím | Törzs | Állapot |
|---|---|---|---|
| 00 | A hajnali 3 órás ébredés biológiája (brief) | B2 | vázlat kész |
| 01 | Van otthon öt illóolajad, de csak kettőt használsz? | C3 | vázlat kész (1. hullám) |
| 02 | A diffúzorod nem varázspálca | C2 | vázlat kész |
| 03 | Miért nem mindegy, hogyan kened a bőrödre az illóolajat? | C1 | vázlat kész (1. hullám) |
| 04 | Citromolaj a bőrödön, aztán irány a napfény? | C1 | vázlat kész (1. hullám) |
| 05 | Citromlé vagy citromolaj – ugyanaz lenne? | C1 | vázlat kész |
| 06 | A lakásod tiszta, vagy csak jó illatú? | B3 | vázlat kész |
| 07 | A bőröd nem padlócsempe | B1 | vázlat kész |
| 08 | Miért építed fordítva a wellnessrutinodat? | B3 | vázlat kész (1. hullám) |
| 09 | Tele van a szekrényed étrend-kiegészítőkkel? | B3 | vázlat kész |
| 10 | Tudtad, hogy egy illóolaj mögött laboratórium is állhat? | C3 | vázlat kész (1. hullám) |

A vázlatokban minden kész a hangon és a szájszinkronon kívül: szöveg, időzítés, feliratok, grafikák, SFX, zene. Prof Enzo itt még állókép, a feliratok időzítése becsült. A végleges változathoz ez hiányzik:
1. **Prof Enzo hangja.** A HeyGen-fiókban van: HeyGen API-kulcs kell (`api.heygen.com`, `X-Api-Key`). Másik lehetőség az ElevenLabs-kredit és egy „Prof Enzo” Instant Voice Clone `assets/prof-enzo-hangminta.wav`-ból.
2. **Szájszinkronos animáció.** HeyGen Avatar (a saját fiókból, vagy ElevenLabs-on keresztül a `heygen-avatar6` modellel).

Ha megvan a hangfájl, a feliratok és a jelenetek automatikusan a valódi beszédhez igazodnak:
```bash
cd engine
python3 build.py plan  ../videok/04-citrus-napfeny --vo hang.wav --words szavak.json   # szavak.json: faster-whisper szóidők
python3 build.py video ../videok/04-citrus-napfeny
python3 build.py audio ../videok/04-citrus-napfeny
python3 build.py mux   ../videok/04-citrus-napfeny vegleges.mp4
```
Vázlat hang nélkül: `plan … --draft`, aztán `video`, `audio`, `mux … vazlat.mp4`. A csomag frissítése: `python3 package.py ../videok/NN-…`.

Mentés a Drive-ra és bemutató:
```bash
./drive_preview.sh ../videok/NN-…/build/vazlat.mp4 elonezet.mp4   # kb. 3 MB, 540×960: ekkora fér át a Drive-csatlakozón
python3 package.py --html ../videok/NN-…                          # build/gyartasi-csomag.html, Google Docként importálható
python3 showreel.py bemutato.mp4                                    # bemutatóvideó: részlet minden vázlatból
```

## Drive-mappa
A csapat Drive-mappája: **Prof Enzo – TikTok videók (Claude)**. Itt is van egy „0 – OLVASS EL” áttekintés.
- `1 – Vázlatok (hang és szájszinkron nélkül)`: a vázlatok kb. 3 MB-os előnézetei.
- `2 – Gyártási csomagok`: a csomagok Google Docként. A `Forrásfájlok – timeline.json` almappában vannak a gépi tervek. Egy új munkamenet ezeket visszamásolja a `videok/NN-…/timeline.json` helyre, és onnan folytatja.
- `3 – Végleges videók (Prof Enzo hangjával)`: a kész, publikálható videók.

A Drive-csatlakozó hívásonként kb. 3 MB-ot visz át, ezért a teljes minőségű MP4-ek nem férnek fel. Ezeket a csapat közvetlenül kapja meg.

## Új videó a 60 témacímből
1. Másold le egy meglévő `timeline.json`-t, és írd be a narrációt (a végén az egységes CTA).
2. A jeleneteket a narráció szavaihoz kell horgonyozni (`"from": "@Állj"`). Elérhető sablonok: `studio`, `cards` (list/grid/vs), `bigtext`, `label`, `kbsearch`, `shelf`, `stop`, `sun`, `house`, `field`, `chroma`, `diffuser`, `carrier`, `concentrate`, `drop`, `plate`, `neurons`, `chart1/2`, `clock`, `phone`, `end`.
3. A feliratok automatikusan 3–4 szavas csoportokra tördelődnek. A `keywords.amber` és `keywords.green` szótövek adják a színkódot.
