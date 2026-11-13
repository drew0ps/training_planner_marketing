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

sips --resampleWidth 1200 -s format png \
  "$app/Branding/CreativeAssets/SearchResults-3x2-3840x2560.png" \
  --out "$site/og-image.png" > /dev/null

sips --resampleWidth 180 -s format png \
  "$app/Branding/AppIcon-1024.png" --out "$site/apple-touch-icon.png" > /dev/null

ls -la "$site/screenshots" "$site/og-image.png" "$site/apple-touch-icon.png"
