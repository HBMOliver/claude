#!/bin/sh
# Cuts the footage film v6 uses into assets/clips/ and the reel-wall stills into assets/tiles/ (25 fps, H.264, no
# sound, BT.709). All of it is the team's own work: the FlyX promo they made (only shots filmed in the cinema; the
# promo's aerials, volcano, ship and cockpit may be the ride's licensed film, so they stay out), Gyenis András's stage
# intro, Bálint's showreel (he is on the team), their FlyX ad, and the founder's own footage from Photos (Latvia,
# Türkiye, Bridle Up Hope). No stock B-roll, no child in the foreground, no other brand as the subject; people whose
# age or consent is not known only appear small in the wall.
# Run from this folder: sh clips.sh <photos-folder>   (the Photos originals in latvia/, turkiye/, bridleup/)
# The six service reels (ph-svc-video, -social, -web, -web-en, -auto, -strat) are v5's, copied from ../film/assets/clips.
set -e
DMC="$HOME/Downloads/DMC Promo video.mp4"            # their FlyX Tenerife promo, 4K
INTRO="$HOME/Movies/CapCut/INTRO-FINAL.mp4"          # Gyenis András's stage intro
B="$HOME/Downloads/Balint portfolio (YouTube)/01 Referencia videó (Klinger Bálint - Videóvágó, hangmérnök, fotós) [z9idMTbdpeE].mp4"
AD1="$HOME/Movies/CapCut/Flyx AD 1.mp4"              # their ad for FlyX
D2="$HOME/Movies/CapCut/funny assets/drive2"         # FlyX iPhone clips (HLG)
PH="${1:?usage: sh clips.sh <photos-folder>}"
LV="$PH/latvia"; TR="$PH/turkiye"; BU="$PH/bridleup"
mkdir -p assets/clips assets/tiles
OUT="-an -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709"
# HLG (iPhone HDR) to SDR BT.709
HLG="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv"
clip() { # name source start seconds filter
  ffmpeg -v error -y -ss "$3" -i "$2" -t "$4" -vf "$5,fps=25,format=yuv420p" $OUT "assets/clips/$1.mp4"
}
# full-frame shots (1920 x 1080)
clip w-crowd "$DMC" 34.0 2.6 "scale=1920:1080:flags=lanczos"        # the cinema laughing (claim, second line)
clip w-screen "$DMC" 25.5 2.4 "scale=1920:1080:flags=lanczos"       # the screen and the seats (FlyX Tenerife)
# the sun going down over the Baltic (Latvia, 4K60): its last, steady 2.95 s at 0.45x (6.5 s, smooth from 60 fps), a band
# across sun and horizon for the wide cut
ffmpeg -v error -y -ss 11.6 -t 2.95 -i "$LV/IMG_1737.MOV" -vf "setpts=PTS/0.45,crop=iw:iw*9/16:0:ih*0.36-iw*9/32,scale=1920:1080:flags=lanczos,fps=25,format=yuv420p" $OUT assets/clips/w-sunset.mp4
# two service reels of their own (1080 x 1920): the arena (Videó) and their FlyX ad's sunset (Hirdetés)
clip ph-svc-stage "$INTRO" 1.0 0.9 "crop=608:1080:(iw-608)/2:0,scale=1080:1920:flags=lanczos"
clip ph-svc-ads2 "$AD1" 8.2 0.9 "scale=1080:1920:flags=lanczos"
# the reel wall: 9:16 stills (460 x 818), cut to cover from wide frames at focus x, or from upright ones
still() { # name source time focus-x [extra filter before]
  pre="${5:+$5,}"
  ffmpeg -v error -y -ss "$3" -i "$2" -frames:v 1 -vf "${pre}scale=-2:818:flags=lanczos,crop=460:818:'min(max(0,iw*$4-230),iw-460)':0" -q:v 3 "assets/tiles/$1.jpg"
}
upst() { # name source time [extra filter before]: an upright source
  pre="${4:+$4,}"
  ffmpeg -v error -y -ss "$3" -i "$2" -frames:v 1 -vf "${pre}scale=460:818:force_original_aspect_ratio=increase:flags=lanczos,crop=460:818" -q:v 3 "assets/tiles/$1.jpg"
}
still t01 "$DMC" 27.0 0.55          # the screen and the seats
still t02 "$DMC" 46.5 0.45          # laughing in the seats
still t03 "$DMC" 35.0 0.62          # laughing in the dark
still t04 "$DMC" 44.8 0.42          # waves on the screen
still t05 "$INTRO" 1.3 0.5          # the arena
still t06 "$INTRO" 2.2 0.36         # András on stage
upst t07 "$LV/IMG_1746.MOV" 4.0     # gold-lit waves
upst t08 "$LV/IMG_1619.MOV" 2.0     # foam
upst t09 "$LV/IMG_1628.MOV" 3.0     # the breakwater
upst t10 "$LV/IMG_1672.MOV" 2.0     # the crew on the beach
upst t11 "$LV/IMG_1828.MOV" 10.0    # a silhouette at sunset
still t12 "$TR/IMG_1075.MOV" 5.0 0.5    # under the Taurus mountains
still t13 "$TR/video-output-45BA08E3-4BA9-41AC-BF6E-29273178748E-1.mov" 3.0 0.6   # the cat
still t14 "$B" 6.5 0.5              # a studio shoot
still t15 "$B" 35.0 0.5             # the microphone
still t16 "$B" 4.5 0.5              # hands on the keys
still t17 "$B" 8.5 0.45             # writing the plan
upst t18 "$D2/b218_IMG_6216.MOV" 2.0 "$HLG"   # the sunset on the FlyX screen
upst t19 "$D2/b216_IMG_6214.MOV" 3.0 "$HLG"   # clouds on the FlyX screen
upst t20 "$D2/b146_IMG_0472.MOV" 3.0 "$HLG"   # mountains on the FlyX screen, from the back row
upst t21 "$LV/IMG_1539.MOV" 2.0     # a cobbled street in Liepāja
still t22 "$B" 17.5 0.5             # the green-screen studio
echo done
