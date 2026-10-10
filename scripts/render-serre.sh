#!/usr/bin/env bash
# « Culture sous serre » (guide) — rendu HyperFrames (26 s, musique + effets) en 9:16, 1:1 et 16:9
# Usage : bash scripts/render-serre.sh   (depuis la racine du dépôt)
set -euo pipefail
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"
node motion/serre/build.mjs
mkdir -p output
for fmt in 9x16 1x1 16x9; do
  $HF lint "motion/serre/build/$fmt"
  $HF render "motion/serre/build/$fmt" -o "output/culture-sous-serre-$fmt.mp4" --fps 30 --quality delivery --quiet
  printf 'output/culture-sous-serre-%s.mp4 : %ss\n' "$fmt" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "output/culture-sous-serre-$fmt.mp4")"
done
