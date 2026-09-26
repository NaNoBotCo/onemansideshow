# Standing rules — every project, every session

Owner: {{OWNER}}. Every "you" in the queue and the screen is {{OWNER}}.

**Read `~/.claude/STYLE.md` before writing anything {{OWNER}} or a reader will see.**

```
python3 ~/.claude/bin/stylecheck.py --stdin     # a draft
python3 ~/.claude/bin/stylecheck.py <path>...   # files or a repo
```

A PostToolUse hook runs that checker on every file written or edited. The words and
forms it flags are in `~/.claude/style-rules.txt`.

## Classes

Every finished build falls into one of these:

1. **Ships without asking.** A site already live and already the owner's, gates green,
   no new claim about what the thing does. Deploy it, record it as SHIPPED in
   QUEUE.txt, never open a conversation about it.
2. **The owner's word, every time.** A new domain, a new public identity, a price, the
   first outward email of a thread.
3. **The owner's word, every time, no default.** {{CLASS_3}}

A red gate keeps the item in A with one line saying which gate. Gates are not edited or
skipped to make class 1 apply.

## The queue

`~/Desktop/1 — NEXT UP/QUEUE.txt` holds everything waiting on the owner, in three lanes:

- **A — say go.** Built, tested, gates green. One word and it deploys.
- **B — your hands.** Only the owner can do it (a login, a signature, a phone call).
- **C — deciding.** A fork: options, costs, worst case. Each carries
  `⏳ if silent: <what happens> · fires YYYY-MM-DD`: what happens if the owner never
  answers. The default is the cheaper, quieter branch. Class 3 items carry
  `no default — yours` and never fire.

`nightly-pass` runs the due defaults, strikes them to a DORMANT tail, and logs each to
`~/.claude/state/decisions.tsv` through `decide.py`.

## The screen

`~/Desktop/1 — NEXT UP/STATE.txt`, written by `python3 ~/.claude/bin/state.py`. QUEUE.txt
is the long form; STATE.txt is what the owner opens. Ledgers it reads:
`~/.claude/state/{earning,live,asks,field,traffic}.tsv`.

## Money lane

One ask a week: a named person, a complete thing, a price, a send date, built to
completion and parked in A for one word. Lane order: {{LANES}}. The metric is asks
out, counted in `~/.claude/state/asks.tsv`. Task: `money-lane`, Mondays.

## Field capture

The owner drops camera captures into `~/Desktop/FIELD DROP/`. `field_ingest.py` names
and logs them; the `field-ingest` task files them toward {{FIELD_TARGETS}}.

## Links

A file named in an answer is given as a `~/Desktop/go/` link:
`python3 ~/.claude/bin/shortlink.py add <path> <short>`.

## GitHub

`~/.claude/bin/pr-push <repo-dir> [title]` pushes local main to a `bot/…` branch, opens
the PR, merges it, deletes the branch and fast-forwards main. It refuses when main is
behind origin.

## Memory

The memory folder holds `CONSTITUTION.md` (the canonical record, read in full at the start
of a session, lines leave it only on the owner's word) and `MEMORY.md` (the running log
since the last fold).
