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

# 4. Voix calée phrase par phrase (coupes uniquement dans les pauses de la voix)
#    voix 0 à 30,59 s -> position d'origine : plans 1 à 5
#      ("Vous pensez à votre mère…" … "Pas de panique douanière.")
#    voix 30,59 s à la fin ("Expédiez maintenant. Votre mère vous attend.") -> 40,79 s,
#      pour que la phrase démarre à 41,0 s sur le CTA du plan 7.
CUT=30.59
CTA_AT=40.79
ffmpeg -y -v error -i "$OUT/plans/mbc-cargo-silent.mp4" -i "$AUDIO" -filter_complex "
  [1:a]atrim=0:$CUT,asetpts=PTS-STARTPTS,afade=t=out:st=$(echo "$CUT-0.05" | bc):d=0.05[a1];
  [1:a]atrim=start=$CUT,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,adelay=delays=$(echo "$CTA_AT*1000/1" | bc):all=1[a2];
  [a1][a2]amix=inputs=2:normalize=0:duration=longest,apad=whole_dur=$TOTAL[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t "$TOTAL" -movflags +faststart "$FINAL"

# 5. Vérification des durées
for n in 1 2 3 4 5 6 7; do
  printf 'plan-%s : %ss\n' "$n" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/plans/plan-$n.mp4")"
done
printf 'final  : %ss -> %s\n' "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL")" "$FINAL"
