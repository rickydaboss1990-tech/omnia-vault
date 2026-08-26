#!/usr/bin/env python3
"""relay_tool.py — deterministic helper for the Claude <-> Codex relay.

The relay is how two different coding agents work the same project without
copy-paste: whichever agent finishes a work session writes the baton
(`_relay/STATE.md`), and whichever agent starts next reads it first.
This tool stamps and checks the baton; the CONTENT of the baton is written by
the agent (see `.claude/skills/relay/SKILL.md` and `_relay/PROTOCOL.md`).

Standard library only. Usage:

    python scripts/relay_tool.py status
        Show who holds the baton, when it was last stamped, and whether commits
        have landed AFTER the last handoff (= someone worked without handing off).

    python scripts/relay_tool.py stamp --agent claude --summary "what changed"
        Update the `> Last handoff:` line in _relay/STATE.md and prepend an
        entry to _relay/HISTORY.md. Run this AFTER editing STATE.md's sections.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
STATE = VAULT / "_relay" / "STATE.md"
HISTORY = VAULT / "_relay" / "HISTORY.md"
STAMP_RE = re.compile(r"^> Last handoff:.*$", re.M)


def git(*args):
    try:
        r = subprocess.run(["git", *args], cwd=str(VAULT), capture_output=True,
                           text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def parse_stamp(text):
    m = STAMP_RE.search(text)
    if not m:
        return None
    line = m.group(0)
    m2 = re.search(r"Last handoff: (\S+) [·|] by (\S+) [·|] at (\S+)", line)
    if not m2:
        return {"raw": line}
    return {"raw": line, "when": m2.group(1), "agent": m2.group(2), "sha": m2.group(3)}


def cmd_status(_):
    if not STATE.is_file():
        print("relay: no _relay/STATE.md — this vault has no baton yet.")
        print("  Create one from _relay/PROTOCOL.md, or run a `save` so the agent writes it.")
        return 1
    text = STATE.read_text(encoding="utf-8")
    stamp = parse_stamp(text)
    head = git("rev-parse", "--short", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    print(f"relay: baton file  _relay/STATE.md")
    if stamp and stamp.get("when"):
        print(f"relay: last stamp  {stamp['when']} by {stamp['agent']} at {stamp['sha']}")
    else:
        print("relay: last stamp  (none — STATE.md has never been stamped)")
    if head:
        print(f"relay: git HEAD    {head} on {branch}")
        if stamp and stamp.get("sha") and stamp["sha"] not in ("", "no-git", head):
            behind = git("rev-list", "--count", f"{stamp['sha']}..HEAD")
            # The stamp is written BEFORE the handoff commit, so exactly one
            # commit after the stamped sha is a normal, fresh handoff. Two or
            # more means work landed without a new handoff.
            if behind and behind.isdigit() and int(behind) > 1:
                print(f"relay: WARNING     {behind} commits landed after the last handoff "
                      "stamp (1 is normal — the handoff commit itself) — the baton may "
                      "be stale. Read `git log` before trusting it.")
    # Show the "Now" section so `status` is a one-stop orientation.
    m = re.search(r"^## Now\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if m and m.group(1).strip():
        print("\n--- STATE.md · Now ---")
        print(m.group(1).strip())
    return 0


def cmd_stamp(args):
    if not STATE.is_file():
        print("relay: _relay/STATE.md missing — create it first (see _relay/PROTOCOL.md).")
        return 1
    head = git("rev-parse", "--short", "HEAD") or "no-git"
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "-"
    when = now_iso()
    line = f"> Last handoff: {when} · by {args.agent} · at {head} ({branch})"
    text = STATE.read_text(encoding="utf-8")
    if STAMP_RE.search(text):
        text = STAMP_RE.sub(line, text, count=1)
    else:
        text = line + "\n\n" + text
    STATE.write_text(text, encoding="utf-8")

    entry = f"## {when} · {args.agent} · {head}\n\n{args.summary.strip()}\n\n"
    old = HISTORY.read_text(encoding="utf-8") if HISTORY.is_file() else "# Relay History\n\nNewest first. One entry per handoff (stamped by `scripts/relay_tool.py stamp`).\n\n"
    if not old.endswith("\n\n"):
        old = old.rstrip("\n") + "\n\n"
    m = re.search(r"\n## ", old)
    insert_at = m.start() + 1 if m else len(old)
    HISTORY.write_text(old[:insert_at] + entry + old[insert_at:], encoding="utf-8")
    print(f"relay: stamped STATE.md ({when} · {args.agent} · {head}) and logged to HISTORY.md")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Claude <-> Codex relay helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="show baton state + staleness check").set_defaults(fn=cmd_status)
    st = sub.add_parser("stamp", help="stamp STATE.md and append to HISTORY.md")
    st.add_argument("--agent", required=True, help="who is handing off (claude | codex | <name>)")
    st.add_argument("--summary", required=True, help="one-paragraph summary of the session")
    st.set_defaults(fn=cmd_stamp)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
