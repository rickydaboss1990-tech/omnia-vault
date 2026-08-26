# CLAUDE.md — Cortex Vault

This folder is a **Cortex vault**: an Obsidian LLM Wiki + code knowledge graphs
+ a two-agent relay. It is the project's memory — everything you need is inside
it. Read [AGENTS.md](AGENTS.md) (hard rules) and [VAULT-GUIDE.md](VAULT-GUIDE.md)
(full operating guide) before working here.

## Session commands

**catchup** — when the user says "catch up", "resume", "where were we", or at
the start of a work session: follow the `relay` skill's catch-up move — read
`_relay/STATE.md`, run `python scripts/relay_tool.py status`,
`git log --oneline -10`, then summarize state + next steps in a few sentences.
Never re-read Raw sources or sweep code to resume. (Also: `/catchup`.)

**save** — when the user says "save", "wrap up", or the session made meaningful
changes: (1) archive memory — `python scripts/import_chats.py` (Claude + Codex
transcripts → gitignored `chats/`) and `python scripts/sync_graphs.py` (if
repos are tracked); (2) log — `python scripts/wiki_tool.py log --title "..."
--details "..."` plus a `Wiki/Logs/` note if substantial; (3) run the
maintenance gate; (4) relay handoff — rewrite `_relay/STATE.md` and stamp with
`python scripts/relay_tool.py stamp --agent claude --summary "..."`; (5) commit.
(Also: `/save`.)

**handoff** — when the user is switching to Codex mid-stream: the lighter pass —
STATE.md rewrite + stamp + gate + commit. (Also: `/handoff`.)

## 3-Layer Query Rule (any question about the project or its code)

1. **Graph first:** `graphify query "<question>" --graph graphify/<repo>/graph.json`
   (or from inside a repo, against its `graphify-out/graph.json`). Also
   `graphify explain`, `graphify path`, `graphify affected`, and the
   `graphify/<repo>/_COMMUNITY_*.md` notes.
2. **Wiki second:** `python scripts/wiki_tool.py search-catalog --query "<topic>"`
   → open the top 1–3 compiled notes.
3. **Raw last:** the specific Raw source a note cites, or the specific repo
   files you will edit. Never sweep.

Full traversal recipe: `.claude/skills/project-context-query/SKILL.md`.

## Workflows → skills

| Task | Skill |
|---|---|
| Ingest any source (doc, URL, text, diagram) | `llm-wiki-ingest` (+ `defuddle` for web pages) |
| Watch/ingest a recording or YouTube/TikTok URL | `video-ingest` |
| Adopt an existing project (repos, media, docs) | `import-project` |
| Answer questions | `project-context-query` / `llm-wiki-query` |
| Validate / fix notes | `llm-wiki-lint` |
| Commit hygiene + routine upkeep | `llm-wiki-maintain` |
| Agent handoff (⇄ Codex) | `relay` |
| Code knowledge graphs | `graphify` |
| Obsidian file editing | `obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli` |
| Outward-facing updates/reports | `stakeholder-update-writing` (+ `humanizer`) |
| Frontend design work | `taste`, `ui-ux-pro-max` (see `/design-setup`) |

Slash commands: `/setup`, `/import`, `/catchup`, `/save`, `/handoff`,
`/ingest`, `/video`, `/graph`, `/wiki`, `/gate`, `/design-setup`,
`/docs-setup`.

## Memory automation

- **Chat archive** — `python scripts/import_chats.py` converts BOTH agents'
  session transcripts (Claude Code and Codex) into readable Markdown under
  `chats/` — gitignored local memory, secrets redacted on import, never
  committed. Run at `save`.
- **Code-graph freshness** — install `graphify hook install` inside each
  tracked repo once; `python scripts/sync_graphs.py` then keeps the committed
  `graphify/<repo>/` snapshots current. Runs at `save`.

## Hard rules (the short list)

- Compiled knowledge lives in `Wiki/`, captured material in `Raw/Sources/` —
  never blur the layers; never edit Raw sources to "improve" them.
- Every compiled note: exactly one type tag matching its folder, accurate
  `sources` + `source_count`, `[[wikilinks]]`. Never invent citations.
- **Maintenance gate before every commit:** `doctor` → `build` → `lint` →
  `source-lint` → `python scripts/audit_public.py` (after ingests also
  `source-scan --update --accept-covered`). All must pass.
- Never commit secrets or machine-local absolute paths (`audit_public.py`
  gates this). Never commit tracked work repos into the vault (gitignore
  them), and never commit vault tooling into a work repo.
- Never hand-edit generated files (`Wiki/catalog.jsonl`, `index.md` files,
  `Schema/source-manifest.jsonl`, `graphify/`).

## Machine notes

- Use `python` on Windows, `python3` on macOS/Linux.
- Before `graphify`/`crv` on Windows PowerShell: `$env:PYTHONUTF8=1`.
- `crv` needs `ffmpeg`/`ffprobe` reachable (prepend to PATH if needed).
- `python scripts/setup_vault.py --check` verifies optional tooling.
