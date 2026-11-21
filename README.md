# TrainingPlanner marketing site

A static site for TrainingPlanner, the progressive overload planner for iPhone, iPad, Mac and Apple Watch:
the home page, the press kit, the privacy and support pages, and a blog. No build step and no dependencies:
HTML, `styles.css` and the images, with a few scripts that rewrite them.

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
| `blog/` | The blog: `index.html` lists the published posts, `feed.xml` is their Atom feed, each post is `<slug>.html`, and `media/` has every post's pictures, clips and covers. |
| `_drafts/` | Posts waiting to be published, in the order of `_drafts/queue.txt`. Not on the site (see Blog below). `_drafts/media` is a link to `blog/media`. |
| `scripts/publish-post.py` | Publishes the next post in the queue and brings the blog's list, feed, sitemap and links up to date. |
| `dietapp/` | DietApp Pro's page, trainingplanner.pro/dietapp/: the developer's other app, on this site's stylesheet with `dietapp.css` for its own mark. See DietApp Pro below. |
| `scripts/update-blog-media.py` | Makes the pictures and clips the posts use from the app repository's captures. |
| `scripts/update-program-posts.py` | Writes the program posts' tables from the programs the app exports. |
| `scripts/make-covers.swift` | Draws each post's cover, the picture its link shows. |
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
  four pages and, between its `blog` comments, the blog and its published posts (`scripts/publish-post.py`
  writes those). Update a page's `lastmod` when its copy changes.
- **Smart App Banner:** the `apple-itunes-app` meta tag makes Safari on iPhone and iPad offer the
  app at the top of the page.
- **Prices:** shown in CHF, as set in App Store Connect; the App Store shows each storefront's own.

## Blog

The blog explains the training methods TrainingPlanner supports (progression, periodization, effort, volume,
deloads, readiness and the set types) with how to set each one up on iPhone, iPad and Mac, and has a post for
every built-in program. Guides (a quick start with a simple Push · Legs · Pull, coaching between a trainer and a
client) are listed first, under Using TrainingPlanner. A post's section is its `article:section`: `Guides`,
`Training` or `Programs`. The posts are published one at a time, from a queue.

- **Drafts:** every post waits in `_drafts/<slug>.html`, a complete page. GitHub Pages builds this site with
  Jekyll, which leaves out every folder whose name starts with `_`, so drafts are not on the site; they stay out
  only as long as there is no `.nojekyll` file. Their pictures and clips are in `blog/media/` already, on the
  site but linked from nowhere: `_drafts/media` links to it, so a post's paths are the same before and after it
  is published. Look at a draft with the local preview below, at `/_drafts/<slug>.html`.
- **Publishing:** `scripts/publish-post.py` publishes the first post of `_drafts/queue.txt` that's still a
  draft (or `scripts/publish-post.py <slug>`): it moves it to `blog/`, dates it today (`--date 2026-12-01` for
  another day), and rewrites the list on `blog/index.html` (between its `posts` comments), `blog/feed.xml`, the
  blog's part of `sitemap.xml`, and the Blog link in the top bar and footer of the home, press, privacy and
  support pages (between their `blog-link` comments, empty until the first post is out). Then commit and push.
  `--list` shows the queue, `--refresh` rewrites the lists and links without publishing, and `--check` lists any
  picture, clip or link a post names that isn't there. The dates in `queue.txt` are the plan (Mondays and
  Thursdays); nothing is published by itself.
- **Links between posts** are written `<a href="<slug>.html" data-post="<slug>">`. While the post they lead to
  isn't out, the publishing script turns them into plain words (`<span class="pending">`) and hides the "Read
  next" lines for it (`data-needs`); publishing that post turns them back into links everywhere.
- **Pictures and clips:** the app is filmed and photographed for the blog in the app repository:
  `Branding/capture-blog.sh` (iPhone, iPad, every program, the Mac) writes `Branding/Blog`. A post names each
  picture by where it goes under `blog/media` (`media/iphone/periodization-chosen.jpg`,
  `media/clips/ipad/pyramid.mp4`, `media/programs/fiveByFive/mac-board.jpg`), and
  `scripts/update-blog-media.py` makes exactly those from the captures, sized for the page, with a still for
  each clip, and removes what no post uses any more. The home page counts as a post there: what it shows from
  `blog/media` is made and kept too. Look at frames of the clips before pushing, as for the home page's.
