#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"

ts() { date '+%Y-%m-%d %H:%M:%S'; }

# --- 二重起動・ロック残留の防止（macOSにflockが無いのでmkdir方式） ---
# mkdir はアトミック。既にロックがあっても、中のPIDが死んでいれば
# 残留とみなして掃除する（ハングした前回実行が永久に後続を弾くのを防ぐ）
LOCK_DIR="$SCRIPT_DIR/.update.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    oldpid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
    if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
        echo "$(ts) 別の実行が進行中 (pid=$oldpid) のためスキップ"
        exit 0
    fi
    # 前回実行は死んでいる → 残留ロックを掃除して取り直す
    echo "$(ts) 残留ロックを検出。掃除して続行"
    rm -rf "$LOCK_DIR"
    mkdir "$LOCK_DIR"
fi
echo $$ > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT

# データの吸い出し
python3 scripts/export.py

# 変更が無ければ何もしない（空コミットでエラーにしない）
if git diff --quiet && git diff --cached --quiet; then
    echo "$(ts) 変更なし。コミット/プッシュをスキップ"
    exit 0
fi

# コミット
git add .
git commit -m "fix: update card logic"

# push（credential入力待ちで固まらないようにする）
export GIT_TERMINAL_PROMPT=0

# macOSに timeout が無いので、バックグラウンド実行＋見張りプロセスで自前タイムアウト（120秒）
git push &
push_pid=$!
( sleep 120; kill "$push_pid" 2>/dev/null ) &
watcher_pid=$!

if wait "$push_pid"; then
    kill "$watcher_pid" 2>/dev/null || true
    echo "$(ts) push 成功"
else
    kill "$watcher_pid" 2>/dev/null || true
    echo "$(ts) git push 失敗（タイムアウト/ネットワーク/認証）。次回再試行"
    exit 1
fi
