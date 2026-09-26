ONE MAN SIDESHOW
================

A Claude Code setup for one person running many projects.
The page: https://nanobotco.github.io/onemansideshow/

  kit/        the free kit: scripts, templates, scheduled-task prompts, installer
  docs/       the page (GitHub Pages): index.html, card.png, llms.txt, robots.txt, sitemap.xml
  tools/      check.sh (gates), scrub.py (personal-trace gate), card.py (share card),
              serve.py (preview)


INSTALL (Mac, Claude Code already installed)

  sh kit/install.sh

Four questions: your name, your money lanes, where field photos go, and what needs
your word with no default. An existing file is kept; the kit's copy lands beside it
as <name>.kit.

It puts:
  ~/.claude/CLAUDE.md, STYLE.md, style-rules.txt
  ~/.claude/bin/        state.py  decide.py  stylecheck.py  stylehook.py
                        field_ingest.py  shortlink.py  pr-push
  ~/.claude/state/      the ledgers (tab-separated, headers only)
  ~/.claude/scheduled-tasks/   nightly-pass  money-lane  field-ingest
  ~/Desktop/1 — NEXT UP/QUEUE.txt  and  STATE.txt
  ~/Desktop/FIELD DROP/  and  ~/Desktop/go/
  a style hook in ~/.claude/settings.json
  a launchd job that rebuilds STATE.txt at 07:00 and 19:00

Then ask Claude to schedule the three tasks, and copy ~/.claude/memory-kit/ into the
project's memory folder.


GATES

  sh tools/check.sh             scrub, style, compile, installer dry run
  sh tools/check.sh --publish   also fails while the site has an open {{…}} slot

scrub.py reads its term list from ../onemansideshow-private/scrub-terms.txt, outside
this folder. kit/ and tools/ carry nothing of their maker; docs/ and this README name
her on purpose and are checked only for the private terms.


SETUP FOR YOU

  25,000 baht for Thai companies, US$25,000 for everyone else. Training included.
  nan@motdang.net


LICENCES

  Code (kit/, tools/): MIT, LICENSE-CODE.
  The page, its text, card and drawings (docs/): CC BY 4.0, LICENSE.
