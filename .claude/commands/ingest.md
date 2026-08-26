---
description: Ingest a source (file, URL, pasted text, doc, diagram) into Raw → Wiki
argument-hint: <path, URL, or description of the source>
---

Ingest this source into the vault: $ARGUMENTS

Route by type, then follow the `llm-wiki-ingest` skill:

- **Video/audio (file or YouTube/TikTok/etc. URL)** → use the `video-ingest`
  skill instead (crv extraction in the background, frames ⇄ transcript).
- **Web page/article URL** → extract clean markdown first (the `defuddle`
  skill), then ingest.
- **PDF / Word / slides** → extract text faithfully; images/diagrams:
  transcribe content to text (that's the Raw source), image file → `assets/`.
- **Pasted text / meeting notes** → clean it up verbatim (no summarizing in
  the Raw layer).

Then: Raw source in `Raw/Sources/<date>-<slug>.md` with full source
frontmatter → `search-catalog` → compile/enrich focused `Wiki/` notes (right
folder + tag, `sources` + `source_count` accurate, wikilinks into the topic +
project) → run the gate incl. `source-scan --update --accept-covered` →
commit, with a log entry if substantial.
