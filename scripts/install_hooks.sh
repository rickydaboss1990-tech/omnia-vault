#!/usr/bin/env sh
# Point git at the versioned hooks in .githooks/ so the pre-commit
# maintenance gate runs automatically.
set -e
cd "$(dirname "$0")/.."
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit 2>/dev/null || true
echo "Git hooks installed: core.hooksPath -> .githooks"
