---
description: Enable the frontend design stack — vendored Taste + UI/UX Pro Max, plus the impeccable plugin
---

Set up the design skills for this project:

1. **Already vendored (work out of the box, nothing to install):**
   - `taste` (`.claude/skills/taste`) — anti-slop frontend taste for landing
     pages, portfolios, redesigns (MIT, Leonxlnx/taste-skill).
   - `ui-ux-pro-max` (`.claude/skills/ui-ux-pro-max`) — searchable design
     intelligence: styles, palettes, font pairings, UX rules, stacks (MIT,
     nextlevelbuilder/ui-ux-pro-max-skill). Its search tool:
     `python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain>`
   Confirm both load by listing available skills.
2. **Impeccable (plugin, adds ~23 design commands like `impeccable:polish`,
   `impeccable:animate`, `impeccable:critique`):** ask the user to run
   `/plugin marketplace add pbakaus/impeccable` then
   `/plugin install impeccable@impeccable` (Apache-2.0). If plugins are
   unavailable in their client, `npx impeccable install` does the same from a
   terminal.
3. Tell the user when to reach for which: **ui-ux-pro-max** for system-level
   design decisions and reviews, **taste** for landing-page-class visual work,
   **impeccable** commands for iterating on an existing UI.
