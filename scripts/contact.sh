#!/bin/zsh
# Usage: scripts/contact.sh out.png cols file1 file2 ...  → tiled contact sheet (tiles 640 px wide).
# Inputs may be PNG or JPEG (all of the same type).
out=$1; cols=$2; shift 2
tmp=$(mktemp -d)
ext="${1##*.}"
i=1; for f in "$@"; do cp "$f" "$tmp/$(printf %03d $i).$ext"; i=$((i+1)); done
n=$((i-1)); rows=$(( (n + cols - 1) / cols ))
ffmpeg -v error -y -i "$tmp/%03d.$ext" -vf "scale=640:-1,pad=644:364:2:2:black,tile=${cols}x${rows}" -frames:v 1 "$out"
rm -rf "$tmp"
