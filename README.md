<div align="center">

<img src=".github/assets/cortex-banner.svg" alt="Cortex — one brain, two agents, zero copy-paste" width="100%"/>

<br/><br/>

**Clone a brain, not a boilerplate.**

Cortex is a plug-and-play project OS: an Obsidian **LLM Wiki**, **Graphify code graphs**,
a **video-watching pipeline**, and a **relay** that lets **Claude Code and Codex work the
same project — alternating freely, with zero copy-paste.**

<br/>

[![License: MIT](https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-ready-7dd3fc?style=flat-square)](CLAUDE.md)
[![Codex](https://img.shields.io/badge/Codex-ready-86efac?style=flat-square)](AGENTS.md)
[![Obsidian](https://img.shields.io/badge/Obsidian-vault-a78bfa?style=flat-square)](https://obsidian.md)
[![Tooling](https://img.shields.io/badge/python-stdlib_only-fbbf24?style=flat-square)](scripts/)

<br/>

[**Get started in 5 minutes →**](GETTING-STARTED.md) ·
[Operating guide](VAULT-GUIDE.md) ·
[The relay protocol](_relay/PROTOCOL.md) ·
[Every command](Schema/command-reference.md)

</div>

---

## Why this exists

AI coding agents are brilliant and amnesiac. Every session starts from zero: you re-explain
the project, re-paste the context, re-open the same twenty files. Switch from Claude Code to
Codex and it's worse — two brilliant agents, two separate amnesias, and you're the
copy-paste middleware between them.

Cortex fixes the memory problem at the repository level. **The repo *is* the brain.**
Everything an agent needs to be instantly useful — knowledge, code understanding, session
state — lives in files, is validated by deterministic tooling, and travels with `git`.

| Memory | What it holds | Where it lives |
|---|---|---|
| 🧠 **Knowledge** | every meeting, doc, video, and decision — compiled into short, linked, *source-traceable* notes | `Wiki/` + `Raw/Sources/` |
| 🕸️ **Code understanding** | a queryable knowledge graph per repo (communities, god nodes, impact analysis) | `graphify/` |
| 🏃 **Session state** | the baton: what just landed, what's next, what to watch out for | `_relay/STATE.md` |

Open the folder in **Obsidian** and the whole brain becomes a navigable constellation —
notes, code nodes, and sources, all one graph.

---

## The relay — use both agents like one agent

Claude Code plans beautifully. Codex grinds through execution and debugging. Cortex lets
you use each for what it's best at, **on the same project, alternately, without
re-explaining anything**:

```mermaid
sequenceDiagram
    participant C as Claude Code
    participant R as _relay/STATE.md (the baton)
    participant X as Codex
    C->>R: /handoff — rewrite baton, stamp, commit
    Note over R: Now · Just landed · Next<br/>Open questions · Watch out
    X->>R: "catch up" — reads baton + git log
    X->>X: implements, tests, debugs
    X->>R: rewrite baton, stamp (--agent codex), commit
    C->>R: /catchup — picks up exactly where Codex stopped
```

- Both agents read the same rules (`CLAUDE.md` for Claude, `AGENTS.md` for Codex) and
  write the same baton.
- `python scripts/relay_tool.py status` detects a **stale baton** (commits after the last
  handoff) so nobody trusts old state.
- Both agents' chat transcripts are archived locally (`python scripts/import_chats.py`)
  — searchable memory, secrets redacted, never committed.

> No copy-paste. No "let me summarize the conversation so far." Open the other tool and say
> *"catch up."*

---

## The layered memory — answers stay fast, cheap, and cited

Every question routes through the cheapest layer that can answer it:

```mermaid
flowchart LR
    Q([question]) --> G["1 · Code graph<br/><code>graphify query</code>"]
    G -->|not enough| W["2 · Wiki catalog<br/><code>search-catalog</code>"]
    W -->|not enough| R["3 · Raw files<br/>one file, narrowly"]
    style G fill:#0ea5e9,color:#fff,stroke:none
    style W fill:#8b5cf6,color:#fff,stroke:none
    style R fill:#f59e0b,color:#fff,stroke:none
```

No repo sweeps. No transcript re-reads. Claims trace back to sources, and a linter
enforces it: every compiled note must name the raw files that support it
(`sources` / `source_count`), tags must match folders, and a **maintenance gate**
(`doctor → build → lint → source-lint → audit`) blocks bad commits — including secrets
and machine-local paths.

---

## It watches videos, too

Point it at a meeting recording, a screen capture, **or a YouTube/TikTok URL**:

```
/video standup-2026-03-14.mkv
/video https://youtube.com/watch?v=...   ← reference videos for design/research
```

Under the hood: [`crv`](https://pypi.org/project/claude-real-video/) extracts scene-aware
deduplicated keyframes + a Whisper transcript, the agent **correlates what's shown with
what's said** frame-by-frame, redacts secrets, and compiles the result into linked notes
with curated screenshots. Your standups become queryable knowledge.

---

## 60-second start

```bash
git clone https://github.com/gavishap/cortex.git my-project
cd my-project
claude        # or: codex
```

**New project?**

```
/setup My Product Name
```

**Existing project?** Drop your repos / recordings / docs into the folder, then:

```
/import
```

Then live the loop:

```
/catchup   →   work: ask · ingest · build · design   →   /save
```

Full walkthrough (+ optional tooling like `graphify`, `crv`, `ffmpeg`):
[GETTING-STARTED.md](GETTING-STARTED.md)

---

## What's in the box

```
├─ Wiki/            compiled knowledge — topics · concepts · entities · projects · logs
├─ Raw/Sources/     captured material, verbatim, source-of-truth for every claim
├─ graphify/        committed code-graph snapshots per tracked repo
├─ _relay/          the baton (STATE.md) + handoff history + protocol
├─ Schema/          frontmatter contracts · naming · lint rules · command reference
├─ _templates/      six note templates (source/topic/concept/entity/project/log)
├─ scripts/         deterministic tooling — python stdlib only, no dependencies
├─ .claude/
│  ├─ skills/       18 skills, ready on clone (see below)
│  └─ commands/     12 slash commands (/setup /import /catchup /save /handoff ...)
├─ CLAUDE.md        Claude Code wiring        AGENTS.md   Codex + any-agent rules
└─ VAULT-GUIDE.md   the full operating guide
```

### The skill arsenal

| Ready on clone (vendored) | What it does |
|---|---|
| `graphify` | any folder / repo / paper / video → queryable knowledge graph (`query` · `explain` · `path` · `affected`) |
| `video-ingest` | recordings & video URLs → transcript ⇄ frames, correlated, compiled |
| `import-project` | adopt an existing codebase + raw files into the vault |
| `relay` | the Claude ⇄ Codex baton pass |
| `project-context-query` | the 3-layer answer engine |
| `llm-wiki-ingest / query / lint / maintain` | the LLM Wiki core loops |
| `taste` | anti-slop frontend design ([Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), MIT) |
| `ui-ux-pro-max` | searchable design intelligence: 79 styles · 192 palettes · 74 font pairs · 119 UX rules ([nextlevelbuilder](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), MIT) |
| `obsidian-markdown / bases / canvas / cli / defuddle` | first-class Obsidian editing ([kepano/obsidian-skills](https://github.com/kepano/obsidian-skills), MIT) |
| `humanizer` + `stakeholder-update-writing` | outward-facing prose that doesn't read like a bot |

| One command away | How |
|---|---|
| **impeccable** — 23 design commands (`polish`, `animate`, `critique`, …) | `/design-setup` |
| **Anthropic document skills** — Word · PDF · PowerPoint · Excel deliverables | `/docs-setup` |

### The commands

| Command | Does |
|---|---|
| `/setup` · `/import` | initialize a new project · adopt an existing one |
| `/catchup` · `/save` · `/handoff` | the daily loop + the agent switch |
| `/ingest` · `/video` | any source → knowledge · any recording/URL → knowledge |
| `/wiki` · `/graph` · `/gate` | layered answers · code graphs · the quality gate |
| `/design-setup` · `/docs-setup` | design stack · document stack |

---

## FAQ

**Do I need both agents?** No — everything works with just Claude Code *or* just Codex.
The relay simply means you never lose state if you add the second one.

**Do I need Obsidian?** No, but you want it: the vault is plain Markdown that happens to
render as a beautiful navigable graph.

**What are the actual dependencies?** Python 3.9+ and git. That's it — every script is
standard-library only. `graphify` (code graphs), `crv` + `ffmpeg` (video), and Node
(web clipping) are optional, checked by `python scripts/setup_vault.py --check`, and each
unlocks a feature when present.

**Is my data safe in here?** The vault ships empty (one self-documenting demo you can
prune with one command). The audit gate blocks secrets and machine-local paths from ever
being committed, repos you import stay gitignored, and chat archives never leave your
machine.

**Where did this design come from?** It's the extraction of a production consulting
system — battle-tested on a real engagement (multi-repo codebase, recorded meetings,
diagrams, evolving requirements), then scrubbed to a clean template.

---

<div align="center">

Built on the shoulders of [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills),
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill),
[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill),
[graphifyy](https://pypi.org/project/graphifyy/) and
[claude-real-video](https://pypi.org/project/claude-real-video/) —
see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

**MIT licensed. Clone it, gut it, ship with it.**

⭐ if your projects deserve a brain.

</div>
