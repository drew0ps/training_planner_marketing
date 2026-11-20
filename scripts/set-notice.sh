#!/bin/sh
# Puts a notice at the top of the site's pages while a new version waits in App Review: the
# pages describe that version, the App Store still has the one before it, and a visitor
# should know that some of what they read arrives with the update. Take it off the day the
# version is out. With --mac, the version is out for iPhone and iPad and still to come on the
# Mac, whose App Store has the one before it.
#
# It rewrites what stands between the two "notice" comments under <body> in index.html and
# press.html, and nothing else. Run it again to change the wording.
#
# Usage: scripts/set-notice.sh <version in review> <version on the App Store> [what arrives with it]
#        scripts/set-notice.sh --mac <version out on iOS> <version on the Mac> [what arrives with it]
#        scripts/set-notice.sh --clear
#
# For example:
#   scripts/set-notice.sh 2.4 2.3 "the Apple Watch, iPad and Mac apps, readiness and medals"
#   scripts/set-notice.sh --mac 2.4.1 2.4 "a cleaner look with everything on cards"
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"

if [ "${1:-}" = "" ]; then
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

mac=no
if [ "$1" = "--mac" ]; then
  mac=yes
  shift
fi

notice=""
if [ "${1:-}" != "--clear" ]; then
  coming="${1:-}"
  current="${2:-}"
  arrives="${3:-}"
  for version in "$coming" "$current"; do
    case "$version" in
      "" | *[!0-9.]*) echo "Two versions are needed, such as 2.4 and 2.3; got \"$version\"" >&2; exit 2 ;;
    esac
  done
  # The words go into HTML: & and the angle brackets are written as entities
  arrives="$(printf '%s' "$arrives" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g')"
  if [ "$mac" = yes ]; then
    notice="<p class=\"notice\" role=\"note\"><strong>Version $coming is out for iPhone and iPad, and on its way to the Mac.</strong>
  Some of what this page shows of the Mac arrives with it${arrives:+, among them
  $arrives}. Until then the Mac App Store has version $current.</p>
"
  else
    notice="<p class=\"notice\" role=\"note\"><strong>Version $coming is in review at the App Store.</strong>
  Some of what this page shows arrives with it${arrives:+, among them
  $arrives}. Until then the App Store has version $current.</p>
"
  fi
fi

status=0
for page in index.html press.html; do
  file="$site/$page"
  [ -f "$file" ] || continue
  if ! grep -q '<!-- notice:' "$file" || ! grep -q '<!-- /notice -->' "$file"; then
    echo "$page has no notice comments under <body>: nothing changed there" >&2
    status=1
    continue
  fi
  NOTICE="$notice" perl -0pi -e '
    my $n = $ENV{NOTICE};
    s{(<!-- notice:[^\n]*-->\n).*?(<!-- /notice -->)}{$1$n$2}s;
  ' "$file"
  if [ -n "$notice" ] && [ "$mac" = yes ]; then
    echo "$page: says $coming is out on iOS and coming to the Mac, which has $current"
  elif [ -n "$notice" ]; then
    echo "$page: says $coming is in review and the App Store has $current"
  else
    echo "$page: no notice"
  fi
done
exit "$status"
