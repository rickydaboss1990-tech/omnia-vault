---
description: Run the maintenance gate (doctor, build, lint, source-lint, audit) and fix what fails
---

Run the full maintenance gate from the vault root and show the results:

```bash
python scripts/wiki_tool.py doctor
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-lint
python scripts/audit_public.py
```

If sources were ingested this session, also:

```bash
python scripts/wiki_tool.py source-scan --update --accept-covered
python scripts/wiki_tool.py source-lint
```

For every failure, open the offending note and fix the **cause** (see the
`llm-wiki-lint` skill and `Schema/lint-checklist.md`) — never silence a check
by deleting `sources` or hand-editing generated files. Re-run until green,
then report what was fixed.
