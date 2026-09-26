#!/usr/bin/env python3
"""Short, browser-pasteable links for files with long names.

Paths pasted into a browser often carry em-dashes, brackets and
commas, so a file:// URL of the real path becomes hundreds of characters of
percent-encoding — unreadable. This keeps an all-ASCII symlink farm at
~/Desktop/go/ whose file:// URLs need no encoding at all.

Symlinks, never copies: editing through one edits the real file; deleting one
deletes only the shortcut.

    python3 engine/shortlink.py add <path> [short-name]
    python3 engine/shortlink.py list
    python3 engine/shortlink.py prune
"""
import sys, os, re, pathlib

GO = pathlib.Path.home() / "Desktop" / "go"
BASE = GO.as_uri() + "/"
RESERVED = {"README.txt"}


def slug(p):
    name = p.name
    # drop leading "3 — " style ordinals and any bracketed tail
    name = re.sub(r'^[0-9]+[a-z]?\s*[—–-]\s*', '', name)
    name = re.sub(r'\([^)]*\)', ' ', name)
    stem, ext = (name.rsplit('.', 1) + [''])[:2] if '.' in name else (name, '')
    stem = re.sub(r'[^A-Za-z0-9]+', '-', stem).strip('-').lower()
    stem = '-'.join(stem.split('-')[:4])[:32].strip('-') or "item"
    return f"{stem}.{ext.lower()}" if ext else stem


def url(name):
    return BASE + name


def add(target, name=None):
    # Absolute: a relative symlink resolves only from where it was made.
    t = pathlib.Path(target).expanduser().resolve()
    if not t.exists():
        sys.exit(f"nothing at: {t}")
    GO.mkdir(parents=True, exist_ok=True)
    n = name or slug(t)
    if n in RESERVED:
        n = "x-" + n
    link = GO / n
    # A dead link is a name whose target moved. Reclaim it rather than number
    # around it, so the name already in use keeps working.
    if link.is_symlink() and not os.path.exists(os.path.realpath(link)):
        link.unlink()
    # if the name is taken by a DIFFERENT, LIVE target, number it
    if link.exists() or link.is_symlink():
        if os.path.realpath(link) != os.path.realpath(t):
            stem, dot, ext = n.partition('.')
            k = 2
            while True:
                cand = GO / f"{stem}-{k}{dot}{ext}"
                if not (cand.exists() or cand.is_symlink()) or \
                   os.path.realpath(cand) == os.path.realpath(t):
                    link, n = cand, cand.name
                    break
                k += 1
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(t)
    return url(n)


def listing():
    if not GO.is_dir():
        print("no ~/Desktop/go yet")
        return
    rows = []
    for e in sorted(GO.iterdir()):
        if e.name.startswith('.'):
            continue
        real = os.path.realpath(e)
        ok = os.path.exists(real)
        rows.append((ok, e.name, real))
    w = max((len(n) for _, n, _ in rows), default=4)
    for ok, n, real in rows:
        print(f"  {'OK ' if ok else 'DEAD'}  {url(n):<{w+len(BASE)}}  ->  {real}")
    dead = sum(1 for ok, _, _ in rows if not ok)
    print(f"\n  {len(rows)} link(s), {dead} dead")


def prune():
    removed = 0
    for e in sorted(GO.iterdir()):
        if e.is_symlink() and not os.path.exists(os.path.realpath(e)):
            e.unlink()
            removed += 1
            print("  removed dead link:", e.name)
    print(f"  {removed} removed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "add":
        print(add(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
    elif cmd == "list":
        listing()
    elif cmd == "prune":
        prune()
    else:
        sys.exit(__doc__)
