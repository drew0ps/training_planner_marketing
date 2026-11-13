# TrainingPlanner marketing site

A single static page for TrainingPlanner, the progressive overload
planner for iPhone. No build step and no dependencies: `index.html`, `styles.css` and the images.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The page. Copy follows the App Store listing in the app repository's `docs/`. |
| `styles.css` | Styles. Colours come from `Branding/BRAND.md` in the app repository. |
| `screenshots/*.jpg` | The app's dark captures, 780 px wide, shown inside a CSS phone frame. |
| `og-image.png` | The link preview image, from the App Store search-results artwork. |
| `favicon.svg`, `apple-touch-icon.png` | The mark and the app icon. |
| `scripts/update-screenshots.sh` | Regenerates every image above from the app repository. |

## Updating

- **Screenshots:** retake the dark captures in the app repository (the `AppStoreScreenshots` UI test),
  then run `scripts/update-screenshots.sh`. It expects the app repository next to this one as
  `../Training Planner`; pass another path as the first argument otherwise.
- **App Store link:** the download buttons and the JSON-LD block point at
  <https://apps.apple.com/us/app/trainingplanner-pro/id6824840650>.
- **Link preview:** `og:image` is a relative path. Once the site has its final domain, make it an
  absolute URL so Messages, Slack and social networks can fetch it.
- **Prices:** shown in CHF, as set in App Store Connect; the App Store shows each storefront's own.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>.
