#!/usr/bin/env bash
# Bracelet sport LED — rendu HyperFrames (30 s, musique + effets) en 9:16, 1:1 et 16:9
# Usage : bash scripts/render-bracelet.sh   (depuis la racine du dépôt)
set -euo pipefail
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"
node motion/bracelet/build.mjs
mkdir -p output
for fmt in 9x16 1x1 16x9; do
  $HF lint "motion/bracelet/build/$fmt"
  $HF render "motion/bracelet/build/$fmt" -o "output/bracelet-sport-led-$fmt.mp4" --fps 30 --quality delivery --quiet
  printf 'output/bracelet-sport-led-%s.mp4 : %ss\n' "$fmt" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "output/bracelet-sport-led-$fmt.mp4")"
done
