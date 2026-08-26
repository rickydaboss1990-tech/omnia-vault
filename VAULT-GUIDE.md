# VAULT-GUIDE.md — Cortex Operating Guide

> **Purpose:** hand this single file to a new AI agent (or human) so it can
> understand what this vault is, how it's organized, and exactly how to work
> with it — then start being useful immediately.
>
> **Companion files:** [AGENTS.md](AGENTS.md) (the hard rules),
> [CLAUDE.md](CLAUDE.md) (Claude Code wiring),
> [Schema/command-reference.md](Schema/command-reference.md) (every command),
> [_relay/PROTOCOL.md](_relay/PROTOCOL.md) (the agent handoff). This guide is
> the narrative that ties them together.

---

## 1. TL;DR for a new agent

1. This is a **Cortex vault**: an Obsidian **LLM Wiki** that separates captured
   source material (`Raw/Sources/`) from compiled, reusable knowledge
   (`Wiki/`), plus **Graphify code graphs** of any tracked repos
   (`graphify/`), plus a **relay baton** (`_relay/STATE.md`) that lets Claude
   Code and Codex trade the work with zero copy-paste.
2. **Start every session at the baton:** read `_relay/STATE.md`, run
   `python scripts/relay_tool.py status`.
3. **To answer a question:** graph → wiki catalog → raw, cheapest first
   (`python scripts/wiki_tool.py search-catalog --query "topic"`).
4. **To add knowledge:** capture verbatim in `Raw/Sources/`, compile into
   short linked `Wiki/` notes, keep `sources`/`source_count` accurate.
5. **Never invent claims or citations.** No source → Open Question, not prose.
6. **Run the maintenance gate before every commit** (Section 8), and **end
   every session by rewriting + stamping the baton** and committing.

---

## 2. What this system is

An **LLM Wiki** is a knowledge system built so agents (and people) answer
questions from short, linked, pre-vetted notes instead of re-reading raw
material every time. Cortex adds two things around it:

- a **code layer** — Graphify knowledge graphs, so questions about tracked
  codebases are answered by graph traversal, not repo sweeps;
- an **agent relay** — a baton file + stamp tool + git, so two different
  coding agents (with different strengths: planning vs execution) can work the
  same project alternately without either losing state.

Three memories, one system:

| Memory | Lives in | Refreshed by |
|---|---|---|
| Knowledge (durable) | `Wiki/` + `Raw/Sources/` | ingest workflows + gate |
| Code understanding | `graphify/<repo>/` | graphify hooks + `sync_graphs.py` |
| Session state (short-term) | `_relay/STATE.md` + `chats/` | relay handoffs + `import_chats.py` |

---

## 3. Directory layout

```
<vault root>/
├─ README.md                 # the product tour (for humans)
├─ GETTING-STARTED.md        # 5-minute setup, both modes
├─ VAULT-GUIDE.md            # this file
├─ AGENTS.md                 # hard rules every agent must follow
├─ CLAUDE.md                 # Claude Code wiring (commands, query rule)
├─ Raw/
│  ├─ Sources/               # cleaned Markdown source material (committed)
│  └─ Files/                 # binary/attachment sources (gitignored except .gitkeep)
├─ Wiki/                     # compiled knowledge (the product)
│  ├─ Topics/  Concepts/  Entities/  Projects/  Logs/
│  ├─ index.md               # generated top-level index
│  ├─ catalog.jsonl          # generated machine-readable catalog (SEARCH THIS)
│  └─ log.md                 # generated change log (via `wiki_tool.py log`)
├─ graphify/                 # committed Graphify snapshots per tracked repo
├─ _relay/                   # the agent-to-agent baton: STATE.md, HISTORY.md, PROTOCOL.md
├─ Schema/                   # contracts: frontmatter, naming, lint, commands, examples
├─ _templates/               # source/concept/topic/entity/project/log templates
├─ scripts/                  # deterministic tooling (python stdlib only) — see §6
├─ .claude/
│  ├─ skills/                # the skill library (works for ANY agent — they're markdown)
│  └─ commands/              # Claude Code slash commands (/setup, /save, ...)
├─ .githooks/pre-commit      # build + lint + source-lint (activate via install_hooks.sh)
├─ assets/                   # committed images (screenshots, diagrams)
├─ chats/                    # BOTH agents' transcript archive (gitignored local memory)
└─ <your repos>/             # tracked code repos (gitignored; only their graphs are committed)
```

