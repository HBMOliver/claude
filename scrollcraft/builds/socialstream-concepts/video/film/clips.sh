#!/bin/sh
# Cuts the footage the film uses into assets/clips/ (25 fps, H.264, no sound, BT.709 tags). All of it is the team's
# own work: their client reels, Bálint's showreel and promo (he is on the team), and the founder's own footage from
# the Photos library (Türkiye, Latvia, Bridle Up Hope in Sóskút). No stock B-roll, no child in the foreground,
# no other brand as the subject, and nobody recognisable whose age or consent is not known (the Türkiye film was a
# youth exchange, and Bridle Up Hope works with girls), so the people in it are small, seen from behind, or the team.
# Run from this folder: sh clips.sh <photos-folder>
#   <photos-folder>: the founder's Photos originals, exported unmodified into turkiye/, latvia/ and bridleup/ (file names
#   as Photos gives them; the film's README lists them). The website reel is made separately (node webclip.mjs).
set -e
R="$HOME/Movies/CapCut/FlyX Reels.mp4"
A1="$HOME/Movies/CapCut/Flyx AD 1.mp4"
P="$HOME/Movies/CapCut/5. rész intro.mp4"
I="$HOME/Downloads/interveiw 8.5.mp4"
B="$HOME/Downloads/Balint portfolio (YouTube)/01 Referencia videó (Klinger Bálint - Videóvágó, hangmérnök, fotós) [z9idMTbdpeE].mp4"
C="$HOME/Downloads/Balint portfolio (YouTube)/05 Miskolc Plaza sakk promóció [h2ZJTq3HAO0].mp4"
PH="${1:?usage: sh clips.sh <photos-folder>}"
TRF="$PH/turkiye/copy_FCE53987-21D8-4AF3-8984-32930C2FC7FE.mov"   # their short film in Kemer, Türkiye (Oct 2025)
TRC="$PH/turkiye/video-output-45BA08E3-4BA9-41AC-BF6E-29273178748E-1.mov"   # a shot from the shoot (a cat)
TRV="$PH/turkiye/IMG_1075.MOV"                                     # the clean-up day
LV="$PH/latvia"                                                    # the June 2025 content challenge
BU="$PH/bridleup"                                                  # Bridle Up Hope, Sóskút
mkdir -p assets/clips
enc() { # name source start seconds filter
  ffmpeg -v error -y -ss "$3" -i "$2" -t "$4" -an -vf "$5,fps=25,format=yuv420p" -c:v libx264 -preset slow -crf 19 \
    -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709 "assets/clips/$1.mp4"
}
fill() { # name source start seconds width height: scale to cover, crop the middle
  enc "$1" "$2" "$3" "$4" "scale=$5:$6:force_original_aspect_ratio=increase:flags=lanczos,crop=$5:$6"
}
upright() { # name source start seconds x: a 9:16 window out of a 16:9 frame, centred at x (0-1), 608 x 1080
  enc "$1" "$2" "$3" "$4" "scale=-2:1080:flags=lanczos,crop=608:1080:'min(max(0,iw*$5-304),iw-608)':0"
}

# the phone (seen as large as the whole frame, so full size)
fill ph-flyx "$R" 0.0 6.7 1080 1920          # the owner, then the flight over the sea as the camera dives in
fill ph-pod "$I" 28.0 4.3 1080 1920          # the car interview (the clean part, no inserts)
# the six services, one reel each (seen at phone size)
upright ph-svc-video "$B" 31.0 1.3 0.5       # the clapperboard
fill ph-svc-social "$LV/IMG_1672.MOV" 0.2 1.3 1080 1920   # the crew carries the tripod down to the beach (Latvia)
fill ph-svc-ads "$A1" 0.3 1.3 1080 1920      # their ad for FlyX
# ph-svc-web and ph-svc-web-en: their own site scrolled on a phone, made by webclip.mjs (see the README)
upright ph-svc-auto "$B" 10.2 1.3 0.55       # code on a screen
upright ph-svc-strat "$B" 8.0 1.3 0.45       # a hand writing the plan
# the last reel, which the phone hands to the wall: the sun going down over the Baltic (Latvia, 4K at 60 fps), its
# steady 2.7 s slowed to 0.6x (4.5 s, smooth from 60 fps); upright for the tall cut, a band across sun and horizon for
# the wide one
slow() { # name source start seconds filter
  ffmpeg -v error -y -ss "$3" -t "$4" -i "$2" -an -vf "setpts=PTS/0.6,$5,fps=25,format=yuv420p" -c:v libx264 -preset slow \
    -crf 18 -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709 "assets/clips/$1.mp4"
}
slow ph-last-tall "$LV/IMG_1737.MOV" 11.9 2.7 "scale=1080:1920:flags=lanczos"
slow ph-last-wide "$LV/IMG_1737.MOV" 11.9 2.7 "crop=iw:iw*9/16:0:ih*0.36-iw*9/32,scale=1920:1080:flags=lanczos"
# the stream: fourteen reels rushing past (540 x 960); st-01 passes the camera first, st-14 last
upright st-01 "$TRF" 91.2 2.5 0.5            # dancing in the rain on the main square
upright st-02 "$TRF" 149.2 2.5 0.25        # a volunteer clearing litter under the Taurus mountains
upright st-03 "$B" 4.0 2.5 0.6               # hands on the keys
fill st-04 "$BU/IMG_2196.MOV" 12.9 2.5 540 960   # a horse cantering in the arena
upright st-05 "$TRC" 3.0 2.5 0.6            # a cat along a sunlit hedge
fill st-06 "$C" 13.0 2.5 540 960             # the chess promo
fill st-07 "$LV/IMG_1628.MOV" 1.5 2.5 540 960    # the breakwater
upright st-08 "$B" 69.0 2.5 0.5              # a neon city, animated
upright st-09 "$B" 36.0 2.5 0.4              # at the microphone
upright st-10 "$TRF" 235.2 2.5 0.5           # through the bazaar, from behind
fill st-11 "$LV/IMG_1746.MOV" 1.0 2.5 540 960    # gold-lit waves
upright st-12 "$B" 58.5 2.5 0.5              # an animation
fill st-13 "$BU/BU_hun_subt_20251101.mp4" 2.0 2.5 540 960   # their film for the foundation, before its captions start
upright st-14 "$TRV" 0.5 2.5 0.28            # the clean-up crew heading out
echo done
