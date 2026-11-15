# The brand film, remade in the site's look (2026-11-15)

The founder asked to put the logo animation into the website's film and to "remake that video so it matches the
style of the website". This is that remake: the client's own script and footage, rebuilt in Aurora Mix's look
(night blue with moving blue-purple light, red-pink as the accent, Sora headlines, Instrument Serif italic for the
accent word, glass cards), opening with the logo animation. It replaces the film the site plays
(`../../assets/hero-1080.mp4`, `hero-540.mp4`, `hero-v-720.mp4` and the two posters). The re-cut it replaces is
described in `../README.md`.

Two cuts on one clock, 25 fps, 803 frames, 32.12 s, silent (the site plays it muted):

| Time (s) | Scene | What happens |
|---|---|---|
| 0–4.0 | open + logo | Their reels fly in as a tilted wall; a night band runs through the middle, and the logo builds itself on it (the kit's animation, stacked, 28.125 % of the frame height) |
| 4.0–9.0 | claim | "A social media" is struck through in red-pink, "meghalt." comes in; then "Az érdeklődés vette át a helyét." |
| 9.0–12.0 | flyx | "FlyX Tenerife", Élményközpont · Social & video; three of their reels playing, standing like posts |
| 12.0–14.4 | roas | 81× ROAS counted up, legjobb eredmény, Ajtó webshop · Google PMax, beside three footage panels |
| 14.4–16.9 | mft | 79 M Ft, bevétel egy hét alatt, B2B Meta kampány (panels on the other side) |
| 16.9–19.9 | pod | "Podcast & interjú", Gyártás · Vágás · Feliratozás; three reels |
| 19.9–22.9 | svc | Videó, Social, Hirdetés, Weboldal, Automatizáció, Stratégia: one reel each, swiped up like a feed every half second |
| 22.9–25.6 | m300 | 300 M Ft, kezelt hirdetési büdzsé, 2022 óta az új korban |
| 25.6–28.7 | win | "Mi ebben a korban győzünk." |
| 28.7–32.1 | close | The wall and the logo again; then the wall and the logo go and only the band is left, which is the first frame, so the loop on the site has no jump |

The two cuts hit every beat on the same frame, because Mix crossfades from the wide cut to the tall one while the
film shrinks into its card. The aurora behind everything returns to its starting place at the end.

## Files

- `scenes/`: one HyperFrames scene each, shared by both cuts (the tall layout is in each scene's portrait media
  query); `scenes/result.html` is the template for the three numbers.
- `common.css`: the type, colours and parts every scene uses.
- `build.py`: fills in the scenes, adds the logo animation from the logo kit's `tools/make_motion.py` (formats
  `film-wide` and `film-tall`), and writes the two HyperFrames projects `wide/` (1920 × 1080) and `tall/`
  (1080 × 1920). Each project's `assets/` is a link to `assets/`.
- `assets/`: the fonts (Sora 400/700 Latin, Instrument Serif italic, with their OFL licences), the reel stills for
  the wall (`reels/`, the site's own p-frames), the kit's stacked dark logo, and `clips/` (not in git).
- `clips.sh`: cuts `assets/clips/` from their finished reels on this Mac (FlyX Reels, Flyx AD 1 and 2,
  "5. rész intro", "interveiw 8.5"; all their own, no stock B-roll, no child in the foreground). 720 × 1280, 25 fps.
- `encode.sh`: the site's files from the two renders.

## Rebuild

```bash
sh clips.sh                      # once, from the source reels on this Mac
python3 build.py
(cd wide && npx --yes hyperframes@0.9.40 render -q delivery -o ../master-wide.mp4)
(cd tall && npx --yes hyperframes@0.9.40 render -q delivery -o ../master-tall.mp4)
sh encode.sh master-wide.mp4 master-tall.mp4 ../../assets
```

`encode.sh` writes `hero-1080.mp4` (2.1 Mbps), `hero-540.mp4` (1.1 Mbps) and `hero-v-720.mp4` (1.5 Mbps), two-pass
H.264 with BT.709 tags, and the posters `hero-poster.jpg` (1600 × 900) and `hero-v-poster.jpg` (720 × 1280) from
3.0 s, where the logo is complete. Then `node tools/site.mjs` and the checks in `../../README.md` (Run).

## Checked

- `npx hyperframes check`: no errors in either cut. Warnings kept on purpose: no sound (the site plays it muted),
  the tilted wall reaching past the frame, the wall's repeated stills, and the services' reels starting later
  than 0 inside their scene.
- Contact sheets of both cuts at 1 and 2 frames a second, full-size frames of six beats, and every clip at
  4 frames a second (five clips were moved off stock B-roll or a title card, one off a child in the foreground).
- The site's encodes against the renders: smooth gradients and clean type at 1.1 Mbps.
- Aurora Mix with the new film: `lab/check.mjs` 45/45 on the page and on the packaged site, `lab/sitecheck.mjs`
  passes, and the opening's crossfade from the wide to the tall cut lands on the same moment.
- Not checked: how it looks on a real phone, and nobody listened (there is no sound).
