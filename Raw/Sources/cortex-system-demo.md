---
Title: "Cortex system overview (demo source)"
Author: "Cortex"
Reference: "VAULT-GUIDE.md"
ContentType:
  - "markdown"
Created: 2026-08-26
Processed: true
tags:
  - "source"
---

# Cortex system overview (demo source)

<!-- This is the vault's built-in DEMO source: it exists so a fresh clone shows
     the full Raw -> Wiki loop working end to end. Prune it once you have real
     content: `python scripts/setup_vault.py --prune-demo`. -->

Cortex is a project brain: an Obsidian LLM Wiki, code knowledge graphs, and a
two-agent relay in one repository.

The wiki half separates two layers. The Raw layer captures source material
verbatim — meeting transcripts, articles, extracted documents, video
walkthroughs — and never rewrites it. The compiled layer distills that material
into short notes that each hold one reusable idea, link to related notes, and
name the exact Raw files that support them. Agents answer questions from the
compiled layer first, which keeps answers fast, cheap, and citable.

The code half uses Graphify: each tracked repository gets a knowledge graph
(one node per code entity, communities named in plain language) that agents
query before they ever open source files. Questions route through three layers,
cheapest first: graph, then wiki, then raw files.

The relay half is a baton file. Whichever agent ends a session — Claude Code or
Codex — rewrites `_relay/STATE.md` to describe the present state of the work,
stamps it, and commits. Whichever agent starts next reads the baton first. Two
different tools, one shared memory, no copy-paste.

Deterministic python scripts hold it together: a build/lint/audit gate that
runs before every commit, importers that archive both agents' chat transcripts
as local memory, and a sync tool that keeps committed graph snapshots fresh.
