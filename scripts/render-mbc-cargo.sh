#!/usr/bin/env bash
# MBC Cargo — rendu HyperFrames de la vidéo de 45 s (voix incluse dans la composition)
# Usage : bash scripts/render-mbc-cargo.sh [16x9|9x16|all]   (depuis la racine du dépôt)
#   16x9 -> output/mbc-cargo-motion-45s.mp4        1920x1080
#   9x16 -> output/mbc-cargo-motion-45s-9x16.mp4   1080x1920 (Reels, TikTok, Stories)
set -euo pipefail

export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
HF="${HF:-npx --yes hyperframes@0.8.140}"

node scripts/build-motion.mjs
mkdir -p output

render() {
  local fmt="$1" out="$2"
  $HF lint "motion/build/$fmt"
  $HF render "motion/build/$fmt" -o "$out" --fps 30 --quality delivery --quiet
  # Voix normalisée à -14 LUFS (niveau des réseaux sociaux), image copiée telle quelle
  local m; m=$(ffmpeg -v info -i "$out" -vn -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$m" | grep "\"$1\"" | grep -oE '[-0-9.]+' | head -1; }
  ffmpeg -y -v error -i "$out" -map 0:v -map 0:a -c:v copy -t 45 -movflags +faststart -c:a aac -b:a 192k -ac 2 \
    -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
    "${out%.mp4}.tmp.mp4"
  mv "${out%.mp4}.tmp.mp4" "$out"
  printf '%s : %ss\n' "$out" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")"
}

case "${1:-all}" in
  16x9) render 16x9 output/mbc-cargo-motion-45s.mp4 ;;
  9x16) render 9x16 output/mbc-cargo-motion-45s-9x16.mp4 ;;
  all)  render 16x9 output/mbc-cargo-motion-45s.mp4
        render 9x16 output/mbc-cargo-motion-45s-9x16.mp4 ;;
  *) echo "Format inconnu : $1 (16x9, 9x16 ou all)" >&2; exit 1 ;;
esac
