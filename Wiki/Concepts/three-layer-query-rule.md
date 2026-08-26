---
tags:
  - "concept"
topics:
  - "cortex"
status: evergreen
created: 2026-08-26
updated: 2026-08-26
sources:
  - "Raw/Sources/cortex-system-demo.md"
source_count: 1
aliases:
  - "3-layer rule"
---

# Three-Layer Query Rule

Route every question to the cheapest memory that can answer it, and escalate
only when it falls short: **(1) the Graphify code graph** for anything about
code structure or impact, **(2) the compiled Wiki catalog** for decisions,
process, people, and history, **(3) raw files last** — the one source a note
cites, or the one code file being edited. Never sweep.

## Why It Matters

Context is the scarce resource. The rule keeps sessions fast and answers
citable: graphs compress a codebase into queryable structure, the catalog
compresses every past ingest into searchable notes, and raw reads happen only
with a precise target.

## Details

- Layer 1: `graphify query "..." --graph graphify/<repo>/graph.json` (also
  `explain`, `path`, `affected`).
- Layer 2: `python scripts/wiki_tool.py search-catalog --query "..."` → open
  the top 1–3 notes.
- Layer 3: the specific cited `Raw/Sources/` file, or the specific repo file.
- Full traversal recipe: the `project-context-query` skill.

## Related

- [[cortex]]
- [[raw-vs-compiled-knowledge]]
