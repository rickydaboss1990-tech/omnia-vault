#!/usr/bin/env python3
"""sync_graphs.py — refresh the vault's committed Graphify snapshots from the repos.

For each tracked code repo living in this vault folder: (optionally) rebuild its
code graph with `graphify update` (AST-only, fast, no LLM), then copy the fresh
graph.json + GRAPH_REPORT into the vault snapshot at graphify/<repo>/ so the
3-layer query tools read current code.

Repos are AUTO-DETECTED: any top-level folder in the vault that has its own
`.git/` or an existing `graphify-out/` is treated as a tracked repo. Pass repo
folder names as arguments to override detection.

The per-node Obsidian `.md` notes are NOT regenerated here — that needs a full
`/graphify <repo> --obsidian` export; run that periodically if you want the
browsable notes refreshed. Standard library only.

Usage:
    python scripts/sync_graphs.py                  # auto-detect, rebuild + copy
    python scripts/sync_graphs.py --no-rebuild     # copy existing graphify-out only
    python scripts/sync_graphs.py my-app my-api    # explicit repo folder names
"""

import shutil
import subprocess
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
REBUILD = "--no-rebuild" not in sys.argv
EXPLICIT = [a for a in sys.argv[1:] if not a.startswith("--")]

# Vault system folders that are never code repos.
SYSTEM_DIRS = {
    "Raw", "Wiki", "Schema", "_templates", "_relay", "scripts", "assets",
    "chats", "graphify", "tutorial", "node_modules",
}


def detect_repos():
    repos = []
    for child in sorted(VAULT.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in SYSTEM_DIRS:
            continue
        if (child / ".git").exists() or (child / "graphify-out").is_dir():
            repos.append(child.name)
    return repos


def try_rebuild(repo_path):
    try:
        r = subprocess.run(["graphify", "update", str(repo_path)], cwd=str(repo_path),
                           capture_output=True, text=True, timeout=600)
        return "rebuilt" if r.returncode == 0 else f"update-failed(rc={r.returncode})"
    except FileNotFoundError:
        return "graphify-not-on-PATH (copy-only)"
    except Exception as exc:  # noqa: BLE001
        return f"update-error({type(exc).__name__})"


def main():
    repos = EXPLICIT or detect_repos()
    if not repos:
        print("sync_graphs: no code repos detected in the vault root (nothing to do).")
        print("  A repo = a top-level folder with its own .git/ or graphify-out/.")
        return 0
    any_repo = False
    for repo in repos:
        repo_path = VAULT / repo
        out = repo_path / "graphify-out"
        dst = VAULT / "graphify" / repo
        if not out.is_dir():
            print(f"{repo}: no graphify-out/ yet — run `/graphify {repo}` once to build "
                  "its graph (skipped)")
            continue
        any_repo = True
        status = try_rebuild(repo_path) if REBUILD else "copy-only"
        copied = []
        for src_name, dst_name in [("graph.json", "graph.json"),
                                   ("GRAPH_REPORT.md", "_GRAPH_REPORT.md")]:
            src = out / src_name
            if src.is_file():
                dst.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst / dst_name)
                copied.append(dst_name)
        print(f"{repo}: {status}; synced [{', '.join(copied) or 'nothing'}]")
    print("sync_graphs: done" if any_repo else "sync_graphs: repos found but none built yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
