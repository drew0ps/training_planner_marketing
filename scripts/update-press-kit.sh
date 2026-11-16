#!/bin/sh
# Builds the press kit from the app repository: the app icon, all the devices in one
# picture, six App Store screenshots, the app in a short video and the fact sheet, in
# press/ and as one zip.
#
# The screenshots are the composed App Store set (Branding/Screenshots/AppStore, from
# swift Branding/make-screenshots.swift), saved as JPEG: they have no transparency, and a
# journalist's download should be megabytes, not tens of them. press/fact-sheet.txt is
# written by hand and kept as it is. The video is the App Store's app preview (make -C
# Branding clips films it); without it the kit is made of the pictures alone.
#
# Usage: scripts/update-press-kit.sh [path to the app repository]
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
app="${1:-$site/../Training Planner}"
shots="$app/Branding/Screenshots/AppStore"
press="$site/press"

if [ ! -d "$shots" ]; then
  echo "No App Store screenshots at $shots: run swift Branding/make-screenshots.swift first" >&2
  exit 1
fi

mkdir -p "$press"
cp "$app/Branding/AppIcon-1024.png" "$press/app-icon.png"
sips --resampleWidth 2400 -s format png "$app/Branding/CreativeAssets/DeviceLineup.png" \
  --out "$press/devices.png" > /dev/null

# App Store name → the name in the kit
for pair in 01-today:today 03-workout:workout 04-evaluation:evaluation 09-board:board \
  11-readiness:readiness 14-medals:medals; do
  source="${pair%%:*}"
  name="${pair##*:}"
  sips -s format jpeg -s formatOptions 88 "$shots/$source.png" \
    --out "$press/screenshot-$name.jpg" > /dev/null
done

# The app in use: the App Store's app preview, 886 x 1920, under half a minute, no sound
preview="$app/Branding/Clips/AppStore/app-preview-6.9.mp4"
rm -f "$press/app-preview.mp4"
if [ -f "$preview" ]; then
  cp "$preview" "$press/app-preview.mp4"
else
  echo "No app preview at $preview: the kit goes without its video" >&2
fi

# One download, with a folder inside so it unpacks tidily
kit="TrainingPlanner-press-kit"
work="$(mktemp -d)"
mkdir "$work/$kit"
cp "$press/app-icon.png" "$press/devices.png" "$press"/screenshot-*.jpg "$press/fact-sheet.txt" "$work/$kit/"
if [ -f "$press/app-preview.mp4" ]; then cp "$press/app-preview.mp4" "$work/$kit/"; fi
rm -f "$press/$kit.zip"
(cd "$work" && zip -q -r -X "$press/$kit.zip" "$kit")
rm -rf "$work"

ls -la "$press"
