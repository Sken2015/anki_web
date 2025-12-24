import json
import os
import random
from flask import Flask, render_template, request

app = Flask(__name__)
DATA_PATH = "data/cards.json"


def load_cards():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    cards = load_cards()
    if not cards:
        return "カードがまだありません"

    card_id = random.randrange(len(cards))
    return render_template(
        "card.html",
        card=cards[card_id],
        show_back=False,
        card_id=card_id
    )


@app.route("/show")
def show():
    cards = load_cards()
    card_id = int(request.args.get("id"))
    return render_template(
        "card.html",
        card=cards[card_id],
        show_back=True,
        card_id=card_id
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)