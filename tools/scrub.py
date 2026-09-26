#!/usr/bin/env python3
"""Gate: fail on a term from the private scrub list.

    python3 tools/scrub.py [terms-file]

A plain line in the list applies to the whole repo; a line starting 'kit:' applies
to kit/ and tools/ only. docs/ and the README name the maker on purpose. The list lives outside this
repo (default ../onemansideshow-private/scrub-terms.txt) so the names it guards are not
published with it.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERMS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "onemansideshow-private" / "scrub-terms.txt"
SKIP = {".git"}

if not TERMS.exists():
    sys.exit(f"scrub: no term list at {TERMS}")
everywhere, kit = [], []
for line in TERMS.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("kit:"):
        kit.append(re.compile(line[4:], re.I))
    else:
        everywhere.append(re.compile(line, re.I))

hits = 0
for f in sorted(ROOT.rglob("*")):
    if not f.is_file() or any(p in SKIP for p in f.parts):
        continue
    rel = f.relative_to(ROOT)
    pats = everywhere + kit if rel.parts[0] in ("kit", "tools") else everywhere
    for pat in pats:
        if pat.search(f.name):
            print(f"{rel}  NAME  {pat.pattern}")
            hits += 1
    try:
        text = f.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        for pat in pats:
            if pat.search(line):
                print(f"{rel}:{n}  {pat.pattern}  {line.strip()[:90]}")
                hits += 1
print(f"\n{hits} hit(s)" if hits else "scrub clean")
sys.exit(1 if hits else 0)
