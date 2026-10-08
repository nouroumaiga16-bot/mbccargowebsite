#!/usr/bin/env bash
# Groupe « Cargo & Envois Diaspora Afrique » — rendu HyperFrames (32 s) en 9:16, 1:1 et 16:9
# Usage : bash scripts/render-groupe.sh   (depuis la racine du dépôt)
set -euo pipefail
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"
node motion/groupe/build.mjs
mkdir -p output
for fmt in 9x16 1x1 16x9; do
  $HF lint "motion/groupe/build/$fmt"
  $HF render "motion/groupe/build/$fmt" -o "output/groupe-diaspora-afrique-$fmt.mp4" --fps 30 --quality delivery --quiet
  printf 'output/groupe-diaspora-afrique-%s.mp4 : %ss\n' "$fmt" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "output/groupe-diaspora-afrique-$fmt.mp4")"
done
