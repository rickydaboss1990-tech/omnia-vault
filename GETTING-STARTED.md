# Getting Started with Omnia Vault

Five minutes from clone to a working project brain. Two paths — pick yours.

## 0. Prerequisites

| Need | Required? | Why |
|---|---|---|
| Python 3.9+ | **Yes** | all vault tooling (stdlib only — no pip installs needed) |
| Git | **Yes** | history, the relay, the gate hook |
| [Claude Code](https://claude.com/claude-code) and/or [Codex](https://openai.com/codex) | **Yes** (either or both) | the agents that drive the system |
| [Obsidian](https://obsidian.md) | Recommended | browsing the vault + graph view (the system works without it) |
| `pip install graphifyy` | Optional | code knowledge graphs (`graphify` CLI) |
| `pip install claude-real-video` + [ffmpeg](https://ffmpeg.org) | Optional | video/audio ingest (`crv` CLI) |
| Node.js | Optional | `defuddle` web clipping, `npx`-installed extras |

| `npm i -g @openai/codex` + `codex login` | Optional | the sparring loop's rival reviewer/builder (`/spar`) — the Codex desktop app bundles the CLI too |

Check what you have any time — and let the vault install the missing pieces:

```bash
python scripts/setup_vault.py --check
```

```bash
python scripts/setup_vault.py --install
```

(`--install` handles the pip/npm/winget pieces itself and prints exact
commands for anything it can't do, like `codex login`.)

## 1. Clone it

```bash
git clone https://github.com/gavishap/omnia-vault.git my-project
cd my-project
```

> Cloning for a fresh start? Point the repo at your own remote (or
> `rm -rf .git && git init`) so your project history is yours.

Open the folder in **Claude Code** (`claude`) or **Codex** (`codex`) — both
find their instructions automatically (`CLAUDE.md` / `AGENTS.md`). Open the
same folder in **Obsidian** as a vault to browse it visually.

## 2A. Path A — brand-new project

In Claude Code:

```
/setup My Product Name
```

(or tell Codex: *"read AGENTS.md, then set up a new project called My Product
Name using scripts/setup_vault.py"*)

That seeds your project + topic notes, checks tooling, runs the maintenance
gate, stamps the relay baton, and commits. Then start feeding it:

```
/ingest <a doc, URL, or pasted notes>
/video <a meeting recording or YouTube/TikTok URL>
```

## 2B. Path B — adopt an existing project

Drop what you already have into the vault root — code repo folders, meeting
recordings, docs — then:

```
/import
```

The agent inventories everything (`_relay/IMPORT-INVENTORY.md`), confirms with
you what matters, gitignores the repos, builds a knowledge graph per repo,
ingests the documents and recordings, and wires it all into linked notes.

## 3. The daily loop

```
/catchup     ← start of any session (reads the baton, never re-reads the world)
  ... work: ask, ingest, build, design ...
/save        ← end of session (archive, log, gate, stamp baton, commit)
```

**Switching agents mid-stream?** `/handoff` in Claude Code, then open the same
folder in Codex and say *"catch up"* — it reads the same baton. No copy-paste,
ever. (And back again: Codex stamps the baton per AGENTS.md; `/catchup` in
Claude Code picks it up.)

**Building something high-stakes?** `/spar` first — Codex adversarially
attacks the locked plan in bounded read-only rounds, then one model builds and
the other grades the diff, and the whole argument gets compiled into the wiki.

**Planning a whole project?** `/roadmap` builds the living plan (phases, exit
criteria, toolbox), and from then on `/intel <any YouTube link or recording>`
answers the only question that matters about new content: *does this change
our plan?* — ranked items, an honest INCORPORATE/WATCHLIST/PASS verdict, and
user-gated adoption + tool installs.

## 4. Asking questions

```
/wiki how does the auth flow work?
```

Questions route through the layered memory — code graph first, compiled wiki
second, raw files last and narrowly. That's what keeps answers fast, cited,
and cheap.

## 5. Optional power-ups (one command each)

| Want | Run |
|---|---|
| Frontend design stack (Taste + UI/UX Pro Max are already vendored; adds impeccable's 23 commands) | `/design-setup` |
| Word / PDF / PowerPoint / Excel deliverables (official Anthropic skills) | `/docs-setup` |
| Pre-commit gate that blocks bad commits automatically | `sh scripts/install_hooks.sh` |
| Auto-rebuilding code graphs on every repo commit | `graphify hook install` (inside each repo) |

## 6. Learn the system

- The demo content (`Wiki/Topics/omnia-vault.md` and friends) is a worked example
  of the whole loop — prune it once you have real content:
  `python scripts/setup_vault.py --prune-demo`
- [VAULT-GUIDE.md](VAULT-GUIDE.md) — the full operating guide
- [_relay/PROTOCOL.md](_relay/PROTOCOL.md) — how the two-agent relay works
- [Schema/command-reference.md](Schema/command-reference.md) — every command
- [Schema/workflow-examples.md](Schema/workflow-examples.md) — worked examples
