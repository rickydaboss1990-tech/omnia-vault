---
description: Answer a question from the vault's layered memory (graph → wiki → raw, cheapest first)
argument-hint: <your question>
---

Answer this question using the `project-context-query` skill (3-layer rule):
$ARGUMENTS

1. Code/architecture questions → graphify first
   (`graphify query "..." --graph graphify/<repo>/graph.json`).
2. Knowledge/process/decision questions → the compiled wiki
   (`python scripts/wiki_tool.py search-catalog --query "..."` → open top 1–3
   notes).
3. Raw sources / raw code only when layers 1–2 are insufficient, and narrowly.

Cite the compiled note (and the Raw source if the answer depends on source
material). If the vault has no answer, say so and suggest what to ingest.
