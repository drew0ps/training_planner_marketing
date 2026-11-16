#!/bin/sh
# Refreshes the site's clips from the app repository.
#
# The clips are the ones make -C Branding clips films there (Branding/Clips/Web: the app
# in use on the iPhone, 720 px wide H.264 without sound, one per moment). Each is copied
# to clips/ with a still beside it, its first frame as a JPEG, which the page shows until
# the clip plays. Needs ffmpeg for the stills (brew install ffmpeg).
#
# The page names its clips itself (the data-clip attributes in index.html), with a line
# about each: a clip the page names and the app no longer films is reported at the end.
#
# Usage: scripts/update-clips.sh [path to the app repository]
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
app="${1:-$site/../Training Planner}"
filmed="$app/Branding/Clips/Web"

if ! ls "$filmed"/*.mp4 > /dev/null 2>&1; then
  echo "No clips at $filmed: run make -C Branding clips in the app repository first" >&2
  exit 1
fi
command -v ffmpeg > /dev/null || { echo "ffmpeg is needed: brew install ffmpeg" >&2; exit 1; }

mkdir -p "$site/clips"
rm -f "$site/clips"/*.mp4 "$site/clips"/*.jpg
for source in "$filmed"/*.mp4; do
  name="$(basename "$source" .mp4)"
  cp "$source" "$site/clips/$name.mp4"
  ffmpeg -y -v error -i "$source" -frames:v 1 -q:v 4 "$site/clips/$name.jpg"
done

ls -la "$site/clips"

missing=0
for name in $(grep -o 'data-clip="[^"]*"' "$site/index.html" | sed 's/.*="\(.*\)"/\1/' | sort -u); do
  if [ ! -f "$site/clips/$name.mp4" ]; then
    echo "index.html shows the clip \"$name\", which wasn't filmed" >&2
    missing=1
  fi
done
exit "$missing"