**Generated files — never hand-edit:** `Wiki/catalog.jsonl`, `Wiki/index.md`,
every `*/index.md`, `Schema/source-manifest.jsonl`, everything under
`graphify/`. Regenerate with `build`, `source-scan`, `sync_graphs.py`.

---

## 4. The two frontmatter contracts

Full detail in [Schema/frontmatter-schema.md](Schema/frontmatter-schema.md).

**Raw source note** (`Raw/Sources/*.md`):

```yaml
---
Title: ""            # required
Author: ""
Reference: ""        # required — URL, filename, or identifier of the original
ContentType:
  - "markdown"
Created: YYYY-MM-DD   # required
Processed: false      # flips to true once a compiled note covers it
tags:
  - "source"          # required
---
```

**Compiled Wiki note** (`Wiki/**/*.md`):

```yaml
---
tags:
  - "concept"         # EXACTLY ONE of: topic | concept | entity | project | log
topics: []
status: seed          # seed | growing | evergreen
created: YYYY-MM-DD
updated: YYYY-MM-DD   # bump on every meaningful edit
sources: []           # vault-relative paths under Raw/Sources/
source_count: 0       # MUST equal len(sources)
aliases: []
---
```

Two invariants the linter enforces: the tag must match the folder
(`concept` → `Wiki/Concepts/`, etc.), and `source_count` must equal the number
of `sources`, each pointing at a real file under `Raw/Sources/`.

---

## 5. Conventions

- **Filenames:** lowercase kebab-case, no spaces (`priority-table.md`).
- **One idea per note.** Split notes that grow past a single idea.
- **Link liberally** with `[[wikilinks]]`; an unresolved link marks a note
  worth writing later.
- **Dates** are `YYYY-MM-DD`; bump `updated` on meaningful edits.
- **Every compiled note should link back to ≥1 Raw source** (lint warns
  otherwise; brand-new seed notes may briefly have none).
- **Code ⇄ knowledge bridges are curated:** compiled notes carry a
  `## Code Graph` section with **path-qualified** links like
  `[[graphify/<repo>/_COMMUNITY_...]]` (community names collide across repos).

---

## 6. The deterministic tooling

All stdlib-only, all run from the vault root. Full table:
[Schema/command-reference.md](Schema/command-reference.md).

| Script | Does |
|---|---|
| `wiki_tool.py` | `doctor` health check · `build` catalog/indexes · `lint` compiled notes · `source-scan/-lint/-delta/-coverage` raw layer · `search-catalog` · `log` |
| `audit_public.py` | fails on secrets, machine-local absolute paths, tracked Obsidian plugin state |
| `setup_vault.py` | `--name` seed a new project · `--inventory` scan for importable content · `--gitignore-repos` · `--prune-demo` · `--check` tooling |
| `relay_tool.py` | `status` baton + staleness check · `stamp` handoff stamp + history |
| `import_chats.py` | archive Claude Code **and** Codex transcripts → `chats/` (gitignored, redacted) |
| `sync_graphs.py` | AST-rebuild + copy fresh `graph.json` snapshots into `graphify/<repo>/` |
| `install_hooks.sh` | activate the pre-commit gate (`sh scripts/install_hooks.sh`) |

---

## 7. Installed capabilities

**Workflow skills** (`.claude/skills/` — plain Markdown, readable by any
agent): `llm-wiki-ingest`, `llm-wiki-query`, `llm-wiki-lint`,
`llm-wiki-maintain`, `project-context-query`, `video-ingest`,
`import-project`, `relay`, `stakeholder-update-writing`.

**Obsidian editing skills** (from
[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills), MIT):
`obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`,
`defuddle` (web page → clean markdown; needs `npm i -g defuddle` on first use).

**Design skills:** `taste`
([Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), MIT) and
`ui-ux-pro-max`
([nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill),
MIT) are vendored; the `impeccable` plugin and Anthropic `document-skills`
install in one command each — see `/design-setup` and `/docs-setup`.

**Prose quality:** `humanizer` (vendored, MIT) strips AI-writing tells from
outward-facing text.

