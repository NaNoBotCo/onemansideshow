---
name: nightly-pass
description: Run past-due silent defaults in QUEUE.txt, deploy class-1 builds, rebuild STATE.txt
---

Nightly pass. Read ~/.claude/STYLE.md, then ~/Desktop/1 — NEXT UP/QUEUE.txt.

JOB 1 — THE DUE DEFAULTS.
For each C item whose "⏳ if silent: … · fires YYYY-MM-DD" date is today or earlier:
  - Do what the default says. Most say "leave it / drop it" and need only the strike.
  - Strike it: move its block under "DORMANT — struck items", first line prefixed
    "STRUCK <date> by default:". Items are moved, not deleted.
  - Log it: `python3 ~/.claude/bin/decide.py --item C<n> --chose "<what ran>" --by silence`
    and a row in ~/.claude/state/passes.tsv (date, "default fired", what happened).
Skip items marked "no default — yours". Do not invent a default on the night.
Before a default that spends money, registers a domain, publishes a price or sends a
first email, stop and move the item to B with one line saying why.

JOB 2 — THE SHIP LANE (class 1).
At most two A items a night, newest first. For each: read its note, run the project's
own gates; if every gate is green, deploy by the project's documented command and move
it to a SHIPPED line with the date and what changed. If a gate is red, leave it in A
with one line naming the gate. Gates are not edited to get past them.

THEN: `python3 ~/.claude/bin/state.py`.

If nothing was due and nothing shipped, change nothing and end.
