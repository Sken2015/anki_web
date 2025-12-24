import sqlite3
import json
from pathlib import Path

# パス設定
DB_PATH = Path("data/collection.anki2")
OUT_PATH = Path("data/cards.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = """
    SELECT
        cards.id AS card_id,
        notes.id AS note_id,
        notes.flds,
        notes.tags
    FROM cards
    JOIN notes ON cards.nid = notes.id
    """

    cards = []

    for row in cur.execute(sql):
        fields = row["flds"].split("\x1f")

        card = {
            "card_id": row["card_id"],
            "note_id": row["note_id"],
            "front": fields[0] if len(fields) > 0 else "",
            "back": fields[1] if len(fields) > 1 else "",
            "tags": row["tags"].split() if row["tags"] else []
        }

        cards.append(card)

    conn.close()

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(cards)} cards → {OUT_PATH}")

if __name__ == "__main__":
    main()