#!/usr/bin/env python3
"""STATE.txt — one screen, generated from QUEUE.txt and the state ledgers.

  python3 ~/.claude/bin/state.py            # write STATE.txt
  python3 ~/.claude/bin/state.py --stdout   # print it

Sources
  ~/Desktop/1 — NEXT UP/QUEUE.txt   A / B / C items and their silent defaults
  ~/.claude/state/earning.tsv       date  thread  amount  note
  ~/.claude/state/live.tsv          surface  url  note
  ~/.claude/state/asks.tsv          date  thread  person  what  status
  ~/.claude/state/field.tsv         date  file  place  filed-to
  ~/.claude/state/traffic.tsv       date  zone  requests  pageviews  uniques  (optional)
"""
import datetime as dt
import os
import pathlib
import re
import sys

HOME = os.path.expanduser("~")
QUEUE = os.path.join(HOME, "Desktop", "1 — NEXT UP", "QUEUE.txt")
STATE = os.path.join(HOME, "Desktop", "1 — NEXT UP", "STATE.txt")
LEDGER = os.path.join(HOME, ".claude", "state")
W = 78
TODAY = dt.date.today()

ITEM = re.compile(r"^([ABC])(\d+)\s+(.*)$")
SILENT = re.compile(r"if silent:\s*(.*?)\s*·\s*fires\s*(\d{4}-\d{2}-\d{2})")
YOURS = re.compile(r"no default — yours", re.I)


def rows(name):
    path = os.path.join(LEDGER, name)
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        out.append(line.split("\t"))
    return out


def queue():
    """Return A, B, C lists of dicts read out of QUEUE.txt."""
    if not os.path.exists(QUEUE):
        return {"A": [], "B": [], "C": []}
    lanes = {"A": [], "B": [], "C": []}
    cur = None
    for line in open(QUEUE, encoding="utf-8"):
        if line.startswith("DORMANT — struck items"):
            break
        m = ITEM.match(line)
        if m:
            cur = {
                "id": m.group(1) + m.group(2),
                "lane": m.group(1),
                "title": m.group(3).strip(),
                "body": "",
                "default": None,
                "fires": None,
                "yours": False,
            }
            lanes[m.group(1)].append(cur)
            continue
        if cur is None:
            continue
        if line.startswith("---") or line.startswith("==="):
            cur = None
            continue
        cur["body"] += line
        s = SILENT.search(line)
        if s:
            cur["default"] = s.group(1)
            try:
                cur["fires"] = dt.date.fromisoformat(s.group(2))
            except ValueError:
                pass
        if YOURS.search(line):
            cur["yours"] = True
    return lanes


def head(text):
    return [text, "-" * W]


def trim(text, n=W - 4):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def label(item, n=66):
    """Title plus enough of the body to read as a sentence."""
    body = " ".join(item["body"].split())
    body = body.split("⏳")[0]
    return trim((item["title"] + " " + body).strip(), n)


def traffic():
    """The edge count, per zone, for the last day that is complete."""
    rows = [r for r in rows_traffic() if len(r) == 5]
    if not rows:
        return None, []
    days = sorted({r[0] for r in rows})
    complete = [d for d in days if d < str(TODAY)]
    if not complete:
        return None, []
    day = complete[-1]
    prior = [d for d in complete[-8:-1]]
    out = []
    for r in sorted((r for r in rows if r[0] == day), key=lambda r: -int(r[3])):
        zone = r[1]
        pv, uq = int(r[3]), int(r[4])
        was = [int(x[3]) for x in rows if x[1] == zone and x[0] in prior]
        mean = sum(was) // len(was) if was else 0
        mark = "" if not mean else (" ↑" if pv > mean * 1.2 else " ↓" if pv < mean * 0.8 else " ·")
        out.append(f"  {zone:<22} {pv:>9,} pageviews · {uq:>7,} IPs   "
                   f"{('7-day mean ' + format(mean, ',')) if mean else ''}{mark}")
    return day, out


