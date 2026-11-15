#!/bin/sh
# Cuts the reels the sizzle's phones play into assets/clips/ (720 x 1280, 25 fps, H.264, no sound, BT.709): their
# clients' own reels on this Mac. The wall stills (assets/tiles/) come from ../film-v6/assets/tiles/.
# Run from this folder: sh clips.sh
set -e
C="$HOME/Movies/CapCut"
mkdir -p assets/clips
v() { # name start source seconds
  ffmpeg -v error -y -ss "$2" -i "$3" -t "$4" -an -vf "scale=720:1280:force_original_aspect_ratio=increase:flags=lanczos,crop=720:1280,fps=25,format=yuv420p" \
    -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709 "assets/clips/$1.mp4"
}
v flyx-ad 8.0 "$C/Flyx AD 1.mp4" 3.6          # their FlyX ad: the sunset over Costa Adeje
v flyx-reel 13.0 "$C/FlyX Reels.mp4" 3.6      # a FlyX reel: the landscape, "A whole new perspective"
v flyx-turn 6.0 "$C/FlyX Reels.mp4" 4.0       # the same reel: the boat trip (the first phone at the turn)
v andras-pod 0.0 "$C/5. rész intro.mp4" 4.2   # Gyenis András's podcast reel, its title card
v andras-reel 0.0 "$C/elso reel.mp4" 4.2      # his first reel, its opening (the studio, no stock insert)
mkdir -p assets/tiles && cp ../film-v6/assets/tiles/t*.jpg assets/tiles/
echo done
