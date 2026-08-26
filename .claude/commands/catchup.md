---
description: Catch up on where the project stands (reads the relay baton — never re-reads raw context)
---

Catch up per the `relay` skill:

1. Read `_relay/STATE.md` in full.
2. `python scripts/relay_tool.py status` — if it warns the baton is stale,
   trust `git log --oneline -15` + the newest `Wiki/Logs/` note instead, then
   repair STATE.md.
3. `git log --oneline -10`.
4. If needed for depth: newest `Wiki/Logs/` note + the active
   `Wiki/Projects/` note's Status + Next Steps.
5. Report back in a few sentences: where things stand, what's in flight, what
   you propose to do next. Do NOT re-read Raw sources, sweep repos, or replay
   chats to resume.
