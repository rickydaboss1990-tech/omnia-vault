# Workflow Examples

Three worked examples of the system's core loops, end to end. Commands assume
the vault root (`python` on Windows, `python3` on macOS/Linux).

---

## Example 1 — Ingest a meeting recording

The user drops `standup-2026-03-14.mkv` and says "get this into the vault."

1. **Extract (background)** — per the `video-ingest` skill:
   ```powershell
   $env:PYTHONUTF8=1
   crv "standup-2026-03-14.mkv" -o "../scratch/standup" --lang en `
       --whisper-model small --adaptive --text-anchors --viewer --max-frames 200
   ```
2. **Watch it** — read `transcript.txt` fully; strided pass over `frames/`,
   then dense passes where screens matter; align said ⇄ shown chronologically;
   redact anything secret.
3. **Raw source** — `Raw/Sources/2026-03-14-standup-recording.md` with source
   frontmatter (`Reference:` the filename), provenance note, Summary,
   Walkthrough (said/shown pairs), curated screenshots embedded from
   `assets/`, full transcript appended.
4. **Compile** —
   `python scripts/wiki_tool.py search-catalog --query "deployment pipeline"`
   → the decision from the meeting enriches
   `Wiki/Concepts/deployment-pipeline.md` (add the new source to `sources`,
   bump `source_count` and `updated`) and a new open question lands in the
   project note. A dated `Wiki/Logs/` note records the ingest.
5. **Gate + commit**:
   ```bash
   python scripts/wiki_tool.py build && python scripts/wiki_tool.py lint
   python scripts/wiki_tool.py source-scan --update --accept-covered
   python scripts/wiki_tool.py source-lint && python scripts/audit_public.py
   git add -A && git commit -m "Ingest 2026-03-14 standup recording"
   ```

---

## Example 2 — Answer "where do we validate uploads, and what are the rules?"

A question spanning code + decisions → the 3-layer rule
(`project-context-query` skill):

1. **Layer 1 (code shape):**
   ```bash
   graphify query "where are uploads validated" --graph graphify/my-app/graph.json
   ```
   → points at `UploadValidator` + its callers; `graphify explain "UploadValidator"`
   for detail.
2. **Layer 2 (decided rules):**
   ```bash
   python scripts/wiki_tool.py search-catalog --query "upload validation rules"
   ```
   → `Wiki/Concepts/upload-validation-rules.md` carries the size/type limits
   the team agreed on, with the meeting source cited.
3. **Answer** from those two, citing the note; open the actual code file only
   if an edit is next. No repo sweep, no transcript re-read.

---

## Example 3 — Hand the work from Claude Code to Codex mid-feature

Claude planned a feature; the user wants Codex to grind out the implementation.

1. In Claude Code: `/handoff` →
   - `_relay/STATE.md` rewritten: **Now** (feature X planned, design in
     `Wiki/Concepts/feature-x-design.md`), **Just landed** (plan + scaffolding),
     **Next** (checkboxes: implement endpoints, wire tests), **Watch out**
     (migration untested).
   - `python scripts/relay_tool.py stamp --agent claude --summary "Planned feature X; scaffolding committed; implementation next."`
   - Gate → commit.
2. User opens the same folder in Codex: *"catch up."*
   - Codex (per AGENTS.md) reads `_relay/STATE.md`, runs
     `python scripts/relay_tool.py status` + `git log --oneline -10`,
     confirms the plan, and starts implementing — zero context re-explained.
3. Codex finishes: rewrites STATE.md, stamps with `--agent codex`, gates,
   commits. Next Claude session starts with `/catchup` and sees exactly what
   landed.
