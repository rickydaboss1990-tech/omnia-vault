# Command Reference

All commands run from the vault root. Use `python` on Windows, `python3` on
macOS/Linux. Every script is deterministic and standard-library only.

## wiki_tool.py

| Command | Mutates | Purpose |
|---------|---------|---------|
| `python scripts/wiki_tool.py doctor` | no | Health check: folders, Python version, catalog, manifest, note counts. Exit 1 on missing folders or unreadable generated files. |
| `python scripts/wiki_tool.py build` | yes | Regenerates `Wiki/catalog.jsonl`, `Wiki/index.md`, and per-folder `index.md` files from compiled notes. |
| `python scripts/wiki_tool.py lint` | no | Validates compiled Wiki notes: one allowed tag, tag/folder match, dates, status, existing source links, `source_count` accuracy. Exit 1 on errors. |
| `python scripts/wiki_tool.py source-scan` | no | Lists Raw sources with processed/coverage state (dry run). |
| `python scripts/wiki_tool.py source-scan --update` | yes | Also rewrites `Schema/source-manifest.jsonl`. |
| `python scripts/wiki_tool.py source-scan --update --accept-covered` | yes | Also flips `Processed: true` in source frontmatter for sources now covered by Wiki notes. |
| `python scripts/wiki_tool.py source-lint` | no | Validates source frontmatter and fails if a source is marked processed without Wiki coverage. |
| `python scripts/wiki_tool.py source-delta` | no | Shows Raw sources missing from the manifest and orphaned manifest entries. |
| `python scripts/wiki_tool.py source-coverage` | no | Shows which Raw sources are covered by which compiled notes. |
| `python scripts/wiki_tool.py search-catalog --query "text"` | no | Searches compiled notes via the catalog (title, path, tag, topics, body). **Do this before opening Raw.** |
| `python scripts/wiki_tool.py log --title "t" --details "d"` | yes | Appends a dated entry to `Wiki/log.md`. |

## audit_public.py

| Command | Purpose |
|---------|---------|
| `python scripts/audit_public.py` | Fails (exit 1) on obvious secrets, machine-local absolute paths, and tracked Obsidian plugin/cache/workspace state. |

## setup_vault.py (bootstrap)

| Command | Purpose |
|---------|---------|
| `python scripts/setup_vault.py --name "My Project" [--topic "domain"]` | Seed project + topic notes, refresh the baton, rebuild the catalog. |
| `python scripts/setup_vault.py --inventory` | Scan the vault root for repos / media / documents → `_relay/IMPORT-INVENTORY.md` (existing-project import). |
| `python scripts/setup_vault.py --gitignore-repos` | Append detected repo folders to `.gitignore`. |
| `python scripts/setup_vault.py --prune-demo` | Remove the built-in demo content and rebuild. |
| `python scripts/setup_vault.py --check` | Verify optional tooling (git, graphify, crv, ffmpeg, node, defuddle, codex) with install hints. |
| `python scripts/setup_vault.py --install` | Install what it can (pip: graphifyy, claude-real-video; npm: defuddle; ffmpeg via winget/brew) and print exact commands for the rest. |

## relay_tool.py (agent handoff)

| Command | Purpose |
|---------|---------|
| `python scripts/relay_tool.py status` | Show baton stamp + git HEAD; warns when commits landed after the last handoff (stale baton). |
| `python scripts/relay_tool.py stamp --agent <claude\|codex> --summary "..."` | Stamp `_relay/STATE.md` and prepend the entry to `_relay/HISTORY.md`. Run after rewriting STATE.md's sections. |

## spar_tool.py (cross-model sparring loop)

| Command | Purpose |
|---------|---------|
| `python scripts/spar_tool.py start --task "..." [--rounds 5] [--reviewer codex] [--driver claude] [--archive-active]` | Begin a spar: creates `_relay/spar/{PLAN.md,SPAR-LOG.md,state.json}`. Refuses if one is active unless `--archive-active`. |
| `python scripts/spar_tool.py set-thread --id <id>` | Record the reviewer's session/thread id so any later session can resume the loop. |
| `python scripts/spar_tool.py record-round --critique-file <path>` | Append the critique to SPAR-LOG.md, parse its `VERDICT:` line, bump the round, print `round=N verdict=...` (+ cap/no-verdict flags). Refuses empty critiques. |
| `python scripts/spar_tool.py respond --text "..." \| --file <path>` | Log the driver's arbiter response (what was accepted, what was rebutted, why). |
| `python scripts/spar_tool.py status` | Loop state: phase, round, verdict, thread, files, cap warnings. |
| `python scripts/spar_tool.py finish --outcome approved\|deadlock\|abandoned [--summary "..."]` | Close the spar and archive PLAN + LOG to `_relay/spar/archive/<date>-<slug>/`. |

