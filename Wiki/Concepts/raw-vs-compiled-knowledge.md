---
tags:
  - "concept"
topics:
  - "omnia-vault"
status: evergreen
created: 2026-08-26
updated: 2026-08-26
sources:
  - "Raw/Sources/omnia-vault-system-demo.md"
source_count: 1
aliases: []
---

# Raw vs Compiled Knowledge

Source material and reusable knowledge live in different layers. `Raw/Sources/`
holds what was actually said or written — transcripts, articles, extracted
documents — captured verbatim and never edited in place. `Wiki/` holds what it
*means*: short notes, one idea each, linked with `[[wikilinks]]`, each naming
the Raw files that support it in `sources`.

## Why It Matters

Re-reading raw material on every question is slow, expensive, and un-citable.
Compiling once means every later answer starts from pre-vetted, linked,
traceable notes — and any claim can be walked back to its source on demand.

## Details

- The Raw layer is preserved, not summarized in place; compilation happens in
  new `Wiki/` notes.
- Every compiled note carries `sources` + `source_count`, so the linter can
  prove the wiki never drifts from its evidence.
- A source flips to `Processed: true` only when a compiled note covers it —
  which makes "what haven't we compiled yet?" a script question, not a memory
  question.

## Related

- [[omnia-vault]]
- [[three-layer-query-rule]]
