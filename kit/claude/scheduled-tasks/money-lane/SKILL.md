---
name: money-lane
description: Build one complete ask aimed at a named payer and park it in QUEUE lane A for one word
---

One ask a week, aimed at a person who could pay. Read ~/.claude/STYLE.md first.

Lane order is in ~/.claude/CLAUDE.md under "Money lane". Work down it; return to the top
at the bottom.

An ask counts when all four are true: a named person, a complete thing they can use or
see, a price in writing, a send date.

Build this week's ask to completion:
  - The thing itself, stood up and checked working.
  - The price, written down. Every instrument has a $0 version.
  - The email, drafted in full and signed as CLAUDE.md says.
  - The recipient by name. A role at a company is not a name; research until there is one.

Park it as an A item in ~/Desktop/1 — NEXT UP/QUEUE.txt: one line with the price, the
person, and a go/ link to the full thing (`python3 ~/.claude/bin/shortlink.py add`).

When the owner says go and it sends, append to ~/.claude/state/asks.tsv
(date, thread, person, what, status). When money moves, append to earning.tsv
(date, thread, amount, note). Then `python3 ~/.claude/bin/state.py`.
