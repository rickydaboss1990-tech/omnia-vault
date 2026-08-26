---
description: Initialize this Cortex vault for a NEW project (seed notes, relay baton, first commit)
argument-hint: [project name]
---

Initialize this Cortex vault for a new project.

1. If `$ARGUMENTS` is empty, ask the user for: the project name, the main
   topic/domain (may default to the name), and whether code repos will live in
   this folder. Otherwise treat `$ARGUMENTS` as the project name and ask only
   what's missing.
2. Run `python scripts/setup_vault.py --check` and report any missing optional
   tooling with its install hint (do not block on it).
3. Run `python scripts/setup_vault.py --name "<name>" --topic "<topic>"`.
4. Open the seeded `Wiki/Projects/<slug>.md` and fill in Goal / Status / Next
   Steps from what the user told you. Bump nothing else.
5. If repos will be tracked: follow Step 2 of the `import-project` skill
   (gitignore repos, `/graphify <repo> --obsidian --obsidian-dir graphify/<repo>`,
   `graphify hook install`).
6. Offer `python scripts/setup_vault.py --prune-demo` (recommend keeping the
   demo until the first real ingest, as a worked example).
7. Run the maintenance gate: `doctor`, `build`, `lint`, `source-lint`,
   `python scripts/audit_public.py` — all must pass.
8. Hand off per the `relay` skill (rewrite `_relay/STATE.md`, stamp with
   `--agent claude`), then commit everything with a clear message.
9. Tell the user the daily loop: **/catchup → work → /save**, and that Codex
   picks up the same baton via `AGENTS.md`.
