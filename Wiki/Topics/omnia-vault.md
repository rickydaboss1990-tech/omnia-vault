---
tags:
  - "topic"
topics: []
status: growing
created: 2026-08-26
updated: 2026-08-26
sources:
  - "Raw/Sources/omnia-vault-system-demo.md"
source_count: 1
aliases:
  - "the vault system"
---

# Omnia Vault

The operating system this vault runs on: an Obsidian LLM Wiki + Graphify code
graphs + a Claude Code ⇄ Codex relay. This topic hub groups the concepts that
explain how to work here. (It doubles as the built-in demo of a topic note —
prune with `python scripts/setup_vault.py --prune-demo` once your real topics
exist.)

## Key Concepts

- [[raw-vs-compiled-knowledge]] — why sources and notes are separate layers
- [[three-layer-query-rule]] — graph → wiki → raw, cheapest first
- [[the-relay]] — how two agents share one project with zero copy-paste

## Open Questions

- What is this vault's first real topic? Run `/setup` (or
  `python scripts/setup_vault.py --name "..."`) and start ingesting.
