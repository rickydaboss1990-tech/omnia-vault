---
description: Quick handoff to the other agent (Codex ⇄ Claude) — baton + stamp + commit, no full save
argument-hint: [optional: note for the next agent]
---

The user is switching agents. Do a fast, honest baton pass per the `relay`
skill:

1. Rewrite `_relay/STATE.md` — Now / Just landed / Next / Open questions /
   Watch out — written for a stranger, present-tense state, no chat shorthand.
   Include this note from the user if given: $ARGUMENTS
2. `python scripts/relay_tool.py stamp --agent claude --summary "<one paragraph>"`
3. Run the maintenance gate; if something is red and the user wants to hand off
   anyway, say so loudly in **Watch out** rather than blocking.
4. Commit (baton + any work) with a clear message.
5. Confirm to the user: the other agent should open this folder and say
   "catch up" (Codex reads AGENTS.md → same protocol; Claude runs /catchup).
