#!/usr/bin/env python3
"""setup_vault.py — bootstrap this Cortex vault for a real project.

Two modes, both non-interactive (agents drive this; flags carry the answers):

NEW PROJECT
    python scripts/setup_vault.py --name "My Product" [--topic "core domain"]
        Seeds Wiki/Projects/<slug>.md + Wiki/Topics/<slug>.md from the
        templates, refreshes _relay/STATE.md's "Now" section, rebuilds the
        catalog, and reports next steps.

ADOPT AN EXISTING PROJECT (run from the vault root after dropping repos/media in)
    python scripts/setup_vault.py --inventory
        Scans the vault root for code repos (.git), media (video/audio), and
        documents (pdf/docx/pptx/md/txt), writes _relay/IMPORT-INVENTORY.md,
        and prints it. The `import-project` skill turns that inventory into
        Raw sources, Wiki notes, and graphify graphs.
    python scripts/setup_vault.py --gitignore-repos
        Appends `/repo-name/` lines to .gitignore for every detected repo so
        outside code is never committed into the vault's git.

EXTRAS
    python scripts/setup_vault.py --prune-demo
        Removes the built-in demo source + demo notes once you have real
        content, then rebuilds the catalog.
    python scripts/setup_vault.py --check
        Verifies optional tooling (git, graphify, crv, ffmpeg, node, codex)
        and prints what is missing and how to install it.
    python scripts/setup_vault.py --install
        Installs the missing optional tooling it can install for you
        (pip: graphifyy + claude-real-video; npm: defuddle; ffmpeg via
        winget/brew when available) and prints exact commands for the rest
        (Codex CLI, Claude Code plugins).

Standard library only. Safe to re-run; existing files are never overwritten.
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()

MEDIA_EXT = {".mp4", ".mkv", ".mov", ".webm", ".avi", ".wav", ".mp3", ".m4a", ".flac", ".ogg"}
DOC_EXT = {".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".csv", ".txt", ".html"}
SYSTEM_DIRS = {"Raw", "Wiki", "Schema", "_templates", "_relay", "scripts", "assets",
               "chats", "graphify", "tutorial", "node_modules"}

DEMO_FILES = [
    "Raw/Sources/cortex-system-demo.md",
    "Wiki/Topics/cortex.md",
    "Wiki/Concepts/raw-vs-compiled-knowledge.md",
    "Wiki/Concepts/the-relay.md",
    "Wiki/Concepts/three-layer-query-rule.md",
    "Wiki/Logs/cortex-demo-ingest.md",
]


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "project"


def fill_template(template_name, h1):
    tpl = (VAULT / "_templates" / template_name).read_text(encoding="utf-8")
    tpl = tpl.replace("created: YYYY-MM-DD", f"created: {TODAY}")
    tpl = tpl.replace("updated: YYYY-MM-DD", f"updated: {TODAY}")
    # Replace the first H1 with the real title.
    tpl = re.sub(r"^# .*$", f"# {h1}", tpl, count=1, flags=re.M)
    return tpl


def seed_note(rel_path, template_name, h1):
    out = VAULT / rel_path
    if out.exists():
        print(f"  skip  {rel_path} (already exists)")
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fill_template(template_name, h1), encoding="utf-8")
    print(f"  seed  {rel_path}")
    return True


def run_tool(*args):
    py = sys.executable or "python"
    return subprocess.run([py, str(VAULT / "scripts" / "wiki_tool.py"), *args],
                          cwd=str(VAULT)).returncode


def update_state_now(text_lines):
    state = VAULT / "_relay" / "STATE.md"
    if not state.is_file():
        return
    txt = state.read_text(encoding="utf-8")
    block = "\n".join(text_lines)
    new = re.sub(r"(^## Now\s*\n)(.*?)(?=^## |\Z)", rf"\g<1>{block}\n\n",
                 txt, count=1, flags=re.M | re.S)
    state.write_text(new, encoding="utf-8")


def detect_repos():
    repos = []
    for child in sorted(VAULT.iterdir()):
        if child.is_dir() and not child.name.startswith(".") and child.name not in SYSTEM_DIRS:
            if (child / ".git").exists():
                repos.append(child.name)
    return repos


def cmd_new(args):
    slug = slugify(args.name)
    topic = args.topic or args.name
    tslug = slugify(topic)
    print(f"setup: seeding project '{args.name}' (slug: {slug})")
    seed_note(f"Wiki/Projects/{slug}.md", "project-note.md", args.name)
    seed_note(f"Wiki/Topics/{tslug}.md", "topic-note.md", topic.title())
    update_state_now([
        f"- Project **{args.name}** initialized on {TODAY}.",
        f"- Project note: `Wiki/Projects/{slug}.md` · Topic hub: `Wiki/Topics/{tslug}.md`.",
        "- Next: fill in the project Goal + Next Steps, then ingest the first source.",
    ])
    print("setup: rebuilding catalog...")
    rc = run_tool("build")
    print("setup: done. Next steps:")
    print(f"  1. Open Wiki/Projects/{slug}.md and write the Goal + Next Steps.")
    print("  2. Ingest your first source (a doc, URL, or recording — see the "
          "llm-wiki-ingest / video-ingest skills).")
    print("  3. Run the gate: doctor, build, lint, source-lint, audit_public.")
    print("  4. Commit. From now on: catchup -> work -> save.")
    return rc


def cmd_inventory(_):
    repos, media, docs, loose_md = [], [], [], []
    for child in sorted(VAULT.iterdir()):
        if child.name.startswith(".") or child.name in SYSTEM_DIRS:
            continue
        if child.is_dir():
            if (child / ".git").exists():
                n_files = sum(1 for _ in child.rglob("*") if _.is_file())
                repos.append((child.name, n_files))
            else:
                for f in child.rglob("*"):
                    if f.is_file():
                        if f.suffix.lower() in MEDIA_EXT:
                            media.append(f.relative_to(VAULT))
                        elif f.suffix.lower() in DOC_EXT:
                            docs.append(f.relative_to(VAULT))
        elif child.is_file():
            if child.suffix.lower() in MEDIA_EXT:
                media.append(child.relative_to(VAULT))
            elif child.suffix.lower() in DOC_EXT:
                docs.append(child.relative_to(VAULT))
            elif child.suffix.lower() == ".md" and child.name not in (
                    "README.md", "CLAUDE.md", "AGENTS.md", "VAULT-GUIDE.md",
                    "GETTING-STARTED.md", "THIRD-PARTY-NOTICES.md"):
                loose_md.append(child.relative_to(VAULT))

    lines = ["# Import Inventory", "",
             f"> Generated by `python scripts/setup_vault.py --inventory` on {TODAY}.",
             "> The `import-project` skill consumes this file. Regenerate any time.",
             ""]
    lines.append("## Code repositories (candidates for graphify + gitignore)")
    lines += [f"- `{name}/` — {n} files" for name, n in repos] or ["- (none found)"]
    lines += ["", "## Media files (candidates for video-ingest)"]
    lines += [f"- `{p}`" for p in media[:100]] or ["- (none found)"]
    if len(media) > 100:
        lines.append(f"- ... and {len(media) - 100} more")
    lines += ["", "## Documents (candidates for Raw source ingest)"]
    lines += [f"- `{p}`" for p in docs[:200]] or ["- (none found)"]
    if len(docs) > 200:
        lines.append(f"- ... and {len(docs) - 200} more")
    lines += ["", "## Loose markdown at the vault root (file or ingest these)"]
    lines += [f"- `{p}`" for p in loose_md] or ["- (none found)"]
    lines.append("")
    out = VAULT / "_relay" / "IMPORT-INVENTORY.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"setup: inventory written to {out.relative_to(VAULT)}")
    return 0


def cmd_gitignore_repos(_):
    repos = detect_repos()
    if not repos:
        print("setup: no repos detected; .gitignore unchanged.")
        return 0
    gi = VAULT / ".gitignore"
    text = gi.read_text(encoding="utf-8") if gi.is_file() else ""
    added = []
    for r in repos:
        line = f"/{r}/"
        if line not in text:
            added.append(line)
    if added:
        text = text.rstrip("\n") + "\n\n# Tracked code repos live here but are NOT vault content\n" + "\n".join(added) + "\n"
        gi.write_text(text, encoding="utf-8")
    print(f"setup: gitignored {len(added)} repo folder(s): {', '.join(added) or 'none'}")
    return 0


def cmd_prune_demo(_):
    removed = 0
    for rel_str in DEMO_FILES:
        p = VAULT / rel_str
        if p.is_file():
            p.unlink()
            removed += 1
            print(f"  removed {rel_str}")
    if removed:
        run_tool("build")
        run_tool("source-scan", "--update")
        print(f"setup: pruned {removed} demo file(s) and rebuilt the catalog.")
    else:
        print("setup: no demo files present.")
    return 0


def find_codex():
    """The Codex CLI may be on PATH, or bundled by the Codex desktop app."""
    hit = shutil.which("codex")
    if hit:
        return hit
    local = Path.home() / "AppData" / "Local" / "OpenAI" / "Codex" / "bin"
    if local.is_dir():
        exes = sorted(local.glob("*/codex.exe"), key=lambda p: p.stat().st_mtime)
        if exes:
            return str(exes[-1])
    return None


def tooling_status():
    def have(cmd_name):
        return shutil.which(cmd_name) is not None
    return [
        # (label, present, manual hint, auto-install argv or None)
        ("git", have("git"), "https://git-scm.com", None),
        ("graphify (code graphs)", have("graphify"), "pip install graphifyy",
         [sys.executable, "-m", "pip", "install", "graphifyy"]),
        ("crv (video ingest)", have("crv"), "pip install claude-real-video",
         [sys.executable, "-m", "pip", "install", "claude-real-video"]),
        ("ffmpeg (video ingest)", have("ffmpeg"),
         "winget install Gyan.FFmpeg (Windows) / brew install ffmpeg (macOS) / https://ffmpeg.org",
         None),  # handled specially in --install
        ("node/npm (defuddle web clipping)", have("npm"), "https://nodejs.org", None),
        ("defuddle CLI", have("defuddle"), "npm install -g defuddle",
         ["npm", "install", "-g", "defuddle"] if have("npm") else None),
        ("codex CLI (sparring reviewer/builder)", find_codex() is not None,
         "npm install -g @openai/codex  (then `codex login`) — or the OpenAI Codex "
         "desktop app, which bundles it", None),
    ]


def cmd_check(_):
    checks = tooling_status()
    print(f"setup: tooling check (python {sys.version.split()[0]})")
    missing = 0
    for name, ok, hint, _auto in checks:
        print(f"  [{'OK ' if ok else '-- '}] {name}" + ("" if ok else f"   -> {hint}"))
        missing += 0 if ok else 1
    if missing:
        print(f"setup: {missing} missing — `python scripts/setup_vault.py --install` "
              "installs what it can and prints commands for the rest.")
        print("setup: core vault tooling needs ONLY python — everything above is "
              "optional and unlocks extra features.")
    else:
        print("setup: all tooling present.")
    print("setup: Claude Code plugin extras install from inside Claude Code: "
          "/design-setup (impeccable) and /docs-setup (Word/PDF/PowerPoint/Excel).")
    return 0


def runnable(argv):
    """Resolve argv[0] on PATH; route .cmd/.bat shims through cmd /c (Windows
    CreateProcess can't launch them directly)."""
    exe = shutil.which(argv[0])
    if not exe:
        return None
    if exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", exe] + list(argv[1:])
    return [exe] + list(argv[1:])


def cmd_install(_):
    import subprocess
    checks = tooling_status()
    manual = []
    for name, ok, hint, auto in checks:
        if ok:
            print(f"  [OK ] {name}")
            continue
        if name.startswith("ffmpeg"):
            argv = None
            if shutil.which("winget"):
                argv = ["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                        "--accept-source-agreements", "--accept-package-agreements"]
            elif shutil.which("brew"):
                argv = ["brew", "install", "ffmpeg"]
            auto = argv
        auto = runnable(auto) if auto else None
        if not auto:
            manual.append((name, hint))
            print(f"  [-- ] {name}   -> install manually: {hint}")
            continue
        print(f"  [.. ] {name}   -> running: {' '.join(auto)}")
        try:
            r = subprocess.run(auto, timeout=600)
            print(f"  [{'OK ' if r.returncode == 0 else '!! '}] {name} "
                  f"({'installed' if r.returncode == 0 else f'installer exited {r.returncode}'})")
            if r.returncode != 0:
                manual.append((name, hint))
        except Exception as exc:  # noqa: BLE001
            print(f"  [!! ] {name} install failed ({type(exc).__name__}) -> {hint}")
            manual.append((name, hint))
    if manual:
        print("setup: still needed manually:")
        for name, hint in manual:
            print(f"  - {name}: {hint}")
    print("setup: re-run `--check` to confirm. Claude Code plugin extras: "
          "/design-setup and /docs-setup from inside Claude Code.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Bootstrap this Cortex vault")
    ap.add_argument("--name", help="project name (new-project mode)")
    ap.add_argument("--topic", help="main topic/domain (defaults to --name)")
    ap.add_argument("--inventory", action="store_true", help="scan for importable content")
    ap.add_argument("--gitignore-repos", action="store_true", help="gitignore detected repos")
    ap.add_argument("--prune-demo", action="store_true", help="remove the demo content")
    ap.add_argument("--check", action="store_true", help="verify optional tooling")
    ap.add_argument("--install", action="store_true",
                    help="install missing optional tooling (pip/npm/winget/brew)")
    args = ap.parse_args()

    if args.inventory:
        return cmd_inventory(args)
    if args.gitignore_repos:
        return cmd_gitignore_repos(args)
    if args.prune_demo:
        return cmd_prune_demo(args)
    if args.check:
        return cmd_check(args)
    if args.install:
        return cmd_install(args)
    if args.name:
        return cmd_new(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