- **Program tables:** each program post names its program (`<meta name="tp:program" content="fiveByFive">`) and
  marks where its tables go (`<!-- program-sessions -->` and the like). `scripts/update-program-posts.py` writes
  them from `Branding/Blog/programs.json`, which the app exports (`Branding/capture-blog.sh data`), so the sets,
  phases and weeks shown are the app's own. Run it again when the programs change. The quick start's plan is in
  the same file as `simplePushLegsPull`, though it isn't one of the app's templates.
- **Covers:** `swift scripts/make-covers.swift` draws `blog/media/covers/<slug>.jpg` for every post, with its
  title and the first phone screen it shows, or the one its `<meta name="tp:cover-screen">` names; run it after
  `update-blog-media.py` and after changing a title.
- **A new post:** copy a draft, change its slug, words and pictures, add it to `queue.txt`, then run the media
  script and the covers.
- **On the home page:** "From the blog" (`#from-the-blog` in `index.html`) shows three published posts on the
  blog's cards, chosen by hand and written there, not by the publishing script: the quick start, progressive
  overload and double progression since November 21, 2026. Change a card when its post's title or cover
  changes, and link only posts that are out. "How it works" links the last two in its third step.
- **The AI coach on the home page** (`#coach` in `index.html`, since November 21, 2026) shows the coach tour's
  pictures, `media/iphone/coach-tip.jpg` and `coach-eased.jpg`, each laid over a framed phone (`.phone
  .screen`): bench press at 100 kg for 9 with nothing left in reserve, the next set started 5 % lighter, and the
  coach's tip for it. The tip is Apple Intelligence's own answer, so the tour (`BlogTours.testCoachInWorkout`)
  needs a simulator that has it, on a Mac with Apple Intelligence turned on, and its words differ from run to
  run: retake it with `ONLY=testCoachInWorkout Branding/capture-blog.sh iphone`, read the tip, then run the media
  script and put the tip's words in the picture's `alt`.

## DietApp Pro

`dietapp/` is DietApp Pro's page (the app repository is `../ios_diet_app`). It was the
`ios_diet_app_marketing` site, which had no remote, and moved here on November 20, 2026.

- **Not on the App Store yet:** the buttons say "Coming soon" (`<span class="btn btn-ghost soon">`) and
  lead nowhere. Once the listing is live, make each one a link to its App Store URL
  (`<a class="btn btn-primary" href="…">Download on the App Store</a>`, "Get the app" in the top bar),
  add `installUrl` to the JSON-LD, and change "Coming soon to the App Store, free to start" in the closing
  section. TrainingPlanner's home page has a panel for it below its closing section (`#dietapp` in
  `index.html`), "Coming soon from the same developer": change that line then too.
- **Copy** follows the App Store listing in `../ios_diet_app/docs/app-store-listing.md`: the feature
  lists, the free allowances (3 AI logs a week, 3 saved meals) and the Pro list. Meal photo logging is off
  in the app since 2.0.8, so the page doesn't offer it; scanning a nutrition label is still there.
- **Pictures:** `make -C Branding all` in the app repository photographs the app and runs
  `dietapp/scripts/update-screenshots.sh` here (`make -C Branding site` only copies): the framed captures
  at 640 px, three of the Apple Watch's as they are (`screenshots/devices/watch-*.png`), the link preview
  from the search-results artwork and the touch icon.
- **Clips:** `make -C Branding clips` there films the app and runs `dietapp/scripts/update-clips.sh`
  here, which needs `ffmpeg` for the stills: the five clips the App Store's two app previews are cut
  from, each with its first frame, in `dietapp/clips/`. The "See it move" section plays them in the order
  of its `data-clip` lines, with the main page's script.
- **Privacy policy and support:** `dietapp/privacy.html` and `dietapp/support.html`, since November 20,
  2026; App Store Connect has them without `.html` (Pages serves both forms): Marketing URL
  `https://trainingplanner.pro/dietapp/`, Privacy Policy URL `https://trainingplanner.pro/dietapp/privacy`,
  Support URL `https://trainingplanner.pro/dietapp/support`, which are also their canonical addresses and
  the sitemap's. They were on `drew0ps.github.io/ios_diet_app_hosted`, whose pages now forward here. The
  policy's words are the app's `DietApp/Resources/PrivacyPolicy.md`: change both together.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>, and <http://localhost:8000/_drafts/progressive-overload.html> for a draft.
