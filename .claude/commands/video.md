---
description: Watch + ingest a video/audio recording or URL (YouTube, TikTok, ...) — transcript + frames, correlated
argument-hint: <file path or URL> [optional: what to focus on]
---

Run the `video-ingest` skill on: $ARGUMENTS

Remember the essentials:
- crv extraction runs in the **background** (Whisper is slow on CPU); use a
  scratch output dir outside the vault.
- Correlate frames ⇄ transcript chronologically (strided overview pass, then
  dense passes over the sections that matter).
- Redact secrets; never copy a frame showing one into the vault.
- If the user only wants the video *studied* (a reference/inspiration video),
  answer their question from the transcript + frames and ask before ingesting
  it into the vault.
