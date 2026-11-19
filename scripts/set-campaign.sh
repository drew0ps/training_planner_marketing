#!/bin/sh
# Puts an App Store Connect campaign on the site's App Store links, so installs that start
# here are counted under that campaign in App Analytics; nothing else on the site measures
# anything. The provider token comes from Generate Campaign Link in App Analytics; the
# campaign name is yours (40 characters at most, letters, digits, - and _).
#
# It rewrites the download links of every page, the blog's posts and drafts included, and
# their Smart App Banners. The JSON-LD keeps the plain link. Run it again to change the
# campaign, or with --clear to take it off.
#
# Usage: scripts/set-campaign.sh <provider token> [campaign, default "site"]
#        scripts/set-campaign.sh --clear
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
app_id="6824840650"

if [ "${1:-}" = "" ]; then
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

query=""
banner=""
if [ "$1" != "--clear" ]; then
  token="$1"
  campaign="${2:-site}"
  case "$token" in *[!0-9]*) echo "The provider token is a number: $token" >&2; exit 2 ;; esac
  case "$campaign" in *[!A-Za-z0-9_-]*) echo "Letters, digits, - and _ only: $campaign" >&2; exit 2 ;; esac
  if [ "${#campaign}" -gt 40 ]; then echo "40 characters at most: $campaign" >&2; exit 2; fi
  # In an HTML attribute the & is written &amp;
  query="?pt=$token&amp;ct=$campaign&amp;mt=8"
  banner=", affiliate-data=pt=$token&amp;ct=$campaign"
fi

cd "$site"
for page in index.html press.html privacy.html support.html blog/*.html _drafts/*.html; do
  file="$site/$page"
  [ -f "$file" ] || continue
  QUERY="$query" BANNER="$banner" APP_ID="$app_id" perl -0pi -e '
    my ($q, $b, $id) = @ENV{qw(QUERY BANNER APP_ID)};
    # Links: whatever campaign was there goes, then the new one comes
    s{(href="https://apps\.apple\.com/[^"?]*id\Q$id\E)(?:\?[^"]*)?"}{$1$q"}g;
    s{(<meta name="apple-itunes-app" content="app-id=\Q$id\E)[^"]*"}{$1$b"}g;
  ' "$file"
  links="$(grep -c "href=\"https://apps.apple.com/[^\"]*id$app_id" "$file" || true)"
  echo "$page: $links App Store links${query:+ with $query}"
done
