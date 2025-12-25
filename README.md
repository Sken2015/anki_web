# anki_web

# 公開サーバー
https://render.com

# データの吸い出し
cp ~/Library/Application\ Support/Anki2/ユーザー\ 1/collection.anki2 ~/Desktop/anki_web/data/collection.anki2
python3 export.py

# 内部ファイルを変更したら
git status
git add .
git commit -m "fix: update card logic"
git push