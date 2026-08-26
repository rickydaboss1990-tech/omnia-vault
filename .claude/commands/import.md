---
description: Adopt an EXISTING project (repos, docs, recordings) into this Cortex vault
argument-hint: [optional: paths or notes about what to import]
---

Adopt an existing project into this vault. Follow the `import-project` skill
end to end:

1. Confirm the material is in the vault root (or ask the user to drop it in /
   point you at it). Context from the user: $ARGUMENTS
2. `python scripts/setup_vault.py --inventory` → review
   `_relay/IMPORT-INVENTORY.md` WITH the user: what imports now, what's
   skipped, what order.
3. Repos: gitignore (`--gitignore-repos`), graph each one
   (`/graphify <repo> --obsidian --obsidian-dir graphify/<repo>`), install
   `graphify hook install` in each.
4. Seed the project + topic notes (`setup_vault.py --name ...`), fill Goal /
   Status / Next Steps.
5. Ingest confirmed documents per `llm-wiki-ingest`; recordings per
   `video-ingest` (background). Search-catalog before every compile; enrich
   over duplicate.
6. Gate → relay handoff (STATE.md + stamp) → commit. Work in increments; a
   large import is several commits, not one.
