#!/bin/sh
# check.sh — gates for the kit and the site.   sh tools/check.sh [--publish]
# --publish also fails while the site still carries a {{…}} slot.
set -e
cd "$(dirname "$0")/.."
python3 tools/scrub.py
python3 kit/claude/bin/stylecheck.py kit README.txt docs/index.html docs/llms.txt
test -s docs/card.png || { echo "no share card: python3 tools/card.py"; exit 1; }
python3 -m py_compile kit/claude/bin/*.py tools/*.py
T=$(mktemp -d)
printf 'Test\nlane\nproject\nclass three\n' | HOME="$T" KIT_NO_LAUNCHD=1 sh kit/install.sh >/dev/null 2>&1
test -s "$T/Desktop/1 — NEXT UP/STATE.txt" && grep -q "Owner: Test" "$T/.claude/CLAUDE.md"
rm -rf "$T"
echo "installer ok"
if [ "$1" = --publish ]; then
  if grep -n '{{' docs/index.html; then echo "slots still open"; exit 1; fi
  echo "publish ok"
fi
