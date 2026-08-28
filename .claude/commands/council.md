---
description: Convene the cross-model council — five seats split between Codex and Claude, blind opinions, cross-bench review, one ruled verdict
argument-hint: <the decision or question, with the options you're weighing>
---

Run the `council` skill on: $ARGUMENTS

The shape of the session:

1. **Frame** — vault context the cheap way (baton, plan digest, catalog), then
   ONE neutral framed question with options, constraints, and the cost of
   being wrong. Prepare the Outsider's stripped version (bare decision, zero
   project context). One clarifying question max if the ask is vague.
2. **Convene all five seats in parallel, blind** — Skeptic (codex, read-only),
   Rebuilder (claude subagent), Maximalist (claude subagent), Outsider
   (codex from an EMPTY directory with `--skip-git-repo-check` —
   mechanically context-free), Operator (codex, read-only). Fresh thread per
   Codex seat; each seat ends with `POSITION: <stance>`. Dead seat →
   relaunch once, then report a four-seat council rather than ghost-write it.
3. **Cross-bench review** — shuffle opinions to A..E, then one fresh Codex
   reviewer + one fresh Claude reviewer each grade the anonymized set
   (strongest, biggest blind spot, what all five missed).
4. **The Chair rules** — Consensus / Dissent / Caught in review / The Chair's
   ruling (one committed answer; siding with a lone dissenter is allowed and
   stated) / First move. Present in chat.
5. **Keep the record** — full session to `_relay/council/<date>-<slug>.md`,
   ripple the ruling into the plan/wiki/baton as warranted, gate, commit.

Honor the sparring skill's Codex mechanics (stdin feeding, `-o` files,
10-minute timeouts, never resume across seats).
