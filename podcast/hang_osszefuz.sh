#!/usr/bin/env bash
# Mondatonkénti hangfájlok összefűzése szünetekkel (a szájszinkron-animációhoz).
# Használat: ./hang_osszefuz.sh <kimenet.wav> <szunet_mp> 1.mp3 2.mp3 3.mp3 ...
# A kimenet: egy hangsáv, minden mondat után <szunet_mp> csenddel (az utolsó után nincs).
# Mellé kiír egy idokodok.txt-t: melyik mondat mikor kezdődik/ér véget.
set -euo pipefail
OUT="$1"; GAP="$2"; shift 2
ARGS=(); FILTER=""; N=0
for f in "$@"; do ARGS+=(-i "$f"); N=$((N+1)); done
T=0; : > "${OUT%.*}_idokodok.txt"
for i in $(seq 0 $((N-1))); do
  FILTER+="[$i:a]aformat=sample_rates=44100:channel_layouts=mono[a$i];"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${@:$((i+1)):1}")
  printf "%d. mondat: %.2f – %.2f mp\n" $((i+1)) "$T" "$(echo "$T+$d" | bc -l)" >> "${OUT%.*}_idokodok.txt"
  T=$(echo "$T+$d+$GAP" | bc -l)
done
CONCAT=""
for i in $(seq 0 $((N-1))); do
  CONCAT+="[a$i]"
  if [ $i -lt $((N-1)) ]; then
    FILTER+="anullsrc=r=44100:cl=mono,atrim=0:${GAP}[s$i];"; CONCAT+="[s$i]"
  fi
done
CNT=$((2*N-1))
ffmpeg -v error -y "${ARGS[@]}" -filter_complex "${FILTER}${CONCAT}concat=n=${CNT}:v=0:a=1[out]" -map "[out]" "$OUT"
cat "${OUT%.*}_idokodok.txt"
