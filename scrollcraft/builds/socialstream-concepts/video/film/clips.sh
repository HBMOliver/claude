#!/bin/sh
# Cuts the client clips the film uses from their finished reels on this Mac (all BT.709 SDR, vertical).
# Each comes out 720x1280, 25 fps, H.264, no sound, in assets/clips/. Run from this folder: sh clips.sh
set -e
R="$HOME/Movies/CapCut/FlyX Reels.mp4"
A1="$HOME/Movies/CapCut/Flyx AD 1.mp4"
A2="$HOME/Movies/CapCut/Flyx AD 2.mp4"
P="$HOME/Movies/CapCut/5. rész intro.mp4"
I="$HOME/Downloads/interveiw 8.5.mp4"
cut() { # name source start seconds
  ffmpeg -v error -y -ss "$3" -i "$2" -t "$4" -an -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=25,format=yuv420p" \
    -c:v libx264 -preset slow -crf 21 -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709 "assets/clips/$1.mp4"
}
# FlyX Tenerife: three phones
cut flyx-1 "$R" 0.4 3.6      # the owner talking
cut flyx-2 "$A2" 7.3 3.6     # the 5D flying cinema
cut flyx-3 "$R" 9.3 3.6      # guests in the seats
# podcast and interview: three phones
cut pod-1 "$P" 18.3 3.6      # András at the mic
cut pod-2 "$I" 26.7 3.6      # the car interview
cut pod-3 "$P" 15.2 3.6      # András at the mic
# the six services, one phone each
cut svc-video "$A2" 7.6 1.2
cut svc-social "$I" 7.8 1.2
cut svc-ads "$A1" 0.3 1.2
cut svc-web "$R" 19.2 1.2
cut svc-auto "$P" 11.4 1.2
cut svc-strat "$A2" 0.3 1.2
# behind the numbers
cut roas-1 "$I" 31.0 2.8
cut roas-2 "$R" 19.6 2.8
cut roas-3 "$A2" 8.2 2.8
cut mft-1 "$R" 14.0 3.0      # the flight on the cinema screen
cut mft-2 "$A2" 14.6 3.0
cut mft-3 "$I" 28.7 3.0      # the car interview
cut m300-1 "$P" 24.0 3.0
cut m300-2 "$I" 43.0 3.0
cut m300-3 "$P" 35.0 3.0
echo done
