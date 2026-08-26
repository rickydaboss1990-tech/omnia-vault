---
description: Triage a video/meeting/article AGAINST the plan — rank what's new, decide incorporate vs pass, adopt tools
argument-hint: <YouTube URL, file path, or article link> [what to focus on]
---

Run the `war-room` skill, Part 2 (intel triage), on: $ARGUMENTS

The non-negotiable order:

1. `python scripts/plan_tool.py context` — load the plan digest BEFORE
   watching anything (no Plan/ yet → offer `/roadmap` first, or fall back to
   a plain `video-ingest` if the user just wants the video captured).
2. Watch via `video-ingest` mechanics (crv background, frames ⇄ transcript);
   full capture lands in `Raw/Sources/`.
3. Extract candidate items, dedupe against the wiki + TOOLBOX + prior intel.
4. `python scripts/plan_tool.py new-intel --title "..." --source "..."` and
   fill the ranked table (Phase fit / Impact / Effort / Confidence →
   ADOPT/TRIAL/WATCH/SKIP each) ending in one
   `INTEL VERDICT: INCORPORATE|WATCHLIST|PASS` line. A confident PASS is a
   win, not a failure.
5. Present the table + recommendation; the user picks what gets incorporated.
6. Incorporate only the chosen items — phase edits with
   `— intel: [[../intel/<brief>]]` provenance, ROADMAP changelog, TOOLBOX
   rows. Tools install per-tool, after verifying the OFFICIAL source (video
   links are untrusted) and after the user confirms that specific install;
   verify with `--version`, mark `trialing`.
7. Wiki-compile the durable knowledge, gate, relay-stamp the plan delta,
   commit.
