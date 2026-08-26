---
description: Full save — archive chats, refresh code graphs, log, gate, relay handoff, commit
---

Wrap up this session properly:

1. **Archive memory:** `python scripts/import_chats.py` (Claude + Codex
   transcripts → gitignored `chats/`); `python scripts/sync_graphs.py`
   (refresh committed code-graph snapshots, if repos are tracked).
2. **Log it:** `python scripts/wiki_tool.py log --title "..." --details "..."`;
   add a `Wiki/Logs/` note (template `_templates/log-note.md`) if the change
   was substantial, with wikilinks.
3. **Gate:**
   `python scripts/wiki_tool.py doctor` → `build` → `lint` → `source-lint` →
   `python scripts/audit_public.py`
   (after ingests also `source-scan --update --accept-covered` + `source-lint`).
   All must pass — fix causes, not symptoms.
4. **Relay handoff:** rewrite `_relay/STATE.md` (Now / Just landed / Next /
   Open questions / Watch out) per the `relay` skill, then
   `python scripts/relay_tool.py stamp --agent claude --summary "<paragraph>"`.
5. **Commit** vault knowledge + regenerated artifacts + the baton together,
   with a clear message. Chat dumps stay gitignored.