**Graphify code graphs** (`graphify/`, generated by the `graphifyy` pip
package + the vendored `graphify` skill): one `.md` note per code node with
`[[wikilinks]]`, `_COMMUNITY_*.md` cluster overviews, a `graph.json` snapshot
per repo, and CLI query tools (`query` / `explain` / `path` / `affected`).
In Obsidian, filter the graph view with `path:graphify` to isolate code nodes.

**Video understanding** (`crv`, the `claude-real-video` pip package): local
files or URLs (YouTube/TikTok/Instagram) → scene-aware deduplicated keyframes +
Whisper transcript, which the `video-ingest` skill correlates and compiles.

---

## 8. How to interact with it

### Answer a question
Graph (for code) → `search-catalog` → open top 1–3 compiled notes → answer,
citing notes (and Raw sources when it depends on source material). Only open
`Raw/Sources/` when compiled notes are insufficient.

### Ingest a new source
Capture cleaned Markdown in `Raw/Sources/` (template:
`_templates/source-note.md`; images → transcribe to text, file → `assets/`) →
`search-catalog` for related notes → create/enrich focused `Wiki/` notes
(right folder + tag, accurate `sources`/`source_count`, wikilinks) → gate →
commit (+ log note if substantial). Recordings: the `video-ingest` skill.

### Maintenance gate (before every meaningful commit)
```bash
python scripts/wiki_tool.py doctor
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-lint
python scripts/audit_public.py
```
After a source ingest, also:
```bash
python scripts/wiki_tool.py source-scan --update --accept-covered
python scripts/wiki_tool.py source-lint
```
All must pass (exit 0). Optionally activate the pre-commit hook once:
`sh scripts/install_hooks.sh`.

### End of session
Follow `save` in [CLAUDE.md](CLAUDE.md) / the relay rules in
[AGENTS.md](AGENTS.md): archive chats, refresh graphs, log, gate, rewrite +
stamp the baton, commit.

---

## 9. Environment specifics & gotchas

- **`python` on Windows, `python3` on macOS/Linux.** The scripts need only the
  standard library.
- **CRLF warnings on commit are normal on Windows** — Git normalizing line
  endings. Harmless.
- **The Obsidian graph does NOT draw `sources:` frontmatter links** — only
  `[[wikilinks]]`. Raw sources look "orphaned" in the graph view even though
  the catalog/manifest fully connects them (`source-coverage` proves it). Add a
  body wikilink from a log/compiled note if graph cosmetics matter.
- **Obsidian may auto-create empty stub `.md` files** at the vault root from
  unresolved template `[[placeholders]]`. Delete any zero-byte stray:
  `Get-ChildItem -Recurse -Filter *.md | Where-Object Length -eq 0`.
- **`Raw/Files/*` is gitignored** — committable images go in `assets/`,
  embedded as `![[name.png]]`.
- **`audit_public.py` fails on machine-local home paths** in committed text —
  refer to user-home locations generically in notes.
- **The giant hub node in each `graphify/` cluster is `graph.canvas`** — an
  export artifact, not code. Filter it out with `-file:graph.canvas` in the
  graph view. If a filtered graph looks empty, disable "Orphans"/"Existing
  files only" in graph settings.
- **Whisper mishears domain terms consistently** — when a transcript word looks
  wrong everywhere, flag it as an Open Question instead of propagating it.
- **PowerShell + graphify/crv:** set `$env:PYTHONUTF8=1` first (cosmetic
  Unicode crash on final print otherwise).

---

## Appendix — bootstrap prompt for a fresh agent on this vault

Paste this to bootstrap an agent that knows nothing:

```text
I'm continuing work in this Cortex vault (the folder containing this file).
The vault IS your memory — everything you need is inside it. In order:

1. ORIENT — read CLAUDE.md (or AGENTS.md if you're not Claude), then skim
   VAULT-GUIDE.md. Don't scan the whole vault.
2. CATCH UP — read _relay/STATE.md, run `python scripts/relay_tool.py status`
   and `git log --oneline -10`, then summarize where things stand + next steps.
3. VERIFY TOOLING — `python scripts/wiki_tool.py doctor` and
   `python scripts/setup_vault.py --check`.
4. WORK — questions via the 3-layer rule (graph → wiki → raw); new material
   via the ingest skills; before every commit run the maintenance gate.
5. HAND OFF — before you finish: rewrite _relay/STATE.md, stamp it
   (`python scripts/relay_tool.py stamp --agent <you> --summary "..."`),
   gate, commit.
```
