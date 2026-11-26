#!/bin/zsh
# film.sh: the lock-screen film from the rendered loop (out/loop-h264.mp4).
# As Apple's own moving wallpapers are: HEVC Main 10, 3840 x 2160, BT.709, no sound; 60 frames a second.
# final/SocialStream-loop-40s.mov is the loop once; final/SocialStream-lock-screen.mov is the same loop six
# times in one file (4 minutes), because Apple's files are long and macOS may not start a short one again.
set -e
cd "$(dirname "$0")"
mkdir -p final
ffmpeg -hide_banner -loglevel error -y -i out/loop-h264.mp4 -an -c:v libx265 -preset medium -crf 16 -pix_fmt yuv420p10le \
  -x265-params "keyint=120:min-keyint=120:scenecut=0:open-gop=0:colorprim=bt709:transfer=bt709:colormatrix=bt709:log-level=error" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -tag:v hvc1 -movflags +faststart out/loop-hevc.mov
# The render starts where the logo's build starts, so its first frame has no logo; macOS shows the film's first
# frame as the desktop picture after every start. The loop is seamless, so it can begin anywhere: begin it 2 s
# before a build (at 38 s, a keyframe), where the finished logo stands. No re-encoding: the two pieces are copied.
ffmpeg -hide_banner -loglevel error -y -ss 38 -i out/loop-hevc.mov -c copy -tag:v hvc1 out/rot-a.mov
ffmpeg -hide_banner -loglevel error -y -i out/loop-hevc.mov -frames:v 2280 -c copy -tag:v hvc1 out/rot-b.mov   # 19 groups of 120 frames, exactly
printf "file 'rot-a.mov'\nfile 'rot-b.mov'\n" > out/rot.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i out/rot.txt -c copy -tag:v hvc1 -movflags +faststart "final/SocialStream-loop-40s.mov"
: > out/concat.txt
for k in 1 2 3 4 5 6; do echo "file '../final/SocialStream-loop-40s.mov'" >> out/concat.txt; done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i out/concat.txt -c copy -tag:v hvc1 -movflags +faststart "final/SocialStream-lock-screen.mov"
ls -la final/*.mov
