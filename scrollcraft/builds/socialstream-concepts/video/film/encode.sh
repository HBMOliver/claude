#!/bin/sh
# usage: encode.sh <master-wide> <master-tall> <out-dir> [suffix]
# Writes the site's three cuts (hero-1080, hero-540, hero-v-720, each with the suffix: "" for Hungarian, "-en" for
# English), two-pass H.264 with BT.709 tags. Without a suffix it also writes the two posters from 3.0 s, where the
# logo is complete (the same for both languages: the frame has no words).
set -e
W="$1"; T="$2"; O="$3"; S="${4:-}"
enc() { # in out WxH kbps
  for pass in 1 2; do
    out=/dev/null; [ "$pass" = 2 ] && out="$2"
    ffmpeg -v error -y -i "$1" -an -vf "scale=${3}:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -profile:v high \
      -b:v "${4}k" -maxrate "$(( $4 * 2 ))k" -bufsize "$(( $4 * 4 ))k" -pass "$pass" -passlogfile "$O/pl-$(basename "$2")" \
      -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart -f mp4 "$out"
  done
}
enc "$W" "$O/hero-1080$S.mp4" 1920:1080 2100
enc "$W" "$O/hero-540$S.mp4" 960:540 1100
enc "$T" "$O/hero-v-720$S.mp4" 720:1280 1500
if [ -z "$S" ]; then
  ffmpeg -v error -y -ss 3.0 -i "$W" -frames:v 1 -vf "scale=1600:900:flags=lanczos" -q:v 3 "$O/hero-poster.jpg"
  ffmpeg -v error -y -ss 3.0 -i "$T" -frames:v 1 -vf "scale=720:1280:flags=lanczos" -q:v 3 "$O/hero-v-poster.jpg"
fi
rm -f "$O"/pl-*
