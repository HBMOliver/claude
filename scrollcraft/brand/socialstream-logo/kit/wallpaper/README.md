# Mac wallpaper and lock-screen film

One scene in the kit's colours: Night ground, slow blue and violet light, and a stream of reels (soft cards of
light in the shape of the logo's phone, leaning its 15 degrees, drifting up along their lean in three depths).
In the middle, on a calm field, the kit's stacked logo, flat and untouched (the guide: "No shadows, outlines,
gradients or effects"). Made 2026-11-24 to 26 for the founder's MacBook Pro 14 (3024 x 1964, macOS 26).

## Files

| File | What it is |
|---|---|
| `final/SocialStream-wallpaper-3024x1964.png` | The still wallpaper at the MacBook Pro 14's own size, with the whole logo |
| `final/SocialStream-wallpaper-phone-3024x1964.png` | The same with the phone alone |
| `final/SocialStream-wallpaper-3840x2160.png`, `...-phone-3840x2160.png` | Both stills in 4K, for a desk display |
| `build.py`, `film.sh` | The build: HyperFrames projects for the stills and the film, then the film's encode |
| `install-lock-screen.sh`, `restore-lock-screen.sh` | Put the film in the place of a Mac's moving wallpaper, and Apple's back |
| `assets/grain.png` | The grain tile the scene lays over itself (it hides banding in the dark gradients) |

**The films are not in the repo** (233 MB and 39 MB; the repo keeps no film masters). `film.sh` writes them to
`final/`: `SocialStream-loop-40s.mov`, a seamless 40 s loop (3840 x 2160, 60 frames a second, HEVC 10-bit, no
sound), and `SocialStream-lock-screen.mov`, the same loop six times (4 minutes). The founder's Mac has both in
`~/Pictures/SocialStream wallpaper/`, with the stills, the two scripts and Apple's own film.

## The film

In the film the logo builds itself with the kit's own logo animation (`../../tools/make_motion.py`): the phone
arrives, the S swipes up into it like the next reel, it leans 15 degrees, the cut opens, it settles and the
name comes out from under it. It holds, fades, and builds again, once every 10 seconds (`CYCLE` in `build.py`).
The film begins two seconds before a build, with the finished logo standing, because macOS shows a film's first
frame as the desktop picture after every start (`film.sh` moves the start without encoding again).

## How macOS uses them

macOS 26 has one wallpaper for the lock screen and the desktop. A still picture stands still in both. Only
Apple's own moving wallpapers move on the lock screen, and come to rest as the desktop picture after sign-in.

- **Still (the official way):** System Settings > Wallpaper > Add Photo, choose one of the PNG files.
- **Moving (unofficial):** macOS 26 keeps Apple's moving wallpapers as films in
  `~/Library/Application Support/com.apple.wallpaper/aerials/videos/`. `install-lock-screen.sh` keeps Apple's
  "Tahoe Day" film (the one that Mac has) in `~/Pictures/SocialStream wallpaper/Apple original/` and puts the
  SocialStream film in its place; `restore-lock-screen.sh` puts Apple's back. The wallpaper must stay set to
  Tahoe Day. An update of macOS may put Apple's film back: run the install script again. System Settings keeps
  showing Apple's own thumbnail for it. Both scripts end by restarting the two programs that show the
  wallpaper, which also puts the film back to its first frame.

## What is checked and what is not (2026-11-26)

- **Checked** on the founder's Mac: the film is in the slot (compared byte for byte), the wallpaper program
  opens and decodes it without an error, and the desktop shows its first frame. The founder answered "Looks
  right" that day; by the system log that can only have been this still picture.
- **Not checked: the film playing.** The Mac had not shown its lock screen once between the install and this
  note, so nobody has seen it move. Apple's films have 240 frames a second in layers, which macOS uses to slow
  them down; this one has 60 and no layers. How smoothly macOS plays and slows it is unknown.
- **Measured from the system log, with Apple's film** (the eight times the lock screen came up in three days):
  the picture stands a second or three, then the film goes on from exactly where it last stopped. After
  sign-in it runs about one more second, slows over about five and stops, and that frame is the desktop
  picture until the next lock. A quick Touch ID sign-in moves the film on by about 1.9 seconds each time.
- **So about three rests in ten are not the finished logo.** In each 10 s the logo is finished from 0 to 1.3 s,
  fades to 1.6, is absent to 2.0, builds to 4.2 and is finished from there. Not changed: how often the logo
  builds is the founder's choice. A longer `CYCLE` leaves the finished logo on the desktop more often; letting
  the old logo fade while the next phone arrives would leave no frame without one (not built).
- **To read what a lock did:** `/usr/bin/log show --last 10m --style compact --predicate 'process ==
  "WallpaperAerialsExtension"'`, then look for `Start timebase at`, `Pause Called`, `RAMP-DOWN` and `frames
  enqueued in the last 6 seconds` (about 360 or 180 while playing is smooth; about 45 would be a stutter).

## Rebuild

```sh
python3 build.py                       # the HyperFrames projects: loop/ (the film), still-*/ (the stills)
mkdir -p out/stills
(cd loop && npx --yes hyperframes@0.9.40 render -q delivery --crf 8 -o ../out/loop-h264.mp4)   # about 8 minutes
./film.sh                              # the two .mov files in final/, about 9 minutes (ffmpeg with libx265)
(cd still-mbp14 && npx --yes hyperframes@0.9.40 snapshot --at 2 --no-end --keep -o ../out/stills/still-mbp14)
cp out/stills/still-mbp14/at-2s.png final/SocialStream-wallpaper-3024x1964.png
sips --embedProfile "/System/Library/ColorSync/Profiles/sRGB Profile.icc" final/SocialStream-wallpaper-3024x1964.png
```

The other stills are made the same way from `still-mbp14-phone/`, `still-4k/` and `still-4k-phone/`. The
projects, `out/` and the films are not tracked. Rendering to ProRes (`--format mov`) captures every 4K frame
losslessly and takes hours; the MP4 route above takes minutes. The snapshot tool stops at 4096 px wide, so
there is no 5K still. `hyperframes check` reports `canvas_covered` for the logo compositions over the opaque
scene; the film shows the logo on top, so it is a false alarm here.
