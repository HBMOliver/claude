# Átadás – Prof. Enzo podcast-projekt (helyi munkamenethez)

Ez a fájl mindent tartalmaz, amit a felhős munkamenet eddig elvégzett, hogy egy **helyi (Mac-en futó) Claude Code munkamenet** folytatni tudja.

## Hogyan indítsd
1. Mac-en, terminálban:
   ```bash
   git clone https://github.com/HBMOliver/claude.git   # ha még nincs meg
   cd claude
   git fetch origin claude/clever-hamilton-mdtd5r
   git checkout claude/clever-hamilton-mdtd5r
   brew install ffmpeg   # ha még nincs fent
   claude
   ```
2. Az első üzenet a helyi Claude-nak:
   > Olvasd el a `podcast/ATADAS.md` fájlt, és folytasd onnan a munkát. A 25 perces podcast videó a `~/Downloads` mappában van.

## A cél
- Egy podcast videóba (fix, szemből vevő kamera, 2 szék) a **bal oldali székre** beilleszteni az animált **Prof. Enzo** karaktert; a jobb oldalon az élő **András** ül.
- Enzo ne az asztalon üljön, hanem András mellett, **nagyjából ugyanolyan magas, hasonló testalkatú** legyen.
- Gesztikuláljon beszéd közben, szünetekben figyeljen Andrásra (jobbra néz, bólogat).
- Természetes fények, árnyék, a szék/asztal takarása (occlusion), enyhe kolorgrade az egész videón.

## Következő feladatok (sorrendben)
1. **Epizódok szétvágása:** a `~/Downloads`-ban lévő 25 perces videóban 5 epizód van (egyenként ~3–4 perc).
   - Az epizódszkriptek eddig **nem kerültek át** ebbe a munkamenetbe – kérd el a felhasználótól, vagy készíts leiratot (ElevenLabs Speech-to-Text) és abból keresd meg a határokat.
   - Vágás ffmpeg-gel, újrakódolás nélkül vagy minimálisan (`-c copy`, vagy pontos vágáshoz `-c:v libx264 -crf 16`), kimenet: `podcast/epizodok/epizod_1.mp4 … epizod_5.mp4`.
   - A felhasználó a fájlokat **CapCut**-ban is látni szeretné: helyben a vágott mp4-eket a CapCutba lehet importálni (vagy, ha elérhető, a CapCut projektmappába tenni). HyperFrames (HeyGen) igény is felmerült – a felhős munkamenetben a HyperFrames szerkesztés le volt tiltva; helyben a `npx skills add heygen-com/hyperframes` skill telepíthető.
2. **Hang:** a felhasználó **új hangot fog megadni** a karakterhez – erre kell lecserélni. (Márk HeyGen-hangja volt az eredeti kérés; az ElevenLabs-klón nem jelent meg a bekötött fiókban, ezért ideiglenesen **Miklós** hanggal készült.)
3. **Beillesztés** minden epizódba, ahol Enzo beszél: a `podcast/beilleszt.sh` scripttel (lásd lent), pozíció/méret beállítása a valós széken, takarási maszk, árnyék, színillesztés, kolorgrade.

## Ami eddig elkészült (a `podcast/` mappában)
| Fájl | Mi ez |
|---|---|
| `KARAKTER.md` | Prof. Enzo karakterlap: stílus (nyugodt, pontos, kedves, enyhén száraz humor, nem licitálja túl Andrást), mozgás, animációs prompt |
| `karakter/doktor_eredeti.jpg` | Eredeti karakterkép (álló) |
| `karakter/ulo_A.png` | **Ülő karakter zöld háttéren – ezt használjuk** (jobbra, András felé fordul) |
| `karakter/ulo_A_atlatszo.png` | Ugyanez átlátszó háttérrel |
| `karakter/ulo_B.png` | Másik ülő változat (szemből) |
| `szoveg_enzo_1.md` | Az 1. részlet 5 mondata (szünetekkel) |
| `hang/Miklos/1-5.mp3`, `enzo_1_Miklos.mp3` | Az 5 mondat Miklós hangján + összefűzve 1,5 mp szünetekkel (időkódok a `_idokodok.txt`-ben) |
| `animaciok/enzo_1_Miklos.mp4` | **Kész szájszinkronos, gesztikuláló animáció** zöld háttéren, 1920×1088, 25 fps, 26 mp, hanggal |
| `animaciok/enzo_1_ideiglenes_Gergo.mp4` | Korábbi, visszafogottabb változat (Gergő hang) |
| `animaciok/proba_beszed_GGeery_hanggal.mp4` | Első szájszinkron-próba |
| `forras/mark_hang_tiszta.mp3` | Márk hangja kivágva a HeyGen reelből, zene nélkül (27 mp) – klónozáshoz |
| `hangprobak/*.mp3` | 4 hangpróba (GGeery, Elison, Martin, Botond) |
| `beilleszt.sh` | Beillesztő script: zöld háttér le (colorkey 0x00B140), despill, árnyék, opcionális takarási maszk, kolorgrade, hangkeverés |
| `hang_osszefuz.sh` | Mondatonkénti hangfájlok összefűzése szünetekkel + időkódok |

