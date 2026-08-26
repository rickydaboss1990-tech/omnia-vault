#!/usr/bin/env python3
"""plan_tool.py — deterministic helper for the war-room (the living project plan).

The war-room is the project's multi-phase roadmap plus the intel loop that
keeps it current: every new meeting or video is triaged AGAINST the plan
(worth incorporating or not), and every plan change carries provenance back to
the intel brief that caused it. Judgment lives in the `war-room` skill; this
tool owns the mechanical parts — scaffolding, the compact plan digest agents
load before watching anything, brief creation, and status math.

Layout (all committed):
    Plan/ROADMAP.md              vision, success criteria, phase table, changelog
    Plan/phases/phase-N-<slug>.md  objective, deliverables, exit criteria, status
    Plan/intel/<date>-<slug>.md  one brief per triaged source (ranked items + verdict)
    Plan/TOOLBOX.md              tool adoption ledger (candidate/trialing/adopted/rejected)

Standard library only. Commands:

    python scripts/plan_tool.py init --name "..." [--vision "..."] [--phases "A,B,C"]
    python scripts/plan_tool.py context          # compact digest — run BEFORE triaging intel
    python scripts/plan_tool.py new-intel --title "..." --source "<url-or-path>"
    python scripts/plan_tool.py status
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PLAN = VAULT / "Plan"
ROADMAP = PLAN / "ROADMAP.md"
PHASES = PLAN / "phases"
INTEL = PLAN / "intel"
TOOLBOX = PLAN / "TOOLBOX.md"
TODAY = date.today().isoformat()

STATUS_RE = re.compile(r"\*\*Status:\*\*\s*(\w+)", re.I)
VERDICT_RE = re.compile(r"^INTEL VERDICT:\s*(.+)$", re.M)


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return (s[:40].rstrip("-")) or "item"


def phase_files():
    return sorted(PHASES.glob("phase-*.md")) if PHASES.is_dir() else []


def phase_info(p):
    text = p.read_text(encoding="utf-8", errors="ignore")
    m = STATUS_RE.search(text)
    status = (m.group(1).lower() if m else "unknown")
    title_m = re.search(r"^# (.+)$", text, re.M)
    title = title_m.group(1) if title_m else p.stem
    boxes = re.findall(r"^- \[( |x|X)\]", text, re.M)
    done = sum(1 for b in boxes if b.lower() == "x")
    return {"path": p, "title": title, "status": status,
            "done": done, "total": len(boxes), "text": text}


def cmd_init(args):
    if ROADMAP.exists():
        print("plan: Plan/ROADMAP.md already exists — the war-room is initialized. "
              "Edit it directly, or use `context` / `status`.")
        return 1
    names = [n.strip() for n in (args.phases or "Discovery,Foundation,Build,Launch").split(",")
             if n.strip()]
    PHASES.mkdir(parents=True, exist_ok=True)
    INTEL.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, name in enumerate(names, 1):
        slug = slugify(name)
        pf = PHASES / f"phase-{i}-{slug}.md"
        status = "active" if i == 1 else "pending"
        pf.write_text(
            f"# Phase {i} — {name}\n\n"
            f"**Status:** {status}\n\n"
            "## Objective\n\n<what this phase must make true — one paragraph>\n\n"
            "## Deliverables\n\n- [ ] <concrete deliverable>\n\n"
            "## Exit criteria\n\n- <the observable condition that ends this phase>\n\n"
            "## Depends on\n\n- <phases/decisions this waits on, or none>\n\n"
            "## Changelog\n\n"
            f"- {TODAY} — phase created (war-room init)\n",
            encoding="utf-8")
        rows.append(f"| {i} | [{name}](phases/{pf.name}) | {status} |")

    ROADMAP.write_text(
        f"# Roadmap: {args.name}\n\n"
        f"_The living plan. Every change here traces to an intel brief or a decision "
        f"with the user. Maintained by the `war-room` skill._\n\n"
        "## Vision\n\n"
        f"{args.vision or '<one paragraph: what done looks like and for whom>'}\n\n"
        "## Success criteria\n\n- <measurable statement of success>\n\n"
        "## Phases\n\n"
        "| # | Phase | Status |\n|---|-------|--------|\n" + "\n".join(rows) + "\n\n"
        "## Top risks\n\n- <biggest thing that could sink this>\n\n"
        "## Changelog\n\n"
        f"- {TODAY} — roadmap created (war-room init)\n",
        encoding="utf-8")

    if not TOOLBOX.exists():
        TOOLBOX.write_text(
            "# Toolbox — adoption ledger\n\n"
            "_Every tool the plan considers, with provenance. Statuses: **candidate** "
            "(spotted, not tried) → **trialing** (installed, timeboxed) → **adopted** "
            "(in the plan) / **rejected** (logged why). Installs happen only after the "
            "user confirms the specific tool, from its official source._\n\n"
            "| Tool | Status | Install | Official source | Intel source | Notes |\n"
            "|------|--------|---------|-----------------|--------------|-------|\n",
            encoding="utf-8")

    print(f"plan: war-room initialized — {len(names)} phases under Plan/")
    print("plan: fill in Vision, Success criteria, each phase's Objective/Deliverables/"
          "Exit criteria, then gate + commit.")
    return 0


def cmd_context(_):
    if not ROADMAP.is_file():
        print("plan: no Plan/ROADMAP.md — the war-room isn't initialized. "
              "Run: python scripts/plan_tool.py init --name \"...\"")
        return 1
    text = ROADMAP.read_text(encoding="utf-8", errors="ignore")
    vision = re.search(r"## Vision\s*\n+(.+?)(?=\n## |\Z)", text, re.S)
    print("=== PLAN CONTEXT (digest — read this before watching anything) ===")
    if vision:
        print("VISION: " + " ".join(vision.group(1).split())[:400])
    infos = [phase_info(p) for p in phase_files()]
    for info in infos:
        print(f"PHASE: {info['title']}  [{info['status']}]  "
              f"deliverables {info['done']}/{info['total']}")
    for info in infos:
        if info["status"] == "active":
            open_items = re.findall(r"^- \[ \] (.+)$", info["text"], re.M)[:10]
            for item in open_items:
                print(f"  OPEN ({info['title']}): {item}")
    if TOOLBOX.is_file():
        ttext = TOOLBOX.read_text(encoding="utf-8", errors="ignore")
        counts = {}
        adopted = []
        for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*(candidate|trialing|adopted|rejected)\s*\|",
                             ttext, re.M | re.I):
            counts[m.group(2).lower()] = counts.get(m.group(2).lower(), 0) + 1
            if m.group(2).lower() == "adopted":
                adopted.append(m.group(1))
        print("TOOLBOX: " + (", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "empty"))
        if adopted:
            print("  adopted: " + ", ".join(adopted))
    briefs = sorted(INTEL.glob("*.md")) if INTEL.is_dir() else []
    for b in briefs[-3:]:
        btext = b.read_text(encoding="utf-8", errors="ignore")
        vm = VERDICT_RE.search(btext)
        print(f"RECENT INTEL: {b.name}  ->  {vm.group(1) if vm else '(no verdict line)'}")
    print(f"=== end digest ({len(infos)} phases, {len(briefs)} intel briefs) ===")
    return 0


def cmd_new_intel(args):
    if not ROADMAP.is_file():
        print("plan: initialize the war-room first (`init --name ...`).")
        return 1
    INTEL.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.slug or args.title)
    out = INTEL / f"{TODAY}-{slug}.md"
    n = 1
    while out.exists():
        n += 1
        out = INTEL / f"{TODAY}-{slug}-{n}.md"
    out.write_text(
        f"# Intel: {args.title}\n\n"
        f"- **Source:** {args.source}\n"
        f"- **Captured:** {TODAY} · full capture: <Raw/Sources/... once ingested>\n"
        f"- **Triaged against:** <active phase(s) from the plan digest>\n\n"
        "## What's genuinely new here\n\n<2-4 sentences — against the wiki and prior "
        "intel, not against zero>\n\n"
        "## Ranked items\n\n"
        "| # | Item | Phase fit | Impact | Effort | Confidence | Verdict | Why (one line) |\n"
        "|---|------|-----------|--------|--------|------------|---------|----------------|\n"
        "| 1 | <technique/tool/pattern> | <phase or none> | H/M/L | H/M/L | H/M/L | ADOPT/TRIAL/WATCH/SKIP | <reason tied to the plan> |\n\n"
        "## Tools & links mentioned\n\n"
        "- <tool> — <official source verified, or 'UNVERIFIED — video link only'>\n\n"
        "## Recommendation\n\n<what to incorporate, what to skip, and what it changes "
        "in which phase>\n\n"
        "INTEL VERDICT: <INCORPORATE (n items) | WATCHLIST | PASS> — <one line>\n\n"
        "## Disposition (filled after the user's call)\n\n"
        "- <item> -> <incorporated into phase-N / watchlisted / passed> — <date>\n",
        encoding="utf-8")
    print(f"plan: intel brief created — {out.relative_to(VAULT)}")
    return 0


def cmd_status(_):
    if not ROADMAP.is_file():
        print("plan: war-room not initialized (no Plan/ROADMAP.md).")
        return 0
    infos = [phase_info(p) for p in phase_files()]
    done_phases = sum(1 for i in infos if i["status"] == "done")
    active = [i["title"] for i in infos if i["status"] == "active"]
    d_done = sum(i["done"] for i in infos)
    d_total = sum(i["total"] for i in infos)
    briefs = sorted(INTEL.glob("*.md")) if INTEL.is_dir() else []
    no_verdict = [b.name for b in briefs
                  if not VERDICT_RE.search(b.read_text(encoding="utf-8", errors="ignore"))]
    print(f"plan: phases       {done_phases}/{len(infos)} done · active: "
          f"{', '.join(active) or 'NONE — mark one phase **Status:** active'}")
    print(f"plan: deliverables {d_done}/{d_total} checked")
    print(f"plan: intel        {len(briefs)} brief(s)")
    if no_verdict:
        print(f"plan: WARNING      brief(s) missing an INTEL VERDICT line: "
              f"{', '.join(no_verdict)}")
    if TOOLBOX.is_file():
        ttext = TOOLBOX.read_text(encoding="utf-8", errors="ignore")
        trialing = re.findall(r"^\|\s*([^|]+?)\s*\|\s*trialing\s*\|", ttext, re.M | re.I)
        if trialing:
            print(f"plan: trialing     {', '.join(t.strip() for t in trialing)} — "
                  "promote to adopted or rejected once judged")
    return 0


def main():
    ap = argparse.ArgumentParser(description="War-room plan helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="scaffold Plan/ (roadmap, phases, intel, toolbox)")
    i.add_argument("--name", required=True)
    i.add_argument("--vision")
    i.add_argument("--phases", help="comma-separated phase names")
    i.set_defaults(fn=cmd_init)

    sub.add_parser("context", help="compact plan digest for intel triage").set_defaults(
        fn=cmd_context)

    ni = sub.add_parser("new-intel", help="scaffold a dated intel brief")
    ni.add_argument("--title", required=True)
    ni.add_argument("--source", required=True)
    ni.add_argument("--slug")
    ni.set_defaults(fn=cmd_new_intel)

    sub.add_parser("status", help="plan health: phases, deliverables, intel, toolbox").set_defaults(
        fn=cmd_status)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
