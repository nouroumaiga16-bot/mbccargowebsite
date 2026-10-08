#!/usr/bin/env bash
# MBC Cargo — rendu HyperFrames du logo animé (6 s) dans les trois formats
# Usage : bash scripts/render-logo.sh   (depuis la racine du dépôt)
set -euo pipefail
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"
node motion/logo/build.mjs
mkdir -p output
for fmt in 16x9 9x16 1x1; do
  $HF lint "motion/logo/build/$fmt"
  $HF render "motion/logo/build/$fmt" -o "output/mbc-cargo-logo-$fmt.mp4" --fps 60 --quality delivery --quiet
  printf 'output/mbc-cargo-logo-%s.mp4 : %ss\n' "$fmt" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "output/mbc-cargo-logo-$fmt.mp4")"
done