def rows_traffic():
    return rows("traffic.tsv")

def build():
    lanes = queue()
    out = []
    out.append("=" * W)
    out.append("STATE — what is true right now")
    out.append(f"{TODAY:%Y-%m-%d %A} · generated · the long form is QUEUE.txt")
    out.append("=" * W)
    out.append("")

    earning = rows("earning.tsv")
    live = rows("live.tsv")
    asks = rows("asks.tsv")
    field = rows("field.tsv")
    firing = sorted(
        [c for c in lanes["C"] if c["fires"]], key=lambda c: c["fires"]
    )
    due = [c for c in firing if c["fires"] <= TODAY]
    soon = [c for c in firing if 0 < (c["fires"] - TODAY).days <= 7]
    mine = [c for c in lanes["C"] if c["yours"]]

    out.append("  COUNTS")
    out.append(f"    earning        {len(earning)}")
    out.append(f"    live           {len(live)}")
    out.append(f"    built, not out {len(lanes['A'])}")
    out.append(f"    your hands     {len(lanes['B'])}")
    out.append(f"    deciding       {len(lanes['C'])}  "
               f"({len(mine)} yours, {len(firing)} on a clock)")
    out.append(f"    past due       {len(due)}  (the default runs tonight)")
    out.append(f"    firing ≤7 days {len(soon)}")
    week = [a for a in asks if a and a[0] >= str(TODAY - dt.timedelta(days=7))]
    out.append(f"    asks out       {len(asks)} total, {len(week)} this week")
    out.append("")

    day, lines = traffic()
    if lines:
        out += head(f"TRAFFIC — the edge, {day}; bots included, IPs are not people")
        out += lines
        out.append("")

    if due:
        out += head("PAST DUE — the default runs on tonight's pass")
        for c in due:
            out.append(f"  {c['fires']}  {c['id']}  {trim(c['title'], 52)}")
            out.append(f"              → {trim(c['default'], 58)}")
        out.append("")

    if soon:
        out += head("FIRING SOON — a default lands unless you say otherwise")
        for c in soon:
            out.append(f"  {c['fires']}  {c['id']}  {trim(c['title'], 52)}")
            out.append(f"              → {trim(c['default'], 58)}")
        out.append("")

    out += head("EARNING")
    if earning:
        for r in earning[-6:]:
            out.append("  " + trim(" · ".join(r)))
    else:
        out.append("  nothing recorded")
    out.append("")

    out += head("ASKS OUT — a named person, a complete thing, a price")
    if asks:
        for r in asks[-6:]:
            out.append("  " + trim(" · ".join(r)))
    else:
        out.append("  none yet")
    out.append("")

    out += head("BUILT, NOT OUT — class 1 ships these unattended")
    for a in lanes["A"][:8]:
        out.append(f"  {a['id']}  {label(a)}")
    if not lanes["A"]:
        out.append("  nothing waiting")
    out.append("")

    out += head("YOUR HANDS")
    for b in lanes["B"][:8]:
        out.append(f"  {b['id']}  {label(b)}")
    if not lanes["B"]:
        out.append("  nothing waiting")
    out.append("")

    out += head("DECIDING — yours, no default fires")
    for c in mine[:10]:
        out.append(f"  {c['id']}  {label(c)}")
    if not mine:
        out.append("  none")
    out.append("")

    out += head("FIELD — off the card")
    if field:
        for r in field[-6:]:
            out.append("  " + trim(" · ".join(r)))
    else:
        out.append("  nothing ingested")
    out.append("")

    out += head("LIVE")
    for r in live:
        out.append("  " + trim(" · ".join(r)))
    if not live:
        out.append("  nothing recorded")
    out.append("")
    out.append(pathlib.Path(STATE).as_uri())
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    text = build()
    if "--stdout" in sys.argv:
        sys.stdout.write(text)
    else:
        with open(STATE, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(STATE)
