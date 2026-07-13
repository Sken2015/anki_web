# anki_web

# 場所
~/anki_web
※ iCloud同期による git ロック競合(Resource deadlock avoided)を避けるため、
  Desktop配下ではなく ~/anki_web に置くこと。

# 公開サーバー
https://render.com

# ローカル起動
cd ~/anki_web
python3 app.py   # http://localhost:8000

# データの吸い出し（Ankiアプリ本体のDBを直接読む）
cd ~/anki_web
python3 scripts/export.py

# 手動で今すぐ更新（export → commit → push）
bash ~/anki_web/scripts/update.sh

# 自動更新
launchd (com.sugi.anki-scheduler) が毎朝6:00に scripts/update.sh を実行。
  今すぐ実行:   launchctl kickstart -p gui/$(id -u)/com.sugi.anki-scheduler
  状態確認:     launchctl list | grep anki   # 2列目が0なら正常
  ログ:         ~/Library/Logs/anki-scheduler.log

# 内部ファイルを変更したら
git status
git add .
git commit -m "fix: update card logic"
git push
