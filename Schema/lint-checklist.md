# Lint Checklist

What `python scripts/wiki_tool.py lint` and `source-lint` enforce, and what to
check manually when editing notes.

## Compiled Wiki Notes (`lint`)

- [ ] Note has YAML frontmatter.
- [ ] Note uses exactly one allowed tag: `topic`, `concept`, `entity`,
      `project`, or `log`.
- [ ] Tag matches the folder the note lives in.
- [ ] `created` and `updated` are present in `YYYY-MM-DD` format.
- [ ] `sources` is a list of vault-relative paths.
- [ ] Every `sources` entry points to an existing file under `Raw/Sources/`.
- [ ] `source_count` equals the number of entries in `sources`.
- [ ] `status` is one of `seed`, `growing`, `evergreen`.

## Raw Source Notes (`source-lint`)

- [ ] Frontmatter includes `Title`, `Reference`, `Created`, `Processed`,
      and `tags`.
- [ ] `tags` includes `source`.
- [ ] If `Processed: true`, at least one compiled Wiki note lists this file
      in its `sources` (coverage check).
- [ ] Manifest entry in `Schema/source-manifest.jsonl` is up to date.

## Manual Checks (not automated)

- [ ] Claims in compiled notes are actually supported by the linked sources.
- [ ] No invented citations.
- [ ] Notes stay short and focused — split notes that grow past one idea.
