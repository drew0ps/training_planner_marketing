#!/bin/sh
# Refreshes the site's images from the app repository.
#
# Screenshots come from the framed set swift Branding/make-screenshots.swift
# writes to Branding/Screenshots/Framed: the raw dark captures of the
# AppStoreScreenshots UI test on Apple's own iPhone chrome, transparent
# (948 x 1980). They are resized to 640 px wide, about twice the widest
# size the page shows them at, and kept as PNG for the transparency. The
# Open Graph image is the App Store search-results artwork, and the touch
# icon is the app icon.
#
# Usage: scripts/update-screenshots.sh [path to the app repository]
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
app="${1:-$site/../Training Planner}"
framed="$app/Branding/Screenshots/Framed"

if [ ! -d "$framed" ]; then
  echo "No framed captures at $framed: run swift Branding/make-screenshots.swift first" >&2
  exit 1
fi

mkdir -p "$site/screenshots"
rm -f "$site/screenshots"/*.jpg
for source in "$framed"/*.png; do
  name="$(basename "$source" .png)"
  sips --resampleWidth 640 -s format png \
    "$source" --out "$site/screenshots/$name.png" > /dev/null
done

# The other devices, from swift Branding/make-device-shots.swift
devices="$app/Branding/Screenshots/Framed"
mkdir -p "$site/screenshots/devices"
sips --resampleWidth 1200 -s format png "$devices/iPad-13-inch/01-today.png" \
  --out "$site/screenshots/devices/ipad-today.png" > /dev/null
sips --resampleWidth 1200 -s format png "$devices/Mac/01-today.png" \
  --out "$site/screenshots/devices/mac-today.png" > /dev/null
cp "$devices/Apple-Watch/01-today.png" "$site/screenshots/devices/watch-today.png"
cp "$devices/Apple-Watch/03-log-set.png" "$site/screenshots/devices/watch-log.png"
cp "$devices/iPhone-Duo/01-today.png" "$site/screenshots/devices/duo-today.png"

sips --resampleWidth 1200 -s format png \
  "$app/Branding/CreativeAssets/SearchResults-3x2-3840x2560.png" \
  --out "$site/og-image.png" > /dev/null

sips --resampleWidth 180 -s format png \
  "$app/Branding/AppIcon-1024.png" --out "$site/apple-touch-icon.png" > /dev/null

ls -la "$site/screenshots" "$site/og-image.png" "$site/apple-touch-icon.png"
