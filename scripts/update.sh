#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"

# データの吸い出し
python3 scripts/export.py

# コミット＆プッシュ
git add .
git commit -m "fix: update card logic"
git push
