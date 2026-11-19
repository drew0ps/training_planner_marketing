#!/usr/bin/env python3
"""Publishes the blog's posts one at a time.

The posts wait in _drafts/, in the order _drafts/queue.txt gives them. GitHub Pages builds
this site with Jekyll, which publishes no folder whose name starts with an underscore, so
nothing in _drafts/ is on the site (as long as there's no .nojekyll file). Their pictures
and clips are in blog/media/ already, unlinked: _drafts/media is a link to it, so a post's
paths are the same before and after it's published.

Publishing a post moves it to blog/, dates it, and brings everything that lists posts up to
date: the list on blog/index.html, the feed (blog/feed.xml), the sitemap, and the Blog link
in the top bar and the footer of every page. A link from one post to another that isn't out
yet stays plain words until that one is published, and a "Read next" line for it stays hidden.

Usage:
  scripts/publish-post.py                 the next post in the queue, dated today
  scripts/publish-post.py <slug>          that post
  scripts/publish-post.py --date 2026-12-01 [<slug>]
  scripts/publish-post.py --list          the queue: what's out and when, and what's next
  scripts/publish-post.py --refresh       the lists, the feed, the links and the reading times
                                          again, publishing nothing
  scripts/publish-post.py --check         every picture, clip and link of every post is there

Then look at the post (python3 -m http.server 8000, http://localhost:8000/blog/), commit and push.
"""
import datetime
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS = os.path.join(ROOT, "_drafts")
BLOG = os.path.join(ROOT, "blog")
SITE = "https://trainingplanner.pro"
ROOT_PAGES = ["index.html", "press.html", "privacy.html", "support.html"]
# A post's article:section, and its heading on the blog's page, in the order they're listed
SECTIONS = [("Guides", "Using TrainingPlanner"), ("Training", "Training methods"), ("Programs", "Programs")]
SLUG = r"[a-z0-9][a-z0-9-]*"


def read(path):
    with open(path, encoding="utf-8") as file:
        return file.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)


def queue():
    """(slug, planned date) in the order they're published."""
    entries = []
    for line in read(os.path.join(DRAFTS, "queue.txt")).splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            parts = line.split()
            entries.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return entries


def slugs_in(folder):
    if not os.path.isdir(folder):
        return set()
    return {name[:-5] for name in os.listdir(folder) if name.endswith(".html") and name != "index.html"}


def meta_content(text, attribute, name):
    match = re.search(r'<meta %s="%s" content="([^"]*)"' % (attribute, re.escape(name)), text)
    return html.unescape(match.group(1)) if match else ""


def strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def info(slug, folder):
    """What the lists say of a post."""
    text = read(os.path.join(folder, slug + ".html"))
    title = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    image = meta_content(text, "property", "og:image")
    return {
        "slug": slug,
        "title": strip_tags(title.group(1)).strip() if title else slug,
        "description": meta_content(text, "name", "description"),
        "section": meta_content(text, "property", "article:section") or "Training",
        "date": meta_content(text, "property", "article:published_time"),
        # The card shows the cover, a path inside blog/
        "image": image.replace(SITE + "/blog/", "") if image.startswith(SITE + "/blog/") else "",
    }


def long_date(day):
    date = datetime.date.fromisoformat(day)
    return f"{date.day} {date.strftime('%B %Y')}"


def set_date(text, day):
    text = re.sub(r'(<meta property="article:published_time" content=")[^"]*(")', r"\g<1>%s\2" % day, text)
    text = re.sub(r'("datePublished": ")[^"]*(")', r"\g<1>%s\2" % day, text)
    text = re.sub(r'("dateModified": ")[^"]*(")', r"\g<1>%s\2" % day, text)
    return re.sub(r'<time class="published" datetime="[^"]*">[^<]*</time>',
                  f'<time class="published" datetime="{day}">{long_date(day)}</time>', text)


