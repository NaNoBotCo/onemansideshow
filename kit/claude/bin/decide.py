#!/usr/bin/env python3
"""Append-only record of what was offered and what was chosen.

QUEUE.txt is rewritten in place and keeps no history; this ledger does.

  decide.py --item C69 --offered "a|b|c|d" --chose b --by silence --note "..."
  decide.py --snapshot        # stamp a copy of QUEUE.txt before a rewrite
"""
import argparse, datetime, os, shutil, sys

STATE = os.path.expanduser("~/.claude/state")
LEDGER = os.path.join(STATE, "decisions.tsv")
QUEUE = os.path.expanduser("~/Desktop/1 — NEXT UP/QUEUE.txt")
SNAPS = os.path.join(STATE, "queue-snapshots")
HEADER = "# date\titem\toffered\tchose\tby\tnote\n"

def snapshot():
    os.makedirs(SNAPS, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(SNAPS, f"QUEUE-{stamp}.txt")
    shutil.copy2(QUEUE, dest)
    return dest

def append(item, offered, chose, by, note):
    os.makedirs(STATE, exist_ok=True)
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a", encoding="utf-8") as fh:
        if new:
            fh.write(HEADER)
        row = [datetime.date.today().isoformat(), item, offered, chose, by,
               (note or "").replace("\t", " ").replace("\n", " ")]
        fh.write("\t".join(row) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item", default="")
    ap.add_argument("--offered", default="", help="options as put, pipe-separated")
    ap.add_argument("--chose", default="")
    ap.add_argument("--by", default="owner", choices=["owner", "silence", "machine"])
    ap.add_argument("--note", default="")
    ap.add_argument("--snapshot", action="store_true")
    a = ap.parse_args()
    if a.snapshot:
        print(snapshot())
        if not a.item:
            return
    if not a.item or not a.chose:
        ap.error("--item and --chose are required unless only --snapshot")
    append(a.item, a.offered, a.chose, a.by, a.note)
    print(f"logged: {a.item} -> {a.chose} ({a.by})")

if __name__ == "__main__":
    main()
