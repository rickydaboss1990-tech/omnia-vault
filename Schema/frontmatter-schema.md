# Frontmatter Schema

All notes in this vault use YAML frontmatter. Two contracts exist: one for Raw
source notes and one for compiled Wiki notes.

## Raw Source Notes (`Raw/Sources/*.md`)

```yaml
---
Title: ""              # required, human-readable title
Author: ""             # optional, creator of the source
Reference: ""          # required, URL or identifier of the original
ContentType:           # required, list; usually "markdown"
  - "markdown"
Created: YYYY-MM-DD    # required, date the source was captured
Processed: false       # required, true once compiled into Wiki notes
tags:                  # required, must include "source"
  - "source"
---
```

Rules:
- `Title`, `Reference`, `Created`, `Processed`, and `tags` are required.
- `Processed` starts `false` and flips to `true` only after at least one
  compiled Wiki note lists this file in its `sources`.

## Compiled Wiki Notes (`Wiki/**/*.md`)

```yaml
---
tags:                  # required, exactly one allowed tag
  - "concept"
topics: []             # list of related topic note names
status: seed           # seed | growing | evergreen
created: YYYY-MM-DD    # required
updated: YYYY-MM-DD    # required, bump on every meaningful edit
sources: []            # required, paths under Raw/Sources/
source_count: 0        # required, must equal len(sources)
aliases: []            # optional alternate names
---
```

Rules:
- Exactly one allowed tag per note: `topic`, `concept`, `entity`, `project`,
  or `log`.
- The tag must match the folder: `topic` → `Wiki/Topics/`, `concept` →
  `Wiki/Concepts/`, `entity` → `Wiki/Entities/`, `project` → `Wiki/Projects/`,
  `log` → `Wiki/Logs/`.
- `sources` entries must be vault-relative paths to existing files under
  `Raw/Sources/` (e.g. `Raw/Sources/why-llm-wiki.md`).
- `source_count` must always equal the number of entries in `sources`.
- Dates use `YYYY-MM-DD`.

## Status Values

| Status | Meaning |
|--------|---------|
| `seed` | New note, minimal content, needs development |
| `growing` | Actively developed, partially sourced |
| `evergreen` | Stable, well-sourced, reusable |
