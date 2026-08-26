#!/usr/bin/env python3
"""audit_public.py — fail if the repo contains content that should not be public.

Checks tracked and untracked-but-not-ignored files for:
  - obvious secrets (private key blocks, cloud/API tokens, hardcoded passwords)
  - machine-local absolute paths (Windows/macOS/Linux home directories)
  - Obsidian plugin/cache/workspace state tracked in git

Exit code 0 = clean, 1 = findings. Standard library only.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

TEXT_EXTENSIONS = {".md", ".txt", ".json", ".jsonl", ".yml", ".yaml", ".py",
                   ".sh", ".js", ".css", ".csv", ".gitignore"}
MAX_BYTES = 1_000_000

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("API secret key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("hardcoded password", re.compile(r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]{4,}['\"]")),
]

LOCAL_PATH_PATTERNS = [
    ("Windows user path", re.compile(r"\b[A-Za-z]:\\+Users\\+[^\\\s\"'<>|]+")),
    ("macOS user path", re.compile(r"(?<![\w/])/Users/[A-Za-z0-9_.-]+/")),
    ("Linux home path", re.compile(r"(?<![\w/])/home/[A-Za-z0-9_.-]+/")),
]

FORBIDDEN_TRACKED_PREFIXES = (
    ".obsidian/plugins/",
    ".obsidian/cache/",
    ".obsidian/logs/",
    ".obsidian/workspace",
)

# Vendored third-party skills legitimately contain example user paths in their
# reference data, so the machine-local-path heuristics are skipped there.
# Secret scanning still applies everywhere.
VENDORED_PREFIXES = (
    ".claude/skills/taste/",
    ".claude/skills/ui-ux-pro-max/",
    ".claude/skills/humanizer/",
    ".claude/skills/obsidian-",  # obsidian-markdown / -bases / -cli
    ".claude/skills/json-canvas/",
    ".claude/skills/defuddle/",
    ".claude/skills/graphify/",
)


def git_lines(args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return [line for line in out.stdout.splitlines() if line.strip()]


def candidate_files():
    """Tracked + untracked-not-ignored files; falls back to a walk without git."""
    listed = git_lines(["ls-files", "--cached", "--others", "--exclude-standard"])
    if listed is not None:
        return sorted(set(listed))
    found = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", ".obsidian/")) or rel.startswith("Raw/Files/"):
            continue
        found.append(rel)
    return found


def main():
    findings = []

    tracked = git_lines(["ls-files"]) or []
    for rel in tracked:
        if rel.startswith(FORBIDDEN_TRACKED_PREFIXES):
            findings.append((rel, "Obsidian plugin/cache/workspace state is tracked "
                             "in git — add it to .gitignore and untrack it"))

    for rel in candidate_files():
        path = ROOT / rel
        if path == SELF or not path.is_file():
            continue
        suffix = path.suffix.lower() or path.name
        if suffix not in TEXT_EXTENSIONS and path.name != ".gitignore":
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            findings.append((rel, f"unreadable: {exc}"))
            continue
        checks = SECRET_PATTERNS if rel.startswith(VENDORED_PREFIXES) \
            else SECRET_PATTERNS + LOCAL_PATH_PATTERNS
        for label, pattern in checks:
            m = pattern.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                findings.append((f"{rel}:{line}", label))

    for location, label in findings:
        print(f"AUDIT {location}: {label}")
    if findings:
        print(f"audit_public: FAILED ({len(findings)} finding(s))")
        return 1
    print("audit_public: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
