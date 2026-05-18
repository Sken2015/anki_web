import sqlite3
import json
import random
from pathlib import Path

# パス設定
ANKI_DB_PATH = Path.home() / "Library/Application Support/Anki2/ユーザー 1/collection.anki2"
OUT_PATH = Path(__file__).parent.parent / "data/cards.json"

def main():
    # Ankiが開いていても backup API でWAL込みの一貫したスナップショットをメモリ上に取得
    src = sqlite3.connect(str(ANKI_DB_PATH))
    src.create_collation("unicase", lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))

    conn = sqlite3.connect(":memory:")
    conn.create_collation("unicase", lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
    src.backup(conn)
    src.close()

    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql_random = """
    SELECT
        cards.id AS card_id,
        notes.id AS note_id,
        notes.flds,
        notes.tags
    FROM cards
    JOIN notes ON cards.nid = notes.id
    ORDER BY RANDOM()
    LIMIT 200
    """

    sql_fallback = """
    SELECT
        cards.id AS card_id,
        notes.id AS note_id,
        notes.flds,
        notes.tags
    FROM cards
    JOIN notes ON cards.nid = notes.id
    LIMIT 2000
    """

    try:
        rows = cur.execute(sql_random).fetchall()
    except sqlite3.DatabaseError:
        rows = cur.execute(sql_fallback).fetchall()
    cards = []

    for row in rows:
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

    if len(cards) > 200:
        cards = random.sample(cards, 200)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(cards)} cards → {OUT_PATH}")

if __name__ == "__main__":
    main()