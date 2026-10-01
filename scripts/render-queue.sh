#!/bin/zsh
# Renders shots one after another (the GPU is the bottleneck, so sequential = fastest overall).
# Usage: scripts/render-queue.sh intro why outro ...
cd "$(dirname "$0")/.."
for s in "$@"; do
  rm -rf "public/renders/$s"
  start=$(date +%s)
  /Applications/Blender.app/Contents/MacOS/Blender -b -P blender/render.py -- --shot "$s" 2>&1 | grep -E "\[render\]|Error|Traceback"
  echo "$s: $(ls public/renders/$s | grep -c jpg) frames in $(( $(date +%s) - start ))s"
done
npx tsx scripts/collect-renders.ts
