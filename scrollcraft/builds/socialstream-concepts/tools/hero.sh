#!/bin/sh
# usage: sh tools/hero.sh <master-wide> <master-tall> [suffix] [poster s]   (from this build's folder)
# Writes the site's cuts of the brand film into assets/ from the film's masters (since 2026-11-16 the sizzle,
# video/sizzle/): hero-1080 (Mix's opening on a wide screen), hero-v-720 (Mix's card and phones) and hero-540 (smaller
# frames on the other concept pages; tools/site.mjs leaves it out of the live site), each with the suffix: "" for
# Hungarian, "-en" for English. Two-pass H.264, silent (the page plays the film muted), BT.709 tags, faststart; the
# same settings as video/film/encode.sh, which made film v5's. With the Hungarian pair (no suffix) it also writes
# the two posters at the poster time (default 2.4 s): one pair serves both languages, so it must be a frame without
# words (in the sizzle the logo stands whole on the wall of reels from about 2.2 s to 2.8 s).
# The two masters must run on one clock: kit.js crossfades the wide cut into the upright one at the same moment.
set -e
W="$1"; T="$2"; S="${3:-}"; P="${4:-2.4}"
[ -f "$W" ] && [ -f "$T" ] || { echo "usage: sh tools/hero.sh <master-wide> <master-tall> [suffix] [poster s]" >&2; exit 1; }
O=assets; L=$(mktemp -d)
enc() { # in out WxH kbps
  for pass in 1 2; do
    out=/dev/null; [ "$pass" = 2 ] && out="$2"
    ffmpeg -v error -y -i "$1" -an -vf "scale=${3}:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -profile:v high \
      -b:v "${4}k" -maxrate "$(( $4 * 2 ))k" -bufsize "$(( $4 * 4 ))k" -pass "$pass" -passlogfile "$L/pl" \
      -map_metadata -1 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart -f mp4 "$out"
  done
}
enc "$W" "$O/hero-1080$S.mp4" 1920:1080 2100
enc "$W" "$O/hero-540$S.mp4" 960:540 1100
enc "$T" "$O/hero-v-720$S.mp4" 720:1280 1500
if [ -z "$S" ]; then
  ffmpeg -v error -y -ss "$P" -i "$W" -frames:v 1 -vf "scale=1600:900:flags=lanczos" -q:v 3 "$O/hero-poster.jpg"
  ffmpeg -v error -y -ss "$P" -i "$T" -frames:v 1 -vf "scale=720:1280:flags=lanczos" -q:v 3 "$O/hero-v-poster.jpg"
fi
rm -r "${L:?}"
ls -l "$O"/hero-*"$S".mp4
