#!/usr/bin/env python3
"""import_chats.py — archive Claude Code AND Codex sessions for this vault into chats/.

Both agents leave transcripts on the machine. This script turns the ones that
belong to THIS vault into cleaned, readable Markdown so past sessions become
local, searchable memory:

  Claude Code  ~/.claude/projects/<slug>/*.jsonl      -->  chats/code/*.md
  Codex CLI    ~/.codex/sessions/**/*.jsonl (by cwd)  -->  chats/codex/*.md

SAFETY:
- `chats/` is gitignored — these dumps are LOCAL memory, never committed (raw
  transcripts contain machine paths + any tokens that appeared in-session).
- As defense-in-depth we still redact obvious secret patterns on the way in.

Standard library only. Usage:
    python scripts/import_chats.py                 # both agents, auto-detected
    python scripts/import_chats.py --claude-only
    python scripts/import_chats.py --codex-only
    python scripts/import_chats.py --slug <slug>   # override the Claude project slug
    python scripts/import_chats.py --force         # re-convert even if up to date
"""

import json
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
ARGS = sys.argv[1:]
FORCE = "--force" in ARGS


def claude_slug():
    """Claude Code stores project transcripts under a slug derived from the
    project path: every non-alphanumeric character becomes '-'.
    e.g.  C:\\Work\\my-vault  ->  C--Work-my-vault"""
    if "--slug" in ARGS:
        return ARGS[ARGS.index("--slug") + 1]
    return re.sub(r"[^A-Za-z0-9]", "-", str(VAULT))


# Defense-in-depth redaction (chats/ is gitignored, but never store live secrets).
REDACTIONS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[REDACTED PRIVATE KEY]"),
    (re.compile(r"x-access-token:gh[a-z]_[A-Za-z0-9]+"), "x-access-token:[REDACTED]"),
    (re.compile(r"\bgh[posru]_[A-Za-z0-9]{20,}\b"), "[REDACTED-GH-TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED-AWS-KEY]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[REDACTED-SLACK-TOKEN]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[REDACTED-API-KEY]"),
    (re.compile(r"""(?i)(\b(?:api[_-]?key|token|secret)\s*[:=]\s*)['"][^'"]{8,}['"]"""), r'\1"[REDACTED]"'),
    (re.compile(r"""(?i)(\bpassword\s*[:=]\s*)['"][^'"]{4,}['"]"""), r'\1"[REDACTED]"'),
]


def redact(text):
    for pat, repl in REDACTIONS:
        text = pat.sub(repl, text)
    return text


def up_to_date(src, out):
    return (not FORCE) and out.exists() and out.stat().st_mtime >= src.stat().st_mtime


# ---------------------------------------------------------------- Claude Code

def claude_block_text(content):
    """Flatten a message .content (str or list of blocks) into readable text."""
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts = []
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            parts.append(b.get("text", "").strip())
        elif t == "tool_use":
            parts.append(f"_[-> tool: {b.get('name', '?')}]_")
        elif t == "tool_result":
            parts.append("_[tool result omitted]_")
        elif t == "thinking":
            continue  # don't archive chain-of-thought
    return "\n\n".join(p for p in parts if p)


def convert_claude(jsonl_path):
    turns, meta = [], {}
    for line in jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") not in ("user", "assistant"):
            continue
        msg = o.get("message")
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", o["type"])
        text = claude_block_text(msg.get("content"))
        if role == "user" and (not text or text.startswith("_[tool result")):
            continue
        if not text:
            continue
        ts = o.get("timestamp", "")
        if not meta:
            meta = {"cwd": o.get("cwd", ""), "branch": o.get("gitBranch", ""),
                    "first_ts": ts}
        meta["last_ts"] = ts
        turns.append((ts, role, text))
    return turns, meta


# ---------------------------------------------------------------------- Codex

SCAFFOLD_RE = re.compile(r"^<[A-Za-z_][\w /-]*>")  # <app-context>, <user_instructions>, ...


def codex_text(content):
    if not isinstance(content, list):
        return ""
    parts = []
    for b in content:
        if isinstance(b, dict) and b.get("type") in ("input_text", "output_text", "text"):
            t = (b.get("text") or "").strip()
            if t:
                parts.append(t)
    return "\n\n".join(parts)


def codex_session_cwd(jsonl_path):
    """Cheap check: the first session_meta line carries the session's cwd."""
    try:
        with jsonl_path.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                o = json.loads(line)
                if o.get("type") == "session_meta":
                    return (o.get("payload") or {}).get("cwd", "")
                return ""  # first real line wasn't meta — treat as unknown
    except (OSError, json.JSONDecodeError):
        return ""
    return ""


