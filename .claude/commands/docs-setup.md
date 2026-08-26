---
description: Enable the Anthropic document skills (Word, PDF, PowerPoint, Excel) for reports & deliverables
---

Enable polished document output (reports, PDFs, decks, spreadsheets):

1. The official Anthropic document skills (docx / pdf / pptx / xlsx) are
   **source-available and cannot be redistributed**, so they are not vendored
   in this repo — they install in one step from Anthropic's marketplace. Ask
   the user to run:
   - `/plugin marketplace add anthropics/skills`
   - `/plugin install document-skills@anthropic-agent-skills`
2. Verify the skills are available (list skills; look for docx/pdf/pptx/xlsx).
3. From then on: "make this a PDF report", "draft the Word doc", "build the
   deck" route through those skills. Pair with the
   `stakeholder-update-writing` skill for the prose and the `humanizer` pass.
4. If plugins are unavailable in the user's client, fall back to generating
   documents with python libraries and say so honestly.
