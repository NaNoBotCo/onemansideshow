---
name: field-ingest
description: Ingest camera captures from the drop folder, name them, file them toward the owner's projects
---

The owner drops photos and clips into ~/Desktop/FIELD DROP/. Everything after the drop
is this task's.

1. `python3 ~/.claude/bin/field_ingest.py`. It moves each file to
   ~/Desktop/Video/Field/<date>/, writes a .json sidecar (original name, time, lat/lng
   when present, camera, duration) and logs a row in ~/.claude/state/field.tsv marked
   "unfiled". On "nothing new in the drop", end.
2. For each new file, decide where it points (the targets are in CLAUDE.md under
   "Field capture") and write that into the sidecar as "filed" plus a one-line "why".
   Record only what the image shows. A file that needs the owner's judgment is marked
   "held".
3. Update the field.tsv rows from "unfiled" to where they went.
4. `python3 ~/.claude/bin/state.py`.

Nothing is deleted or published by this task.
