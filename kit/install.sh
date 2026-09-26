#!/bin/sh
# install.sh — put the One Man Sideshow kit into ~/.claude and onto the Desktop.
# usage: sh install.sh            (asks four questions)
# An existing file is kept; the kit's copy lands beside it as <name>.kit.
set -e
KIT=$(cd "$(dirname "$0")" && pwd)
C="$HOME/.claude"
NEXT="$HOME/Desktop/1 — NEXT UP"

ask() { printf "%s " "$1" >&2; read -r v; printf %s "${v:-$2}"; }
OWNER=$(ask "Your name?" "the owner")
LANES=$(ask "Money lanes, in order (comma list)?" "consulting, products, donations")
FIELD=$(ask "Where do field photos go (projects, comma list)?" "the owner's projects")
CLASS3=$(ask "What needs your word with no default (class 3)?" "Anything legal, medical or financial.")

put() {  # put <src> <dest>
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ]; then cp "$1" "$2.kit"; echo "kept   $2  (kit copy: $2.kit)"
  else cp "$1" "$2"; echo "added  $2"; fi
}

for f in "$KIT"/claude/bin/*; do put "$f" "$C/bin/$(basename "$f")"; done
chmod +x "$C/bin/pr-push"
for f in "$KIT"/claude/state/*.tsv; do put "$f" "$C/state/$(basename "$f")"; done
for d in "$KIT"/claude/scheduled-tasks/*/; do
  n=$(basename "$d"); put "$d/SKILL.md" "$C/scheduled-tasks/$n/SKILL.md"; done
put "$KIT/claude/STYLE.md" "$C/STYLE.md"
put "$KIT/claude/style-rules.txt" "$C/style-rules.txt"

tmp=$(mktemp)
sed -e "s|{{OWNER}}|$OWNER|g" -e "s|{{LANES}}|$LANES|g" \
    -e "s|{{FIELD_TARGETS}}|$FIELD|g" -e "s|{{CLASS_3}}|$CLASS3|g" \
    "$KIT/claude/CLAUDE.md" > "$tmp"
put "$tmp" "$C/CLAUDE.md"
sed "s|{{OWNER}}|$OWNER|g" "$KIT/memory/CONSTITUTION.md" > "$tmp"
MEM="$C/memory-kit"
put "$tmp" "$MEM/CONSTITUTION.md"
put "$KIT/memory/MEMORY.md" "$MEM/MEMORY.md"
rm -f "$tmp"

put "$KIT/desktop/QUEUE.txt" "$NEXT/QUEUE.txt"
mkdir -p "$HOME/Desktop/FIELD DROP" "$HOME/Desktop/go"

# the style hook, merged into settings.json
python3 - "$C/settings.json" <<'EOF'
import json, os, sys
p = sys.argv[1]
d = json.load(open(p)) if os.path.exists(p) else {}
cmd = 'python3 "$HOME/.claude/bin/stylehook.py"'
post = d.setdefault("hooks", {}).setdefault("PostToolUse", [])
if not any(h.get("command") == cmd for e in post for h in e.get("hooks", [])):
    post.append({"matcher": "Write|Edit|MultiEdit|NotebookEdit",
                 "hooks": [{"type": "command", "command": cmd, "timeout": 15}]})
    json.dump(d, open(p, "w"), indent=2)
    print("hook   stylecheck on every write")
else:
    print("hook   already present")
EOF

# the screen, rebuilt at 07:00 and 19:00 (macOS)
if [ "$(uname)" = Darwin ] && [ -z "$KIT_NO_LAUNCHD" ]; then
  L="$HOME/Library/LaunchAgents/net.onemansideshow.state.plist"
  if [ ! -e "$L" ]; then
    mkdir -p "$(dirname "$L")"
    cat > "$L" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>net.onemansideshow.state</string>
<key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$C/bin/state.py</string></array>
<key>StartCalendarInterval</key><array>
<dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
<dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
</array></dict></plist>
EOF
    launchctl load "$L" 2>/dev/null || true
    echo "added  $L"
  fi
fi

python3 "$C/bin/state.py"
echo
echo "Next: copy $MEM/* into this machine's Claude memory folder, and ask Claude to"
echo "schedule nightly-pass (nightly), money-lane (Mondays) and field-ingest (daily)."
