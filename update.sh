#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# データの吸い出し
cp ~/Library/Application\ Support/Anki2/ユーザー\ 1/collection.anki2 data/collection.anki2
python3 export.py

# コミット＆プッシュ
git add .
git commit -m "fix: update card logic"
git push
