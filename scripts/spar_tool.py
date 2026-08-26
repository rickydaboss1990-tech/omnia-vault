#!/usr/bin/env python3
"""spar_tool.py — deterministic state for the sparring loop (cross-model review).

Sparring is the relay's synchronous mode: one agent drives the session, the
rival model attacks its plan (and later its diff) in bounded rounds, and the
whole argument is kept as an artifact. This tool owns the mechanical parts —
round counting, verdict parsing, the append-only log, resumable state — so an
interrupted spar can be picked up by ANY later session. The judgment calls
(what to revise, what to rebut) belong to the driving agent; see
`.claude/skills/sparring/SKILL.md`.

Layout (under _relay/spar/):
    PLAN.md        the evolving plan / frozen spec (committed)
    SPAR-LOG.md    append-only argument transcript (committed)
    state.json     machine-local loop state incl. reviewer thread id (gitignored)
    archive/       finished spars, one folder each (committed)

Standard library only. Commands:

    python scripts/spar_tool.py start --task "..." [--rounds 5]
                                [--reviewer codex] [--driver claude] [--archive-active]
    python scripts/spar_tool.py set-thread --id <thread-or-session-id>
    python scripts/spar_tool.py record-round --critique-file <path>
    python scripts/spar_tool.py respond --file <path> | --text "..."
    python scripts/spar_tool.py status
    python scripts/spar_tool.py finish --outcome approved|deadlock|abandoned [--summary "..."]
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
SPAR = VAULT / "_relay" / "spar"
STATE = SPAR / "state.json"
PLAN = SPAR / "PLAN.md"
LOG = SPAR / "SPAR-LOG.md"
VERDICT_RE = re.compile(r"^\s*VERDICT:\s*(APPROVED|REVISE)\s*$", re.I)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def load_state():
    if not STATE.is_file():
        return None
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def save_state(st):
    SPAR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")


def append_log(text):
    old = LOG.read_text(encoding="utf-8") if LOG.is_file() else ""
    if old and not old.endswith("\n\n"):
        old = old.rstrip("\n") + "\n\n"
    LOG.write_text(old + text.rstrip("\n") + "\n\n", encoding="utf-8")


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return (s[:40].rstrip("-")) or "spar"


def parse_verdict(text):
    """Scan upward from the bottom for the verdict line (models sometimes trail
    whitespace or a sign-off after it)."""
    for line in reversed(text.splitlines()[-8:]):
        m = VERDICT_RE.match(line)
        if m:
            return m.group(1).upper()
    return None


def archive_spar(st):
    stamp = (st.get("started") or now_iso())[:10]
    dest = SPAR / "archive" / f"{stamp}-{slugify(st.get('task', 'spar'))}"
    n = 1
    base = dest
    while dest.exists():
        n += 1
        dest = base.with_name(f"{base.name}-{n}")
    dest.mkdir(parents=True)
    for f in (PLAN, LOG):
        if f.is_file():
            shutil.move(str(f), str(dest / f.name))
    STATE.unlink(missing_ok=True)
    return dest


def require_active():
    st = load_state()
    if not st or st.get("outcome"):
        print("spar: no active spar. Start one: "
              "python scripts/spar_tool.py start --task \"...\"")
        sys.exit(1)
    return st


def cmd_start(args):
    st = load_state()
    if st and not st.get("outcome"):
        if args.archive_active:
            dest = archive_spar(st)
            print(f"spar: archived the previous unfinished spar to {dest.relative_to(VAULT)}")
        else:
            print(f"spar: an active spar exists (task: {st.get('task')!r}, round "
                  f"{st.get('round')}). Finish it (`finish --outcome ...`) or pass "
                  "--archive-active.")
            return 1
    SPAR.mkdir(parents=True, exist_ok=True)
    st = {
        "task": args.task,
        "started": now_iso(),
        "phase": "scout",
        "round": 0,
        "max_rounds": args.rounds,
        "verdict": None,
        "reviewer": args.reviewer,
        "driver": args.driver,
        "thread": None,
        "outcome": None,
    }
    save_state(st)
    if not LOG.is_file():
        LOG.write_text(
            f"# Spar Log: {args.task}\n\n"
            f"Started {st['started']} · driver **{st['driver']}** · reviewer "
            f"**{st['reviewer']}** · max {st['max_rounds']} rounds.\n"
            "Append-only. Every critique, every arbiter response, the whole argument.\n\n",
            encoding="utf-8")
    if not PLAN.is_file():
        PLAN.write_text(
            f"# Plan: {args.task}\n\n_Draft — locked when the LOCK phase resolves "
            "the decision map._\n\n## Goal\n\n## Approach\n\n## Key decisions & tradeoffs\n\n"
            "## Assumptions (with sources)\n\n## Risks / open questions\n\n## Out of scope\n",
            encoding="utf-8")
    print(f"spar: started — task: {args.task!r}")
    print(f"spar: plan {PLAN.relative_to(VAULT)} · log {LOG.relative_to(VAULT)} · "
          f"max_rounds {st['max_rounds']}")
    return 0


def cmd_set_thread(args):
    st = require_active()
    st["thread"] = args.id
    if st["phase"] == "scout":
        st["phase"] = "spar"
    save_state(st)
    print(f"spar: reviewer thread recorded ({args.id})")
    return 0


def cmd_record_round(args):
    st = require_active()
    critique = Path(args.critique_file).read_text(encoding="utf-8", errors="ignore").strip()
    if not critique:
        print(f"spar: critique file {args.critique_file} is empty — the reviewer run "
              "likely failed (auth/model/timeout). Not recording a round.")
        return 1
    st["round"] += 1
    st["phase"] = "spar"
    verdict = parse_verdict(critique)
    st["verdict"] = verdict
    save_state(st)
    append_log(f"## Round {st['round']} — {st['reviewer']} ({now_iso()})\n\n{critique}")
    flags = []
    if verdict is None:
        flags.append("NO-VERDICT-LINE (treat as REVISE; re-ask for the contract line)")
    if st["round"] >= st["max_rounds"] and verdict != "APPROVED":
        flags.append(f"ROUND-CAP-REACHED ({st['max_rounds']})")
    print(f"spar: round={st['round']}/{st['max_rounds']} verdict={verdict or 'NONE'}"
          + (("  [" + "; ".join(flags) + "]") if flags else ""))
    return 0


def cmd_respond(args):
    st = require_active()
    text = Path(args.file).read_text(encoding="utf-8", errors="ignore").strip() \
        if args.file else (args.text or "").strip()
    if not text:
        print("spar: nothing to record (pass --file or --text).")
        return 1
    append_log(f"### Arbiter response — {st['driver']} ({now_iso()})\n\n{text}")
    print("spar: arbiter response logged")
    return 0


def cmd_status(_):
    st = load_state()
    if not st:
        print("spar: no spar state. `start --task \"...\"` begins one.")
        arch = SPAR / "archive"
        if arch.is_dir():
            done = sorted(p.name for p in arch.iterdir() if p.is_dir())
            if done:
                print(f"spar: {len(done)} archived spar(s); latest: archive/{done[-1]}")
        return 0
    print(f"spar: task        {st.get('task')}")
    print(f"spar: phase       {st.get('phase')}   round {st.get('round')}/{st.get('max_rounds')}"
          f"   last verdict {st.get('verdict') or '-'}")
    print(f"spar: driver      {st.get('driver')}   reviewer {st.get('reviewer')}"
          f"   thread {st.get('thread') or '(none yet)'}")
    print(f"spar: outcome     {st.get('outcome') or 'ACTIVE'}   started {st.get('started')}")
    print(f"spar: files       {PLAN.relative_to(VAULT)} · {LOG.relative_to(VAULT)}")
    if st.get("outcome") is None and st.get("round", 0) >= st.get("max_rounds", 0) \
            and st.get("verdict") != "APPROVED":
        print("spar: NOTE        round cap reached without APPROVED — resolve as a "
              "deadlock (finish --outcome deadlock) rather than looping on.")
    return 0


def cmd_finish(args):
    st = require_active()
    st["outcome"] = args.outcome
    st["phase"] = "done"
    summary = (args.summary or "").strip()
    append_log(f"## Outcome — {args.outcome.upper()} ({now_iso()})\n\n"
               f"Rounds used: {st['round']}/{st['max_rounds']}."
               + (f"\n\n{summary}" if summary else ""))
    save_state(st)
    dest = archive_spar(st)
    rel = dest.relative_to(VAULT)
    print(f"spar: finished ({args.outcome}) — archived to {rel}")
    print("spar: next — compile the argument into the vault: capture the log as a "
          f"Raw source citing {rel}/SPAR-LOG.md, fold the plan's Key Decisions into "
          "Wiki notes, gate, relay-stamp, commit (the sparring skill's SHIP phase).")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Sparring loop state helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="begin a spar")
    s.add_argument("--task", required=True)
    s.add_argument("--rounds", type=int, default=5)
    s.add_argument("--reviewer", default="codex")
    s.add_argument("--driver", default="claude")
    s.add_argument("--archive-active", action="store_true",
                   help="archive an unfinished spar instead of refusing")
    s.set_defaults(fn=cmd_start)

    t = sub.add_parser("set-thread", help="record the reviewer's session/thread id")
    t.add_argument("--id", required=True)
    t.set_defaults(fn=cmd_set_thread)

    r = sub.add_parser("record-round", help="log a critique + parse its verdict")
    r.add_argument("--critique-file", required=True)
    r.set_defaults(fn=cmd_record_round)

    p = sub.add_parser("respond", help="log the driver's arbiter response")
    p.add_argument("--file")
    p.add_argument("--text")
    p.set_defaults(fn=cmd_respond)

    sub.add_parser("status", help="show loop state").set_defaults(fn=cmd_status)

    f = sub.add_parser("finish", help="close the spar and archive its artifacts")
    f.add_argument("--outcome", required=True,
                   choices=["approved", "deadlock", "abandoned"])
    f.add_argument("--summary")
    f.set_defaults(fn=cmd_finish)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
