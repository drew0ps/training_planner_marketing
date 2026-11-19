#!/usr/bin/env python3
"""Brings the blog's pictures and clips in from the app repository: the ones the posts use.

The app is filmed and photographed for the blog in the app repository: Branding/capture-blog.sh
writes Branding/Blog. A post names each picture and clip by where it goes under blog/media,
and this makes it from its capture, sized for the page:

  media/iphone/<topic>-<what>.jpg            Branding/Blog/iPhone/<topic>-<nn>-<what>.png, 720 px wide
  media/ipad/<topic>-<what>.jpg              Branding/Blog/iPad/<topic>-<nn>-<what>.png, 1600 px wide
  media/mac/<name>.png                       Branding/Blog/Mac/<name>.png, 1600 px wide
  media/clips/<iphone|ipad>/<topic>.mp4      Branding/Blog/Clips/<iPhone|iPad>/<topic>.mp4
  media/clips/<iphone|ipad>/<topic>.jpg      that clip's first frame, shown until it plays
  media/programs/<id>/<device>-<screen>.jpg  Branding/Blog/Programs/<iPhone|iPad|Mac>/<id>-<screen>.png

The number in a capture's name (its place in the tour) is left out of the post's, so a tour
that takes one more picture doesn't move the others. The covers (media/covers) are
scripts/make-covers.swift's. A file no post uses any more is removed; a capture that's
missing is reported. Needs ffmpeg for the stills (brew install ffmpeg).

Usage: scripts/update-blog-media.py [path to the app repository, default ../Training Planner] [--force]
"""
import glob
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
arguments = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
APP = arguments[0] if arguments else os.path.join(ROOT, "..", "Training Planner")
CAPTURES = os.path.join(APP, "Branding", "Blog")
MEDIA = os.path.join(ROOT, "blog", "media")
DEVICES = {"iphone": "iPhone", "ipad": "iPad", "mac": "Mac"}
WIDTHS = {"iphone": 720, "ipad": 1600, "mac": 1600}


def references():
    found = set()
    for folder in ("_drafts", "blog"):
        for path in glob.glob(os.path.join(ROOT, folder, "*.html")):
            text = open(path, encoding="utf-8").read()
            found.update(re.findall(r"media/([A-Za-z0-9_./-]+\.(?:jpg|png|mp4))", text))
    return found


def capture(folder, name):
    """The capture called <name>.png in <folder>, or <topic>-<nn>-<what>.png for <topic>-<what>."""
    exact = os.path.join(folder, name + ".png")
    if os.path.exists(exact):
        return exact
    topic, _, what = name.partition("-")
    while what:
        matches = glob.glob(os.path.join(folder, f"{topic}-[0-9][0-9]-{what}.png"))
        if matches:
            return sorted(matches)[-1]
        # Topics with a dash in their name: rest-pause-02-mini-set
        head, _, what = what.partition("-")
        topic = f"{topic}-{head}"
    return None


def source(reference):
    """The capture a media file is made from, and how: ("picture", path, width) or ("clip", path)."""
    parts = reference.split("/")
    stem = os.path.splitext(parts[-1])[0]
    if parts[0] in DEVICES and len(parts) == 2:
        return "picture", capture(os.path.join(CAPTURES, DEVICES[parts[0]]), stem), WIDTHS[parts[0]]
    if parts[0] == "clips" and len(parts) == 3 and parts[1] in DEVICES:
        clip = os.path.join(CAPTURES, "Clips", DEVICES[parts[1]], stem + ".mp4")
        return ("clip" if reference.endswith(".mp4") else "still"), (clip if os.path.exists(clip) else None), None
    if parts[0] == "programs" and len(parts) == 3:
        device, _, screen = stem.partition("-")
        if device in DEVICES:
            path = os.path.join(CAPTURES, "Programs", DEVICES[device], f"{parts[1]}-{screen}.png")
            return "picture", (path if os.path.exists(path) else None), WIDTHS[device]
    return None, None, None


def stale(target, origin):
    return FORCE or not os.path.exists(target) or os.path.getmtime(target) < os.path.getmtime(origin)


def make_picture(origin, target, width):
    fmt = ["-s", "format", "jpeg", "-s", "formatOptions", "80"] if target.endswith(".jpg") else ["-s", "format", "png"]
    subprocess.run(["sips", "--resampleWidth", str(width), *fmt, origin, "--out", target],
                   check=True, capture_output=True)


def main():
    if not os.path.isdir(CAPTURES):
        sys.exit(f"No captures at {CAPTURES}: run Branding/capture-blog.sh in the app repository first")
    used = references()
    made, missing = 0, []
    for reference in sorted(used):
        if reference.startswith("covers/"):
            continue
        kind, origin, width = source(reference)
        target = os.path.join(MEDIA, reference)
        if not origin:
            missing.append(reference)
            continue
        if not stale(target, origin):
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if kind == "picture":
            make_picture(origin, target, width)
        elif kind == "clip":
            shutil.copyfile(origin, target)
        elif kind == "still":
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", origin, "-frames:v", "1", "-q:v", "3", target], check=True)
        made += 1
    # What no post uses any more
    removed = 0
    for path in glob.glob(os.path.join(MEDIA, "**", "*.*"), recursive=True):
        relative = os.path.relpath(path, MEDIA)
        if not relative.startswith("covers/") and relative not in used:
            os.remove(path)
            removed += 1
    for folder in sorted(glob.glob(os.path.join(MEDIA, "**"), recursive=True), reverse=True):
        if os.path.isdir(folder) and folder != MEDIA and not os.listdir(folder):
            os.rmdir(folder)
    size = sum(os.path.getsize(p) for p in glob.glob(os.path.join(MEDIA, "**", "*.*"), recursive=True))
    print(f"{made} made, {removed} no longer used and removed; blog/media is {size / 1024 / 1024:.1f} MB")
    if missing:
        print(f"{len(missing)} without a capture:\n  " + "\n  ".join(missing))
        sys.exit(1)


if __name__ == "__main__":
    main()
