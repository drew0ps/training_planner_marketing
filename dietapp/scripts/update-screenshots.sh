#!/bin/sh
# Refreshes the site's images from the app repository.
#
# Screenshots come from the framed set the app repository's
# Branding/make-screenshots.swift writes to Branding/Screenshots/Framed: the
# raw dark captures of the app on Apple's own iPhone chrome, transparent
# (948 x 1980). They are resized to 640 px wide, about twice the widest size
# the page shows them at, and kept as PNG for the transparency. The Apple
# Watch's come from the same set (Branding/make-device-shots.swift: the watch
# on its own chrome, 502 x 582) and are copied as they are. The Open Graph
# image is the App Store search-results artwork, and the touch icon is the app
# icon.
#
# Usage: scripts/update-screenshots.sh [path to the app repository]
# The app repository's "make -C Branding site" runs this, and "make -C Branding
# all" makes the pictures first.
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
app="${1:-$site/../../ios_diet_app}"
framed="$app/Branding/Screenshots/Framed"

if [ ! -d "$framed" ]; then
  echo "No framed captures at $framed: run make -C Branding captures pictures in the app repository first" >&2
  exit 1
fi

mkdir -p "$site/screenshots"
for source in "$framed"/*.png; do
  name="$(basename "$source" .png)"
  sips --resampleWidth 640 -s format png \
    "$source" --out "$site/screenshots/$name.png" > /dev/null
done

sips --resampleWidth 1200 -s format png \
  "$app/Branding/CreativeAssets/SearchResults-3x2-3840x2560.png" \
  --out "$site/og-image.png" > /dev/null

sips --resampleWidth 180 -s format png \
  "$app/DietApp/Assets.xcassets/AppIcon.appiconset/AppIcon.png" --out "$site/apple-touch-icon.png" > /dev/null

# The Apple Watch: the three screens the page shows
mkdir -p "$site/screenshots/devices"
cp "$framed/Apple-Watch/01-log.png" "$site/screenshots/devices/watch-log.png"
cp "$framed/Apple-Watch/02-recent.png" "$site/screenshots/devices/watch-recent.png"
cp "$framed/Apple-Watch/04-water.png" "$site/screenshots/devices/watch-water.png"

ls -la "$site/screenshots" "$site/screenshots/devices" "$site/og-image.png" "$site/apple-touch-icon.png"
