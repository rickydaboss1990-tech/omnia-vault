---
tags:
  - "concept"
topics:
  - "cortex"
status: evergreen
created: 2026-08-26
updated: 2026-08-26
sources:
  - "Raw/Sources/cortex-system-demo.md"
source_count: 1
aliases:
  - "the baton"
  - "agent handoff"
---

# The Relay

Two coding agents — Claude Code and Codex — work the same project by passing a
baton instead of sharing a chat. The baton is `_relay/STATE.md`: an
always-current, present-tense statement of where the work stands (Now / Just
landed / Next / Open questions / Watch out). Ending agents rewrite it, stamp it
(`python scripts/relay_tool.py stamp`), and commit; starting agents read it
first and go.

## Why It Matters

Each agent has different strengths — use one to plan, the other to grind out
execution — without ever re-explaining context or copy-pasting chat history.
State lives in the repo, so it survives closed windows, new machines, and
whichever agent shows up next.

## Details

- `relay_tool.py status` detects a stale baton (commits after the last stamp)
  and says to trust `git log` + the newest log note instead.
- Handoffs travel with commits; `_relay/HISTORY.md` keeps the stamped trail.
- Both agents' chat transcripts are archived locally by
  `python scripts/import_chats.py` (gitignored `chats/`) — searchable memory,
  never committed.
- Full protocol: `_relay/PROTOCOL.md`; agent workflow: the `relay` skill.

## Related

- [[cortex]]
- [[raw-vs-compiled-knowledge]]