def fix_links(text, here, published, drafts):
    """Links between posts as they can be followed from `here` ("blog" or "drafts")."""
    def target(slug):
        if slug in published:
            return "%s.html" % slug if here == "blog" else "../blog/%s.html" % slug
        if here == "drafts" and slug in drafts:
            return "%s.html" % slug
        return None

    def link(match):
        slug, words = match.group("slug"), match.group("words")
        href = target(slug)
        if href:
            return f'<a href="{href}" data-post="{slug}">{words}</a>'
        return f'<span class="pending" data-post="{slug}">{words}</span>'

    # A link may be wrapped between its attributes, as prose is
    text = re.sub(r'<a\s+href="(?:\.\./blog/)?%s\.html"\s+data-post="(?P<slug>%s)">(?P<words>.*?)</a>' % (SLUG, SLUG), link,
                  text, flags=re.S)
    text = re.sub(r'<span class="pending" data-post="(?P<slug>%s)">(?P<words>.*?)</span>' % SLUG, link, text, flags=re.S)

    def needs(match):
        tag, attributes, slug = match.group(1), match.group(2), match.group(3)
        hidden = "" if target(slug) else " hidden"
        return f'<{tag}{attributes} data-needs="{slug}"{hidden}>'

    text = re.sub(r'<(\w+)([^>]*?) data-needs="(%s)"(?: hidden)?>' % SLUG, needs, text)

    def read_next(match):
        # The heading goes too when there's nothing left to read next
        empty = not re.search(r'<li[^>]* data-needs="%s">' % SLUG, match.group(0))
        return re.sub(r'^<nav class="read-next"( hidden)?', '<nav class="read-next" hidden' if empty else '<nav class="read-next"',
                      match.group(0))

    return re.sub(r'<nav class="read-next".*?</nav>', read_next, text, flags=re.S)


def set_minutes(text):
    """The reading time, from the words of the post's article."""
    article = re.search(r"<article.*?</article>", text, re.S)
    if not article:
        return text
    words = len(re.findall(r"\w+", strip_tags(re.sub(r"<(script|style|table)[\s\S]*?</\1>", " ", article.group(0)))))
    minutes = max(1, round(words / 220))
    return re.sub(r'<span class="minutes">[^<]*</span>', f'<span class="minutes">{minutes} min read</span>', text)


def between(text, name, content):
    """What stands between <!-- name --> and <!-- /name -->, every time they appear."""
    pattern = r"(<!-- %s -->).*?(<!-- /%s -->)" % (re.escape(name), re.escape(name))
    return re.sub(pattern, lambda match: match.group(1) + content + match.group(2), text, flags=re.S)


def card(post):
    image = (f'<img src="{html.escape(post["image"])}" width="1200" height="630" loading="lazy" alt="">'
             if post["image"] else "")
    return (f'\n      <li class="post-card"><a href="{post["slug"]}.html">{image}'
            f'<div class="card-body"><h3>{html.escape(post["title"], quote=False)}</h3>'
            f'<p>{html.escape(post["description"], quote=False)}</p>'
            f'<span class="meta">{long_date(post["date"])}</span></div></a></li>')


def render_index(posts):
    sections = []
    for key, heading in SECTIONS:
        chosen = sorted((p for p in posts if p["section"] == key), key=lambda p: p["date"], reverse=True)
        if not chosen:
            continue
        cards = "".join(card(post) for post in chosen)
        sections.append(f'\n  <section aria-labelledby="list-{key.lower()}">\n    <h2 id="list-{key.lower()}">{heading}</h2>'
                        f'\n    <ul class="post-cards">{cards}\n    </ul>\n  </section>')
    if not sections:
        return '\n  <p class="muted">The first post is on its way.</p>\n  '
    return "".join(sections) + "\n  "


def render_feed(posts):
    newest = sorted(posts, key=lambda p: p["date"], reverse=True)
    updated = newest[0]["date"] if newest else datetime.date.today().isoformat()
    entries = "".join(
        f"""
  <entry>
    <title>{html.escape(p["title"], quote=False)}</title>
    <link href="{SITE}/blog/{p["slug"]}.html"/>
    <id>{SITE}/blog/{p["slug"]}.html</id>
    <published>{p["date"]}T08:00:00Z</published>
    <updated>{p["date"]}T08:00:00Z</updated>
    <summary>{html.escape(p["description"], quote=False)}</summary>
    <category term="{p["section"]}"/>
  </entry>""" for p in newest)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>TrainingPlanner blog</title>
  <subtitle>Training methods and programs, and how to set them up in TrainingPlanner.</subtitle>
  <link href="{SITE}/blog/"/>
  <link rel="self" href="{SITE}/blog/feed.xml"/>
  <id>{SITE}/blog/</id>
  <updated>{updated}T08:00:00Z</updated>
  <author><name>Adam Marton</name></author>{entries}
