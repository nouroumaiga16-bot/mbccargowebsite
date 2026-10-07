#!/usr/bin/env bash
# MBC Cargo — rendu HyperFrames de la publicité explicative (45 s, sans voix off)
# Usage : bash scripts/render-mbc-cargo.sh [16x9|9x16|all]   (depuis la racine du dépôt)
#   16x9 -> output/mbc-cargo-pub-16x9.mp4   1920x1080 (YouTube, site, Facebook)
#   9x16 -> output/mbc-cargo-pub-9x16.mp4   1080x1920 (Reels, TikTok, Stories)
set -euo pipefail

export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"

node scripts/build-motion.mjs
mkdir -p output

render() {
  local fmt="$1" out="$2"
  $HF lint "motion/build/$fmt"
  $HF render "motion/build/$fmt" -o "$out" --fps 30 --quality delivery --quiet
  printf '%s : %ss\n' "$out" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")"
}

case "${1:-all}" in
  16x9) render 16x9 output/mbc-cargo-pub-16x9.mp4 ;;
  9x16) render 9x16 output/mbc-cargo-pub-9x16.mp4 ;;
  all)  render 16x9 output/mbc-cargo-pub-16x9.mp4
        render 9x16 output/mbc-cargo-pub-9x16.mp4 ;;
  *) echo "Format inconnu : $1 (16x9, 9x16 ou all)" >&2; exit 1 ;;
esac
