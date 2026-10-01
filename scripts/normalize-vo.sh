#!/bin/zsh
# Normalises the voiceover clips to -16 LUFS (true peak -1.5 dBTP). loudnorm keeps the
# timing sample-accurate, so the TTS word timestamps stay valid. Raw clips are kept in
# out/cache/raw-vo/ so re-running never normalises twice.
set -e
cd "$(dirname "$0")/.."
mkdir -p out/cache/raw-vo
for f in public/audio/vo/*.mp3; do
  raw="out/cache/raw-vo/$(basename "$f")"
  # a newer clip from voiceover.ts --force replaces the cached raw copy
  if [[ ! -f "$raw" || "$f" -nt "$raw" ]]; then cp "$f" "$raw"; fi
  ffmpeg -y -v error -i "$raw" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 44100 -b:a 192k "$f"
  touch -r "$raw" "$f"
  echo "normalised $(basename "$f")"
done
