import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)
DATA_PATH = "data/cards.json"

# 出題モード（全部 / 短答のみ / 論証のみ）
MODES = {
    "all":    {"label": "全部", "path": "/"},
    "tanto":  {"label": "短答", "path": "/tanto"},
    "ronsho": {"label": "論証", "path": "/ronsho"},
}


def load_cards():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def select_cards(cards, mode):
    if mode == "tanto":
        return [c for c in cards if "短答" in c.get("deck", "")]
    if mode == "ronsho":
        # 論証扱い = 短答以外（論証・民事要件事実 等を含む）
        return [c for c in cards if "短答" not in c.get("deck", "")]
    return cards


def render_mode(mode):
    cards = select_cards(load_cards(), mode)
    if not cards:
        return "カードがまだありません"

    # ランダム200枚（cards.json の並び順）を i 番目から順番に出題する
    i = request.args.get("i", default=0, type=int) % len(cards)
    return render_template(
        "card.html",
        card=cards[i],
        index=i,
        total=len(cards),
        mode=mode,
        modes=MODES,
        base=MODES[mode]["path"],
    )


@app.route("/")
def index():
    return render_mode("all")


@app.route("/tanto")
def tanto():
    return render_mode("tanto")


@app.route("/ronsho")
def ronsho():
    return render_mode("ronsho")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
