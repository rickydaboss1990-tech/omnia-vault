# Third-Party Notices

Cortex bundles ("vendors") several excellent open-source skills so a fresh
clone works with zero installs. Each stays under its own license, preserved in
its folder. Thank you to every author.

## Vendored in this repository

| Component | Path | Source | License |
|---|---|---|---|
| Obsidian editing skills (`obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`) | `.claude/skills/…` | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | MIT (`.claude/skills/LICENSE-kepano-obsidian-skills`) |
| Taste — anti-slop frontend design | `.claude/skills/taste` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (skill `taste-skill`, renamed `taste` here) | MIT (`.claude/skills/taste/LICENSE`) |
| UI/UX Pro Max — design intelligence databases | `.claude/skills/ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (script paths adapted from `${CLAUDE_PLUGIN_ROOT}` to project-relative) | MIT (`.claude/skills/ui-ux-pro-max/LICENSE`) |
| Humanizer — remove AI-writing tells | `.claude/skills/humanizer` | [blader/humanizer](https://github.com/blader/humanizer) | MIT (`.claude/skills/humanizer/LICENSE`) |
| Graphify skill (drives the `graphifyy` CLI) | `.claude/skills/graphify` | the [graphifyy](https://pypi.org/project/graphifyy/) project | per its project license |

## Installed on demand (not redistributable or too heavy to vendor)

| Component | How to get it | License |
|---|---|---|
| Anthropic document skills (docx/pdf/pptx/xlsx) | `/docs-setup` → `/plugin marketplace add anthropics/skills` + `/plugin install document-skills@anthropic-agent-skills` | Anthropic source-available (prohibits redistribution — which is why it is not vendored here) |
| impeccable — 23 design commands | `/design-setup` → `/plugin marketplace add pbakaus/impeccable` + `/plugin install impeccable@impeccable` | Apache-2.0 |
| `graphifyy` (the `graphify` CLI) | `pip install graphifyy` | per its project license |
| `claude-real-video` (the `crv` CLI) | `pip install claude-real-video` | per its project license |
| `defuddle` CLI | `npm install -g defuddle` | per its project license |

## Local modifications

- `taste`: skill frontmatter `name` changed from `design-taste-frontend` to
  `taste` for a cleaner invocation.
- `ui-ux-pro-max`: `search.py` invocation paths rewritten from
  `${CLAUDE_PLUGIN_ROOT}/…` to the project-relative
  `.claude/skills/ui-ux-pro-max/scripts/search.py`.
- No other vendored file is modified.
