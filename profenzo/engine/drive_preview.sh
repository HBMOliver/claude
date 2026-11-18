#!/usr/bin/env bash
# Drive-sized preview of a rendered video: 540x960, two-pass H.264 aimed at a file size the Drive connector
# accepts in one call (about 3 MB). Usage: drive_preview.sh in.mp4 out.mp4 [target MiB, default 2.85]
set -euo pipefail
src=$1; out=$2; target=${3:-2.85}
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src")
vb=$(python3 -c "print(int(($target*8*1024*1024/$dur - 48000)/1000))")
log=$(mktemp -d)/pass
common=(-vf scale=540:960:flags=lanczos -c:v libx264 -preset slow -tune animation -b:v "${vb}k" -passlogfile "$log")
ffmpeg -v error -y -i "$src" "${common[@]}" -pass 1 -an -f mp4 /dev/null
ffmpeg -v error -y -i "$src" "${common[@]}" -pass 2 -c:a aac -b:a 48k -ac 1 -movflags +faststart "$out"
rm -rf "$(dirname "$log")"
echo "$(sha256sum "$out" | cut -d' ' -f1) $(stat -c %s "$out") $out (${vb}k)"
