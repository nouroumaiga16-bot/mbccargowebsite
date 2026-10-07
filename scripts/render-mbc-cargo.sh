#!/usr/bin/env bash
# MBC Cargo — rendu HyperFrames des 7 plans + assemblage + voix
# Usage : bash scripts/render-mbc-cargo.sh   (depuis la racine du dépôt)
set -euo pipefail

export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"
AUDIO="audio/mbc-cargo-voix-v1.mp3"
OUT="output"
FINAL="$OUT/mbc-cargo-motion-45s.mp4"
TOTAL=45

# 1. Plans HTML -> compositions HyperFrames (durées exactes)
node scripts/build-hyperframes.mjs
mkdir -p "$OUT/plans"

# 2. Rendu de chaque plan en MP4 1920x1080 / 30 fps
: > "$OUT/plans/concat.txt"
for n in 1 2 3 4 5 6 7; do
  $HF lint "hyperframes/plan-$n"
  $HF render "hyperframes/plan-$n" -o "$OUT/plans/plan-$n.mp4" --fps 30 --quality delivery --quiet
  echo "file 'plan-$n.mp4'" >> "$OUT/plans/concat.txt"
done

# 3. Assemblage dans l'ordre (mêmes paramètres d'encodage -> copie sans ré-encodage)
ffmpeg -y -v error -f concat -safe 0 -i "$OUT/plans/concat.txt" -c copy "$OUT/plans/mbc-cargo-silent.mp4"

# 4. Voix calée à 0:00, complétée par du silence jusqu'à 45 s
ffmpeg -y -v error -i "$OUT/plans/mbc-cargo-silent.mp4" -i "$AUDIO" \
  -map 0:v -map 1:a -c:v copy -af "apad=whole_dur=$TOTAL" -c:a aac -b:a 192k \
  -t "$TOTAL" -movflags +faststart "$FINAL"

# 5. Vérification des durées
for n in 1 2 3 4 5 6 7; do
  printf 'plan-%s : %ss\n' "$n" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/plans/plan-$n.mp4")"
done
printf 'final  : %ss -> %s\n' "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL")" "$FINAL"
