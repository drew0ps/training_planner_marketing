# TrainingPlanner marketing site

A single static page for TrainingPlanner, the progressive overload
planner for iPhone, iPad, Mac and Apple Watch. No build step and no dependencies: `index.html`, `styles.css` and the images.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The page. Copy follows the App Store listing in the app repository's `docs/`. |
| `styles.css` | Styles. Colours come from `Branding/BRAND.md` in the app repository. |
| `screenshots/*.png` | The app's dark captures on Apple's iPhone chrome, 640 px wide; `devices/` has the iPad, Mac, Watch and Duo. |
| `clips/*.mp4`, `clips/*.jpg` | The app filmed in use, one clip per moment, 720 px wide and silent, each with its first frame as a still. |
| `og-image.png` | The link preview image, from the App Store search-results artwork. |
| `favicon.svg`, `apple-touch-icon.png` | The mark and the app icon. |
| `press.html`, `press/` | The press kit: a fact sheet, texts to quote, pictures and a video, and the same as one zip. `press/fact-sheet.txt` is written by hand. |
| `privacy.html`, `support.html` | The privacy policy and the support page: prose, styled by `.doc` in `styles.css`. |
| `robots.txt`, `sitemap.xml` | For search engines. |
| `scripts/update-press-kit.sh` | Rebuilds `press/` and its zip from the app repository. |
| `scripts/set-campaign.sh` | Puts an App Store Connect campaign on the App Store links. |
| `scripts/set-notice.sh` | Puts the "in review" notice on top of the home and press pages, and takes it off on release day. |
| `scripts/update-screenshots.sh` | Regenerates every image above from the app repository. |
| `scripts/update-clips.sh` | Copies the clips from the app repository and makes their stills. |

## Updating

- **Screenshots:** in the app repository, `make -C Branding all` photographs every device from the
  app, frames the pictures and runs `scripts/update-screenshots.sh` here (`make -C Branding site`
  for the copy alone). The script expects the app repository next to this one as
  `../Training Planner`; pass another path as the first argument otherwise.
- **Clips:** in the app repository, `make -C Branding clips` films the app and runs
  `scripts/update-clips.sh` here, which needs `ffmpeg` for the stills. The "See it move" section of
  `index.html` names each clip (`data-clip`) with a line about it and plays them on one phone, laid
  over the display of a framed screenshot: a new clip needs a line there, and the script says so when
  the page names a clip that is no longer filmed.
- **Press kit:** `scripts/update-press-kit.sh` copies the icon, the device picture, six App Store
  screenshots and the App Store's app preview video into `press/` and zips them with the fact sheet.
  Facts change in three places together: `press.html`, `press/fact-sheet.txt` and the App Store
  listing. The download button in `press.html` says the zip's size.
- **Privacy policy:** the words of `privacy.html` are also in the app, at
  `Training Planner/Resources/PrivacyPolicy.md` in the app repository. Change both together, with a
  new "Effective" date when the meaning changes. The pages in the `Training_Planner_Privacy`
  repository (`drew0ps.github.io/Training_Planner_Privacy/`), where the policy and the support page
  were until November 18, 2026, only forward here. They have to stay: an older Mac build's Help menu
  and older App Store descriptions link to them.
- **A version in review:** the home and press pages describe the version that is coming, so while it
  waits in App Review a line on top of both says so:
  `scripts/set-notice.sh 2.4 2.3 "the Apple Watch, iPad and Mac apps, readiness and medals"` (the
  version in review, the one on the App Store, and what arrives with it). **On release day:**
  `scripts/set-notice.sh --clear`, then commit and push. It only rewrites what stands between the two
  `notice` comments under `<body>`.
- **Campaigns:** `scripts/set-campaign.sh <provider token> [campaign]` adds the campaign to the
  download links of every page and the Smart App Banner of the home page, so App Analytics counts
  the installs that start here; `--clear` takes it off. The token comes from Generate Campaign Link in App Analytics.
- **App Store link:** the download buttons and the JSON-LD block point at
  <https://apps.apple.com/us/app/trainingplanner-pro/id6824840650>.
- **Link preview:** `og:image`, `og:url` and the canonical link are absolute URLs on
  `https://trainingplanner.pro/`; change them together if the domain ever changes.
- **Search engines:** `robots.txt` allows everything and points at `sitemap.xml`, which lists the
  four pages. Update a page's `lastmod` when its copy changes.
- **Smart App Banner:** the `apple-itunes-app` meta tag makes Safari on iPhone and iPad offer the
  app at the top of the page.
- **Prices:** shown in CHF, as set in App Store Connect; the App Store shows each storefront's own.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>.