### `beilleszt.sh` használat
```bash
./podcast/beilleszt.sh <podcast.mp4> <karakter_zold.mp4> <kimenet.mp4> [X] [Y] [MAGASSAG]
# Finomhangolás env-ekkel: KEY_SIM, KEY_BLEND, DESPILL, SHADOW, TEMP, OCCLUSION=maszk.png, GRADE=1, KARAKTER_HANG=1
```
Megjegyzés: az X/Y a karaktervideó **teljes 16:9 keretére** vonatkozik (a karakter a keret közepén ül) – érdemes előbb a karakter befoglaló dobozára vágni (`crop`), hogy a pozicionálás egyértelmű legyen. A zöld kulcsoláshoz a 0.22 / 0.08 / despill 0.25 érték bevált (a türkiz póló megmarad).

## ElevenLabs (a felhasználó fiókjában)
- **Flow:** „Doktor karakter – podcast hangpróbák” – flow ID: `Dr643iTMAl7yT8LduqW0`
- Ülő karakter generáció (A): `sCeg4TZ1xlnoH6W7Fj58` (gpt-image-2.5-sunburst)
- Szájszinkron modell: `bytedance-omnihuman-v1.5` (kép + hang → beszélő videó). Ár: ~0,21 USD / mp; 26 mp ≈ 5,5 USD, generálás ~20–25 perc.
- Bevált animációs prompt: lásd `KARAKTER.md` és az alábbi:
  > The seated cartoon doctor (Prof. Enzo) talks calmly and precisely to his podcast partner off-screen to the right. Accurate Hungarian lip-sync. Kind, composed expression with a hint of dry humor. While speaking he gestures naturally with his hands at a moderate level: opens a palm toward the partner, a small explaining gesture with one hand, lightly touches his chest when saying "Én", hands return to his knees between sentences. Slow thoughtful nods. No big waving or exaggerated arm movements. During silent pauses he listens attentively, looking to the right, mouth closed, with small natural nods. Body stays seated in exactly the same position and scale, camera completely static, no zoom, green background unchanged.
- Hang-ID-k: Miklós `zqSgQYLgidMI4Wt9Eiri`, Gergő `CR2bo0mBsCKXtdiJkK6s`, GGeery `So1xYhVoPuU9ivXmy9r8`. TTS modell: `eleven_v4`.
- **Márk klón:** a felhasználó létrehozta az ElevenLabsben, de a bekötött fiókban nem látszott – helyben kérd el a **Voice ID**-t (Voices → My Voices → ⋯ → Copy voice ID).

## Higgsfield
- 0 kredit (ingyenes csomag) → generálás/klónozás nem ment. Feltöltésre (nyilvános URL-hez) használható volt.

## Tanulságok
- A chatbe/Drive-ra elsőre képernyőkép került videó helyett – ellenőrizd a fájltípust (`ffprobe`).
- Az omnihuman-videóban a karakter kissé elmozdulhat/zoomolhat – a promptban kérd a fix pozíciót, és beillesztéskor ellenőrizd képkockákon.
- A nagy forrásvideók (`podcast/forras/*.mp4`) a `.gitignore` miatt nincsenek a repóban.
