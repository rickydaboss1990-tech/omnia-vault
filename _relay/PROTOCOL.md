# The Relay Protocol — Claude Code ⇄ Codex with zero copy-paste

Two different coding agents work this project. They never share a chat window,
but they share three things that live in this repo:

1. **The baton** — [`STATE.md`](STATE.md): a short, always-current statement of
   where the work stands. The ONLY file an agent must read to pick up the work.
2. **The history** — [`HISTORY.md`](HISTORY.md): stamped, newest-first handoff
   entries (who, when, at which commit, what happened).
3. **Git** — every handoff sits on a commit, so "what changed" is always
   diffable and nothing depends on anyone's chat scrollback.

Everything else (the Wiki, the code graphs, the chat archive) is shared memory
both agents already read the same way. The relay is only the *baton pass*.

## The two moves

### CATCH UP (start of any session, either agent)

1. Read `_relay/STATE.md` top to bottom.
2. Run `python scripts/relay_tool.py status` — it warns if commits landed
   *after* the last handoff (a stale baton).
3. Run `git log --oneline -10` for the recent trail.
4. If more depth is needed: newest `Wiki/Logs/` note → project note's Status +
   Next Steps. Do **not** re-read raw sources or sweep the codebase to resume.
5. Say back, in a few sentences, where things stand and what you'll do next.
   Then work.

### HAND OFF (end of any session that changed anything)

1. Edit `_relay/STATE.md` — rewrite the sections (they describe the PRESENT,
   not a diff): `Now`, `Just landed`, `Next`, `Open questions`, `Watch out`.
   Write for the *other* agent: no chat references ("as discussed above"),
   no session-local shorthand, absolute honesty about what is unfinished.
2. Stamp it:
   `python scripts/relay_tool.py stamp --agent <claude|codex> --summary "<one paragraph>"`
3. Run the maintenance gate (see `AGENTS.md`), then **commit** — the baton
   travels with the commit.

## Rules

- **The baton describes state, not effort.** "Auth middleware works, tests
  green, refresh-token path untested" beats a play-by-play of the session.
- **Never hand off a lie.** If the gate fails or tests are red, STATE.md says
  so in `Watch out`.
- **One baton.** Agents don't keep private TODO files; anything worth
  remembering goes in STATE.md (short-term) or the Wiki (long-term).
- **Stale baton = read git first.** If `relay_tool.py status` warns, trust
  `git log` + the newest `Wiki/Logs/` note over STATE.md, then fix STATE.md.
- **Session transcripts are local memory.** `python scripts/import_chats.py`
  archives both agents' transcripts (Claude Code *and* Codex) into `chats/`
  — gitignored, searchable, never committed.

## Why this works for both agents

- **Claude Code** loads `CLAUDE.md`, which wires `catchup` / `save` / `handoff`
  to this protocol (plus `/catchup`, `/save`, `/handoff` commands).
- **Codex** loads `AGENTS.md`, which states the same two moves as hard rules.
- Both write the same file with the same stamp tool, so neither cares which
  agent came before.

## The two modes

| Mode | What | Where |
|---|---|---|
| **Async — the baton** (this file's protocol) | agents alternate across sessions; state travels via STATE.md + git | `_relay/STATE.md`, `_relay/HISTORY.md` |
| **Sync — sparring** | both models in one session: the driver plans/builds, the rival attacks the plan (read-only rounds) and grades the diff | `_relay/spar/` — `PLAN.md`, `SPAR-LOG.md`, machine-local `state.json`, finished spars in `archive/`; driven by `scripts/spar_tool.py` + the `sparring` skill |

A spar in flight is baton-visible: STATE.md's **Now**/**Watch out** name it,
and `python scripts/spar_tool.py status` lets any session resume the loop.
