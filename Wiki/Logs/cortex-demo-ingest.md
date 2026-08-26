---
tags:
  - "log"
topics:
  - "cortex"
status: evergreen
created: 2026-08-26
updated: 2026-08-26
sources:
  - "Raw/Sources/cortex-system-demo.md"
source_count: 1
aliases: []
---

# Log: 2026-08-26 Built-in demo ingest

## What Changed

Seeded the vault's built-in demo: one Raw source
([[cortex-system-demo]]) compiled into the [[cortex]] topic hub and three
concepts — [[raw-vs-compiled-knowledge]], [[three-layer-query-rule]],
[[the-relay]].

## Why

A fresh clone should show the whole Raw → Wiki loop working (and give the
Obsidian graph something to draw) before any real content lands. It doubles as
a worked example of note structure, frontmatter, and source tracing.

## Follow-Ups

- [ ] Once real content exists, prune the demo:
      `python scripts/setup_vault.py --prune-demo`
