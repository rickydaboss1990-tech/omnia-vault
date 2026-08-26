# Naming Conventions

## Files

- All note filenames are lowercase kebab-case: `raw-vs-compiled-knowledge.md`.
- No spaces, no underscores, no special characters in filenames.
- Keep filenames short but descriptive; prefer the note's main noun phrase.

## Folders

| Note type | Folder | Tag |
|-----------|--------|-----|
| Topic | `Wiki/Topics/` | `topic` |
| Concept | `Wiki/Concepts/` | `concept` |
| Entity | `Wiki/Entities/` | `entity` |
| Project | `Wiki/Projects/` | `project` |
| Log | `Wiki/Logs/` | `log` |
| Raw source | `Raw/Sources/` | `source` |
| Raw file/attachment | `Raw/Files/` | — |

## Note Types

- **Topic**: a broad area that groups concepts (e.g. `llm-wiki`).
- **Concept**: one reusable idea, explained in a few paragraphs.
- **Entity**: a person, organization, product, or tool.
- **Project**: an ongoing effort with goals and status.
- **Log**: a dated record of what changed and why.

## Titles and Aliases

- The H1 title inside the note is Title Case and may differ from the filename.
- Use `aliases` in frontmatter for alternate names instead of duplicate notes.

## Generated Files (do not hand-edit)

- `Wiki/catalog.jsonl`
- `Wiki/index.md` and per-folder `index.md` files
- `Schema/source-manifest.jsonl`

Regenerate them with `python scripts/wiki_tool.py build` and
`python scripts/wiki_tool.py source-scan --update`.