</feed>
"""


def render_sitemap(posts):
    if not posts:
        return "\n  "
    newest = max(p["date"] for p in posts)
    lines = [f"\n  <url>\n    <loc>{SITE}/blog/</loc>\n    <lastmod>{newest}</lastmod>\n  </url>"]
    for p in sorted(posts, key=lambda p: p["date"]):
        lines.append(f"\n  <url>\n    <loc>{SITE}/blog/{p['slug']}.html</loc>\n    <lastmod>{p['date']}</lastmod>\n  </url>")
    return "".join(lines) + "\n  "


def refresh():
    published, drafts = slugs_in(BLOG), slugs_in(DRAFTS)
    for folder, here, slugs in ((BLOG, "blog", published), (DRAFTS, "drafts", drafts)):
        for slug in slugs:
            path = os.path.join(folder, slug + ".html")
            text = read(path)
            fixed = set_minutes(fix_links(text, here, published, drafts))
            if fixed != text:
                write(path, fixed)
    posts = [info(slug, BLOG) for slug in published]
    index = os.path.join(BLOG, "index.html")
    write(index, between(read(index), "posts", render_index(posts)))
    write(os.path.join(BLOG, "feed.xml"), render_feed(posts))
    sitemap = os.path.join(ROOT, "sitemap.xml")
    write(sitemap, between(read(sitemap), "blog", render_sitemap(posts)))
    # The Blog link, once there is something to read
    for page in ROOT_PAGES:
        path = os.path.join(ROOT, page)
        if os.path.exists(path):
            write(path, between(read(path), "blog-link", '<a href="blog/">Blog</a>' if posts else ""))
    return posts


def publish(slug, day):
    source = os.path.join(DRAFTS, slug + ".html")
    if not os.path.exists(source):
        sys.exit(f"No draft {slug}: _drafts/{slug}.html isn't there" + (" (it's published)" if slug in slugs_in(BLOG) else ""))
    text = set_date(read(source), day)
    write(os.path.join(BLOG, slug + ".html"), text)
    os.remove(source)
    posts = refresh()
    print(f"Published {slug} on {long_date(day)}: blog/{slug}.html. {len(posts)} posts out.")
    left = [s for s, _ in queue() if s in slugs_in(DRAFTS)]
    print(f"Next in the queue: {left[0]}" if left else "The queue is empty.")
    missing = check(only=[os.path.join(BLOG, slug + ".html")])
    if missing:
        print("Missing from the post:\n  " + "\n  ".join(missing))


def check(only=None):
    """Pictures, clips and links of the posts that aren't there."""
    paths = only or [os.path.join(folder, name) for folder in (BLOG, DRAFTS) if os.path.isdir(folder)
                     for name in sorted(os.listdir(folder)) if name.endswith(".html")]
    missing = []
    for path in paths:
        text = read(path)
        for reference in re.findall(r'(?:src|poster|href)="([^"#?]+)', text):
            if re.match(r"^(https?:|mailto:|data:)", reference) or reference.endswith("/"):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), reference))
            if not os.path.exists(target):
                missing.append(f"{os.path.relpath(path, ROOT)}: {reference}")
    return missing


def main():
    arguments = sys.argv[1:]
    day = datetime.date.today().isoformat()
    if "--date" in arguments:
        index = arguments.index("--date")
        day = arguments[index + 1]
        datetime.date.fromisoformat(day)
        del arguments[index:index + 2]
    if arguments[:1] == ["--help"] or arguments[:1] == ["-h"]:
        print(__doc__)
    elif arguments[:1] == ["--list"]:
        out = slugs_in(BLOG)
        for slug, planned in queue():
            if slug in out:
                print(f"out       {info(slug, BLOG)['date']}  {slug}")
            elif slug in slugs_in(DRAFTS):
                print(f"waiting   {planned or '          '}  {slug}")
            else:
                print(f"missing   {planned or '          '}  {slug} (no draft)")
    elif arguments[:1] == ["--refresh"]:
        print(f"{len(refresh())} posts out; lists, feed, sitemap and links brought up to date.")
    elif arguments[:1] == ["--check"]:
        missing = check()
        print("\n".join(missing) if missing else "Every picture, clip and link is there.")
        sys.exit(1 if missing else 0)
    elif arguments:
        publish(arguments[0], day)
    else:
        waiting = [slug for slug, _ in queue() if slug in slugs_in(DRAFTS)]
        if not waiting:
            sys.exit("Nothing waiting in _drafts/queue.txt.")
        publish(waiting[0], day)


if __name__ == "__main__":
    main()
