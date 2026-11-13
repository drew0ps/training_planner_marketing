#!/bin/sh
# Refreshes the site's images from the app repository.
#
# Screenshots come from the raw dark captures the AppStoreScreenshots UI test
# writes to Branding/Screenshots/Dark (1320 x 2868). They are resized to
# 780 px wide, twice the widest size the page shows them at, and saved as
# JPEG. The Open Graph image is the App Store search-results artwork, and
# the touch icon is the app icon.
#
# Usage: scripts/update-screenshots.sh [path to the app repository]
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
app="${1:-$site/../Training Planner}"
dark="$app/Branding/Screenshots/Dark"

if [ ! -d "$dark" ]; then
  echo "No dark captures at $dark" >&2
  exit 1
fi

mkdir -p "$site/screenshots"
for source in "$dark"/*.png; do
  name="$(basename "$source" .png)"
  sips --resampleWidth 780 -s format jpeg -s formatOptions 88 \
    "$source" --out "$site/screenshots/$name.jpg" > /dev/null
done

sips --resampleWidth 1200 -s format png \
  "$app/Branding/CreativeAssets/SearchResults-3x2-3840x2560.png" \
  --out "$site/og-image.png" > /dev/null

sips --resampleWidth 180 -s format png \
  "$app/Branding/AppIcon-1024.png" --out "$site/apple-touch-icon.png" > /dev/null

ls -la "$site/screenshots" "$site/og-image.png" "$site/apple-touch-icon.png"
