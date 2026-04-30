#!/usr/bin/env bash
#
# Populate backend/data/samples/ with crosswalk video clips.
#
# Order of preference:
#   1) If repo-root samples/ already has *.mp4, copy any new ones across.
#   2) Otherwise, attempt to download a small set of Pexels clips.
#
# Pexels URLs may change over time; if downloads fail, drop your own
# *.mp4 files into backend/data/samples/ manually.
#
set -euo pipefail

cd "$(dirname "$0")/.."

ROOT_SAMPLES="samples"
DEST="backend/data/samples"
mkdir -p "$DEST"

copied=0
if compgen -G "${ROOT_SAMPLES}/*.mp4" > /dev/null; then
  echo "Found $(ls -1 ${ROOT_SAMPLES}/*.mp4 | wc -l | tr -d ' ') clip(s) at ${ROOT_SAMPLES}/"
  for src in "${ROOT_SAMPLES}"/*.mp4; do
    name=$(basename "$src")
    dst="${DEST}/${name}"
    if [[ -f "$dst" ]]; then
      echo "  skip (exists): ${name}"
    else
      echo "  copy: ${name}"
      cp "$src" "$dst"
      copied=$((copied + 1))
    fi
  done
fi

if [[ $copied -eq 0 ]] && ! compgen -G "${DEST}/*.mp4" > /dev/null; then
  echo
  echo "No samples found at ${ROOT_SAMPLES}/ or ${DEST}/."
  echo "Attempting to download a small Pexels set (URLs may break over time)…"
  echo

  declare -a URLS=(
    "https://videos.pexels.com/video-files/12066181/12066181-hd_2320_1080_30fps.mp4"
    "https://videos.pexels.com/video-files/13603867/13603867-uhd_3328_1440_24fps.mp4"
    "https://videos.pexels.com/video-files/18437770/18437770-uhd_3840_2160_50fps.mp4"
  )

  for url in "${URLS[@]}"; do
    fname=$(basename "$url")
    dst="${DEST}/${fname}"
    if [[ -f "$dst" ]]; then
      echo "  skip (exists): ${fname}"
      continue
    fi
    echo "  download: ${fname}"
    if ! curl -fsSL --retry 2 -o "$dst" "$url"; then
      echo "    failed — leaving placeholder out"
      rm -f "$dst"
    fi
  done
fi

echo
echo "Samples in ${DEST}:"
ls -1 "${DEST}"/*.mp4 2>/dev/null | xargs -I{} basename {} | sed 's/^/  /' \
  || echo "  (none)"
