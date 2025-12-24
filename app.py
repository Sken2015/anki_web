from flask import Flask, render_template
import json
from pathlib import Path

app = Flask(__name__)

DATA_PATH = Path("data/cards.json")

@app.route("/")
def index():
    with open(DATA_PATH, encoding="utf-8") as f:
        cards = json.load(f)
    return render_template("index.html", cards=cards)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)