---
description: Build or maintain the project's living plan (Plan/ — roadmap, phases, toolbox)
argument-hint: [project name, or empty to review/update the existing plan]
---

Run the `war-room` skill, Part 1, on: $ARGUMENTS

- **No Plan/ yet:** recon the vault first (baton, catalog, project note; ingest
  any kickoff meetings/videos the user has), interview with load-bearing
  questions only (vision, success criteria, phases + exit criteria), then
  `python scripts/plan_tool.py init --name "..." --phases "..."` and fill
  every placeholder in ROADMAP.md and the phase files. Link the plan from the
  Wiki project note, put the active phase in the relay baton, gate, commit.
- **Plan/ exists:** `python scripts/plan_tool.py status` +
  `python scripts/plan_tool.py context`, review with the user — check off
  shipped deliverables, handle phase transitions (one phase active at a
  time), log Changelog lines with provenance, flag stale `trialing` tools.
- A restructuring-sized change deserves `/spar` before the rewrite.
