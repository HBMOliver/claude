#!/usr/bin/env bash
# Animált karakter beillesztése a podcast videó bal oldali székére.
#
# Használat:
#   ./beilleszt.sh <podcast.mp4> <karakter_zold_hatter.mp4> <kimenet.mp4> [X] [Y] [MAGASSAG]
#
#   X, Y      – a karakter bal felső sarka a podcast képen (pixel)
#   MAGASSAG  – a karakter magassága pixelben (a szélesség arányosan skálázódik)
#
# Környezeti változók (finomhangolás):
#   KEY_SIM=0.22  KEY_BLEND=0.08   – zöld háttér levétele
#   DESPILL=0.25                   – zöld szegély tompítása
#   SHADOW=0.35                    – árnyék erőssége (0 = nincs)
#   TEMP=0                         – színhőmérséklet-igazítás a karakteren (-0.1 hideg … +0.1 meleg)
#   OCCLUSION=maszk.png            – opcionális: a szék/asztal elé kerülő rész (fehér = előtér)
#   GRADE=1                        – a teljes videó finom színkorrekciója
#   KARAKTER_HANG=1                – a karakter videójának hangját is bekeveri
set -euo pipefail

BG="$1"; FG="$2"; OUT="$3"
X="${4:-200}"; Y="${5:-150}"; H="${6:-700}"
KEY_SIM="${KEY_SIM:-0.22}"; KEY_BLEND="${KEY_BLEND:-0.08}"
DESPILL="${DESPILL:-0.25}"; SHADOW="${SHADOW:-0.35}"; TEMP="${TEMP:-0}"
GRADE="${GRADE:-1}"; KARAKTER_HANG="${KARAKTER_HANG:-1}"

# 1) karakter: zöld le, szegély tisztítás, enyhe színillesztés, méretezés
FGCHAIN="[1:v]colorkey=0x00B140:${KEY_SIM}:${KEY_BLEND},despill=type=green:mix=${DESPILL}:expand=0,"
FGCHAIN+="colorbalance=rm=${TEMP}:bm=-${TEMP},scale=-2:${H}:flags=lanczos,format=rgba,split[fg][fgs]"

# 2) lágy árnyék: a karakter alfa csatornájából, elmosva, lefelé eltolva
SHCHAIN="[fgs]colorchannelmixer=rr=0:gg=0:bb=0:aa=${SHADOW},boxblur=18:2[sh]"

# 3) összeállítás
COMP="[0:v][sh]overlay=$((X+12)):$((Y+18)):format=auto[b1];[b1][fg]overlay=${X}:${Y}:format=auto:shortest=1[c]"

LAST="[c]"
INPUTS=(-i "$BG" -i "$FG")
if [[ -n "${OCCLUSION:-}" ]]; then
  # előtér (pl. szék karfa / asztal) visszarakása a karakter elé
  INPUTS+=(-i "$OCCLUSION")
  COMP+=";[2:v]format=gray,scale=iw:ih[m];[0:v][m]alphamerge[fgocc];[c][fgocc]overlay=0:0:format=auto[co]"
  LAST="[co]"
fi

if [[ "$GRADE" == "1" ]]; then
  # finom, természetes kolorgrade: kis kontraszt, meleg középtónus, enyhe vignetta
  COMP+=";${LAST}eq=contrast=1.05:saturation=1.06:gamma=0.98,colorbalance=rm=0.03:gm=0.0:bm=-0.02,vignette=PI/5[out]"
  LAST="[out]"
fi

if [[ "$KARAKTER_HANG" == "1" ]]; then
  AUD=(-filter_complex "${FGCHAIN};${SHCHAIN};${COMP};[0:a][1:a]amix=inputs=2:duration=first:normalize=0[a]" -map "$LAST" -map "[a]")
else
  AUD=(-filter_complex "${FGCHAIN};${SHCHAIN};${COMP}" -map "$LAST" -map 0:a?)
fi

ffmpeg -y "${INPUTS[@]}" "${AUD[@]}" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k "$OUT"
echo "Kész: $OUT"
