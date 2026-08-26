---
description: Build or refresh the code knowledge graphs (graphify) for tracked repos
argument-hint: [repo folder, or empty for all]
---

Keep the code-graph layer current. Target: $ARGUMENTS

- **Quick refresh (default):** `python scripts/sync_graphs.py` — AST-only
  rebuild + snapshot copy into `graphify/<repo>/` for every detected repo.
- **First build for a repo (or full re-export of browsable notes):** run the
  `graphify` skill: `/graphify <repo> --obsidian --obsidian-dir graphify/<repo>`,
  then `graphify hook install` inside the repo so commits auto-rebuild its
  graph.
- After refreshing, verify with a smoke query:
  `graphify query "main entry points" --graph graphify/<repo>/graph.json`
  (set `$env:PYTHONUTF8=1` on Windows first).
- Commit the refreshed `graphify/` snapshots (never hand-edit them).