Reviewer invocation mechanics (stdin feeding, resume sandbox forcing, thread
ids, timeouts) live in `.claude/skills/sparring/SKILL.md`.

## plan_tool.py (war-room — the living plan)

| Command | Purpose |
|---------|---------|
| `python scripts/plan_tool.py init --name "..." [--vision "..."] [--phases "A,B,C"]` | Scaffold `Plan/` — ROADMAP.md, one file per phase, intel/, TOOLBOX.md. Refuses if already initialized. |
| `python scripts/plan_tool.py context` | Compact plan digest (vision, phase statuses, active phase's open deliverables, toolbox, recent intel verdicts). **Run before triaging any new video/meeting.** |
| `python scripts/plan_tool.py new-intel --title "..." --source "<url-or-path>"` | Scaffold a dated intel brief in `Plan/intel/` with the ranking table + `INTEL VERDICT` contract. |
| `python scripts/plan_tool.py status` | Plan health: phases done/active, deliverables checked, briefs missing verdicts, stale `trialing` tools. |

The triage judgment (ranking rubric, incorporation gates, tool-install rules)
lives in `.claude/skills/war-room/SKILL.md`.

## Memory automation

| Command | Mutates | Purpose |
|---------|---------|---------|
| `python scripts/import_chats.py` | yes (local only) | Archive **both** agents' transcripts for this vault — Claude Code (`~/.claude/projects/<slug>`) and Codex (`~/.codex/sessions`, matched by cwd) — into gitignored `chats/code/` and `chats/codex/`. Secrets redacted on import. `--claude-only`, `--codex-only`, `--slug <s>`, `--force`. |
| `python scripts/sync_graphs.py` | yes | Auto-detect tracked repos, rebuild each graph (`graphify update`, AST-only), copy fresh `graph.json` + `_GRAPH_REPORT.md` into `graphify/<repo>/`. `--no-rebuild` to copy only; pass repo names to override detection. |
| `graphify hook install` (run **inside** each repo) | — | Install Graphify's post-commit hook so `graphify-out/graph.json` rebuilds on every commit. Re-run after a fresh clone. |

## Graphify (code graphs — needs `pip install graphifyy`)

| Command | Purpose |
|---------|---------|
| `graphify <repo> --obsidian --obsidian-dir graphify/<repo>` | First full build: graph + browsable per-node notes into the vault. |
| `graphify query "<question>" --graph graphify/<repo>/graph.json` | Answer a code question from the graph (Layer 1). |
| `graphify explain "<Node>"` / `path "<A>" "<B>"` / `affected "<X>"` | Node explanation / shortest path / change impact. |
| `graphify update <repo>` | Fast incremental re-extraction (AST-only, no LLM). |

Set `$env:PYTHONUTF8=1` first on Windows PowerShell.

## crv (video ingest — needs `pip install claude-real-video` + ffmpeg)

| Command | Purpose |
|---------|---------|
| `crv "<file-or-URL>" -o <outdir> --lang en --whisper-model small --adaptive --text-anchors --viewer --max-frames 200` | Extract transcript + scene-aware deduplicated keyframes from a local recording **or** a YouTube/TikTok/Instagram URL. Run in the background; see the `video-ingest` skill. |

## Hooks

| Command | Purpose |
|---------|---------|
| `sh scripts/install_hooks.sh` | Sets `core.hooksPath` to `.githooks/` so the full pre-commit gate (doctor + build + lint + source-lint + audit_public) runs on every commit. Optional but recommended. |

## Maintenance Gate

Before every meaningful commit:

```bash
python scripts/wiki_tool.py doctor
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-lint
python scripts/audit_public.py
```

After source ingestion, also:

```bash
python scripts/wiki_tool.py source-scan --update --accept-covered
python scripts/wiki_tool.py source-lint
```