def convert_codex(jsonl_path):
    turns, meta = [], {}
    with jsonl_path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = o.get("timestamp", "")
            if o.get("type") == "session_meta":
                p = o.get("payload") or {}
                meta = {"cwd": p.get("cwd", ""), "first_ts": ts,
                        "source": p.get("source", ""), "cli": p.get("cli_version", "")}
                continue
            if o.get("type") != "response_item":
                continue
            p = o.get("payload") or {}
            if p.get("type") != "message":
                continue
            role = p.get("role", "")
            if role not in ("user", "assistant"):
                continue  # skip developer/system scaffolding
            text = codex_text(p.get("content"))
            if not text:
                continue
            # Skip injected scaffold blocks that pose as user messages.
            if role == "user" and SCAFFOLD_RE.match(text):
                continue
            meta["last_ts"] = ts
            turns.append((ts, role, text))
    return turns, meta


# --------------------------------------------------------------------- render

def render(title, turns, meta, regen_hint):
    date = (meta.get("first_ts") or "")[:10] or "undated"
    lines = [
        f"# {title} — {date}",
        "",
        "> Local agent transcript archived into the vault as memory. **Gitignored — "
        "not committed.** Secrets auto-redacted on import. Regenerate with "
        f"`{regen_hint}`.",
        "",
        f"- **cwd:** {meta.get('cwd', '')}",
        f"- **turns:** {len(turns)}  |  **span:** {(meta.get('first_ts') or '')[:16]} -> {(meta.get('last_ts') or '')[:16]}",
        "",
        "---",
        "",
    ]
    for ts, role, text in turns:
        hhmm = ts[11:16] if len(ts) >= 16 else ""
        who = "User" if role == "user" else "Assistant"
        lines.append(f"## [{hhmm}] {who}")
        lines.append("")
        lines.append(redact(text))
        lines.append("")
    return "\n".join(lines)


def norm(p):
    return str(p).replace("/", "\\").rstrip("\\").lower() if "\\" in str(p) or ":" in str(p) \
        else str(p).rstrip("/").lower()


def main():
    do_claude = "--codex-only" not in ARGS
    do_codex = "--claude-only" not in ARGS
    total = 0

    if do_claude:
        src_dir = Path.home() / ".claude" / "projects" / claude_slug()
        out_dir = VAULT / "chats" / "code"
        if src_dir.is_dir():
            out_dir.mkdir(parents=True, exist_ok=True)
            n = 0
            for jp in sorted(src_dir.glob("*.jsonl")):
                turns, meta = convert_claude(jp)
                if not turns:
                    continue
                date_guess = (meta.get("first_ts") or "")[:10] or "undated"
                out = out_dir / f"{date_guess}-{jp.stem[:8]}.md"
                if up_to_date(jp, out):
                    continue
                out.write_text(render(f"Claude Code session {jp.stem[:8]}", turns, meta,
                                      "python scripts/import_chats.py"), encoding="utf-8")
                print(f"wrote {out.relative_to(VAULT)}  ({len(turns)} turns)")
                n += 1
            print(f"import_chats: {n} Claude session(s) archived to chats/code/")
            total += n
        else:
            print(f"import_chats: no Claude transcript dir at {src_dir} (skipped)")

    if do_codex:
        src_root = Path.home() / ".codex" / "sessions"
        out_dir = VAULT / "chats" / "codex"
        if src_root.is_dir():
            out_dir.mkdir(parents=True, exist_ok=True)
            n = 0
            here = norm(VAULT)
            for jp in sorted(src_root.rglob("*.jsonl")):
                if norm(codex_session_cwd(jp)) != here:
                    continue
                stem = jp.stem.replace("rollout-", "")[:27]
                out = out_dir / f"{stem}.md"
                if up_to_date(jp, out):
                    continue
                turns, meta = convert_codex(jp)
                if not turns:
                    continue
                out.write_text(render(f"Codex session {stem}", turns, meta,
                                      "python scripts/import_chats.py"), encoding="utf-8")
                print(f"wrote {out.relative_to(VAULT)}  ({len(turns)} turns)")
                n += 1
            print(f"import_chats: {n} Codex session(s) archived to chats/codex/")
            total += n
        else:
            print(f"import_chats: no Codex sessions dir at {src_root} (skipped)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
