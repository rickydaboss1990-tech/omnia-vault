---
description: Make the models argue before you build — Codex attacks the plan in bounded read-only rounds, then one builds and the other grades the diff
argument-hint: <what to plan/build> [rounds=N]
---

Run the `sparring` skill on: $ARGUMENTS

The short version of what that means:

1. **SCOUT** — recon from the vault's layered memory (relay status → graph →
   wiki catalog → narrow raw reads), then present ONE batched Assumptions
   Ledger with sources. Start state: `python scripts/spar_tool.py start --task "..."`.
2. **LOCK** — decision map; load-bearing questions one at a time (each with
   why-it-matters, a committed recommendation, and the cost of guessing
   wrong); cosmetic ones batched; "lock all recommendations" escape hatch.
   Write the locked plan to `_relay/spar/PLAN.md`.
3. **SPAR** — resolve the codex CLI, echo the reviewer model, then bounded
   read-only review rounds (`exec -s read-only` → thread id →
   `exec resume ... -c sandbox_mode="read-only"`), recording every round via
   `spar_tool.py record-round` and arbitrating every FATAL/MAJOR finding
   (accept or rebut, logged via `respond`). APPROVED → user signs off;
   round cap → honest deadlock report.
4. **SHIP** — user picks the builder; the rival model grades the result
   (Codex builds `-s workspace-write` + Claude reads the full diff and runs
   the proof, or Claude builds + a fresh read-only Codex session
   cross-inspects). Human gate on the diff; driver authors the commit.
5. **Aftermath** — `spar_tool.py finish`, capture the argument as a Raw
   source, compile key decisions into Wiki notes, gate, relay-stamp, commit.

Honor every mechanic in the skill's "Mechanics that will bite you" section
(stdin feeding, resume sandbox forcing, explicit thread ids, 10-minute
timeouts, empty-critique = failed round).
