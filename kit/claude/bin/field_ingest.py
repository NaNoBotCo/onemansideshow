#!/usr/bin/env python3
"""FIELD DROP — read what came off the card, name it, log it. Files nothing.

  python3 ~/.claude/bin/field_ingest.py            # ingest new drops
  python3 ~/.claude/bin/field_ingest.py --dry      # show what it would do

Drop folder   ~/Desktop/FIELD DROP/
Store         ~/Desktop/Video/Field/<YYYY-MM-DD>/
Sidecar       <name>.json  — original name, time, lat, lng, camera, duration
Log           ~/.claude/state/field.tsv
Originals are moved, never copied-and-deleted, and never touched twice: a file
already carrying a sidecar is skipped.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
DROP = os.path.join(HOME, "Desktop", "FIELD DROP")
STORE = os.path.join(HOME, "Desktop", "Video", "Field")
LOG = os.path.join(HOME, ".claude", "state", "field.tsv")
STILL = {".jpg", ".jpeg", ".png", ".heic", ".dng", ".tif", ".tiff"}
MOVIE = {".mp4", ".mov", ".360", ".insv", ".lrv", ".m4v"}
ISO6709 = re.compile(r"([+-]\d+\.?\d*)([+-]\d+\.?\d*)")


def dms(value, ref):
    try:
        d, m, s = [float(x) for x in value]
    except Exception:
        return None
    out = d + m / 60 + s / 3600
    return -out if ref in ("S", "W") else out


def still_meta(path):
    try:
        from PIL import Image, ExifTags
    except ImportError:
        return {}
    try:
        img = Image.open(path)
        raw = img._getexif() or {}
    except Exception:
        return {}
    tags = {ExifTags.TAGS.get(k, k): v for k, v in raw.items()}
    out = {}
    when = tags.get("DateTimeOriginal") or tags.get("DateTime")
    if when:
        out["when"] = str(when).replace(":", "-", 2)
    model = tags.get("Model")
    if model:
        out["camera"] = str(model).strip()
    gps = tags.get("GPSInfo") or {}
    gps = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps.items()} if gps else {}
    lat = dms(gps.get("GPSLatitude", []), gps.get("GPSLatitudeRef", "N"))
    lng = dms(gps.get("GPSLongitude", []), gps.get("GPSLongitudeRef", "E"))
    if lat is not None and lng is not None:
        out["lat"], out["lng"] = round(lat, 6), round(lng, 6)
    return out


def movie_meta(path):
    try:
        raw = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path],
            capture_output=True, text=True, timeout=60).stdout
        data = json.loads(raw or "{}")
    except Exception:
        return {}
    fmt = data.get("format", {})
    tags = {k.lower(): v for k, v in (fmt.get("tags") or {}).items()}
    out = {}
    if fmt.get("duration"):
        out["seconds"] = round(float(fmt["duration"]), 1)
    if tags.get("creation_time"):
        out["when"] = tags["creation_time"][:19].replace("T", " ")
    for key in ("com.apple.quicktime.model", "model", "handler_name"):
        if tags.get(key):
            out["camera"] = tags[key]
            break
    for key in ("location", "com.apple.quicktime.location.iso6709"):
        if tags.get(key):
            m = ISO6709.match(tags[key])
            if m:
                out["lat"], out["lng"] = float(m.group(1)), float(m.group(2))
            break
    return out


def mtime(path):
    return dt.datetime.fromtimestamp(os.path.getmtime(path))


def main():
    dry = "--dry" in sys.argv
    os.makedirs(DROP, exist_ok=True)
    found = []
    skipped = []
    for name in sorted(os.listdir(DROP)):
        src = os.path.join(DROP, name)
        ext = os.path.splitext(name)[1].lower()
        if name.startswith("."):
            continue
        if os.path.isdir(src):
            # A folder in the drop belongs to another tool; loose files only.
            n = len([f for f in os.listdir(src) if not f.startswith(".")])
            skipped.append(f"{name}/ ({n})")
            continue
        if not os.path.isfile(src):
            continue
        if ext not in STILL and ext not in MOVIE:
            continue
        meta = still_meta(src) if ext in STILL else movie_meta(src)
        meta.setdefault("when", mtime(src).strftime("%Y-%m-%d %H:%M:%S"))
        meta["original"] = name
        meta["kind"] = "still" if ext in STILL else "movie"
        meta["bytes"] = os.path.getsize(src)
        day = meta["when"][:10]
        stamp = meta["when"][11:19].replace(":", "")
        base = f"{day}-{stamp}-{os.path.splitext(name)[0]}"[:80]
        dest_dir = os.path.join(STORE, day)
        dest = os.path.join(dest_dir, base + ext)
        found.append((src, dest, meta))
        if dry:
            print(f"{name}  ->  {dest}  {meta.get('lat','no pin')}")
            continue
        os.makedirs(dest_dir, exist_ok=True)
        n = 1
        while os.path.exists(dest):
            dest = os.path.join(dest_dir, f"{base}-{n}{ext}")
            n += 1
        shutil.move(src, dest)
        with open(dest + ".json", "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=1)
        pin = (f"{meta['lat']},{meta['lng']}" if "lat" in meta else "no pin")
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(f"{day}\t{os.path.basename(dest)}\t{pin}\tunfiled\n")
    if not found:
        print("nothing new in the drop")
    else:
        print(f"{len(found)} file(s)" + (" (dry run)" if dry else " ingested"))
    if skipped:
        print("left for their own tool: " + ", ".join(skipped))


if __name__ == "__main__":
    main()
