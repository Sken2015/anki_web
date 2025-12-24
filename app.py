import json
import os
from flask import Flask, jsonify

app = Flask(__name__)
DATA_PATH = "data/cards.json"

@app.route("/")
def index():
    if not os.path.exists(DATA_PATH):
        return jsonify({
            "status": "ok",
            "message": "cards.json not found yet",
            "cards": []
        })

    with open(DATA_PATH, encoding="utf-8") as f:
        cards = json.load(f)

    return jsonify(cards)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)