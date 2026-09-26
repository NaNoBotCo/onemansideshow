#!/usr/bin/env python3
"""stylecheck — the machine-checkable half of ~/.claude/STYLE.md.
Rules live in ~/.claude/style-rules.txt.

    python3 ~/.claude/bin/stylecheck.py <path>...   files, or a directory to walk
    python3 ~/.claude/bin/stylecheck.py --stdin     a draft on stdin
    python3 ~/.claude/bin/stylecheck.py --quotes    also report inside quoted text

Exit 1 on a hit, so a build or a hook can gate on it.

Three things it deliberately lets through:
  · a hit inside quotation marks — a sourced quote keeps its absolutes
  · Title Case — a book or place name
  · fenced code blocks, and a line carrying `stylecheck: allow`; a region between
    `stylecheck: allow-start` and `stylecheck: allow-end`, for a file that names the words
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

I = re.I          # case-insensitive
X = 0             # case matters

RULES_FILE = Path.home() / ".claude" / "style-rules.txt"
KINDS = {"WORD", "ASSURANCE", "THROAT"}


def load_rules(path: Path = RULES_FILE) -> list:
    """style-rules.txt: one rule a line, KIND<tab>regex<tab>why; '#' starts a comment.
    A regex is case-insensitive unless the line's KIND ends in '!' (WORD!)."""
    groups: dict[str, list] = {k: [] for k in KINDS}
    if not path.exists():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        kind, pat = parts[0].strip(), parts[1]
        why = parts[2].strip() if len(parts) > 2 else pat
        flags = 0 if kind.endswith("!") else re.I
        kind = kind.rstrip("!").upper()
        if kind in groups:
            groups[kind].append((pat, flags, why))
    return [(groups[k], k) for k in ("WORD", "ASSURANCE", "THROAT") if groups[k]]


RULES = load_rules()

SKIP_DIR = {".git", "node_modules", "__pycache__", "build", "docs", "dist", ".venv", "venv", "_cache", ".cache", "vendor", "fixtures"}
TEXTY = {".md", ".txt", ".html", ".json", ".py", ".js", ".css", ".yml", ".yaml", ".cff", ".xml"}

# A quotation is a mark paired with its own kind.
QUOTE_PAIRS = [("\u201c", "\u201d"), ("\u2018", "\u2019"), ("\u00ab", "\u00bb"), ('"', '"'), ("'", "'")]
QUOTED = [re.compile(re.escape(a) + r".{0,1000}?" + re.escape(b)) for a, b in QUOTE_PAIRS]
# In code, straight quotes mark string literals (reader copy), so only
# typographic quotes mark a quotation there.
CODE = {".py", ".js", ".mjs", ".ts", ".json", ".html", ".xml", ".css"}
QUOTED_CODE = QUOTED[:3]

APOSTROPHE = re.compile(r"(?<=\w)['’](?=\w)")
ALLOW = re.compile(r"stylecheck:\s*allow\b(?!-)", re.I)
BLOCK_ON = re.compile(r"stylecheck:\s*allow-start", re.I)
BLOCK_OFF = re.compile(r"stylecheck:\s*allow-end", re.I)
FENCE = re.compile(r"^\s*(```|~~~)")
TITLE = re.compile(r"^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$")


def scan(text: str, where: str, quotes: bool, code: bool = False) -> list[str]:
    out = []
    off, fenced = False, False
    for n, line in enumerate(text.splitlines(), 1):
        if BLOCK_ON.search(line):
            off = True
            continue
        if BLOCK_OFF.search(line):
            off = False
            continue
        if FENCE.match(line):
            fenced = not fenced
            continue
        if off or fenced or ALLOW.search(line):
            continue
        # An apostrophe inside a word is not a quotation mark.
        masked = APOSTROPHE.sub("\x00", line)
        spans = [] if quotes else [m.span() for p in (QUOTED_CODE if code else QUOTED) for m in p.finditer(masked)]
        for rules, kind in RULES:
            for pat, flags, why in rules:
                for m in re.finditer(pat, line, flags):
                    hit = m.group(0)
                    if TITLE.match(hit):
                        continue                                    # a title, not a claim
                    if any(a <= m.start() < b for a, b in spans):
                        continue                                    # someone else said it
                    out.append(f"{where}:{n}  {kind}  {hit!r} — {why}")
    return out


def files(args: list[str]):
    for a in args:
        p = Path(a)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix in TEXTY and not any(d in f.parts for d in SKIP_DIR):
                    yield f
        elif p.is_file():
            yield p


def main(argv: list[str]) -> int:
    quotes = "--quotes" in argv
    argv = [a for a in argv if a != "--quotes"]
    hits = []
    if "--stdin" in argv:
        hits = scan(sys.stdin.read(), "-", quotes)
    elif not argv:
        print(__doc__.strip())
        return 0
    else:
        for f in files(argv):
            try:
                hits += scan(f.read_text(encoding="utf-8", errors="replace"), str(f), quotes, f.suffix in CODE)
            except OSError:
                pass
    for h in hits:
        print(h)
    print(f"\n{len(hits)} hit(s). ~/.claude/STYLE.md has the rewrites." if hits else "clean")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
