#!/usr/bin/env python3
"""PostToolUse hook: run stylecheck on whatever a session just wrote.

Registered in ~/.claude/settings.json for Write|Edit|MultiEdit|NotebookEdit.
Reads the hook payload on stdin, scans the file that was touched, and on a hit
exits 2 with the report on stderr — which Claude Code feeds back to the session,
so the words get fixed before anyone reads them.

Fails open: any error here exits 0.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_PART = {".git", "node_modules", "__pycache__", "build", "docs", "dist", ".venv", "venv"}


def load_checker():
    spec = importlib.util.spec_from_file_location("stylecheck", HERE / "stylecheck.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    ti = payload.get("tool_input") or {}
    paths = [ti.get("file_path") or ti.get("notebook_path") or ""]
    for e in ti.get("edits") or []:                       # MultiEdit
        if isinstance(e, dict) and e.get("file_path"):
            paths.append(e["file_path"])

    try:
        sc = load_checker()
    except Exception:
        return 0

    hits = []
    for raw in {p for p in paths if p}:
        f = Path(raw)
        if f.suffix not in sc.TEXTY or any(part in SKIP_PART for part in f.parts):
            continue
        if not f.is_file() or f.stat().st_size > 2_000_000:
            continue
        try:
            hits += sc.scan(f.read_text(encoding="utf-8", errors="replace"), str(f), False)
        except Exception:
            continue

    if not hits:
        return 0

    shown = hits[:25]
    more = len(hits) - len(shown)
    print("STYLE — " + str(len(hits)) + " hit(s) in what you just wrote:", file=sys.stderr)
    for h in shown:
        print("  " + h, file=sys.stderr)
    if more:
        print("  … and " + str(more) + " more", file=sys.stderr)
    print("\nRewrite them. ~/.claude/STYLE.md has the rewrites; a quotation passes, and a\n"
          "line that has to name the words takes `stylecheck: allow`.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
