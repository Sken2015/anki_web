import sqlite3
import json
import random
from pathlib import Path

# パス設定
ANKI_DB_PATH = Path.home() / "Library/Application Support/Anki2/ユーザー 1/collection.anki2"
OUT_PATH = Path(__file__).parent.parent / "data/cards.json"


def load_deck_map(cur):
    rows = cur.execute("SELECT id, name FROM decks").fetchall()
    return {row[0]: row[1].split("::")[-1] for row in rows}


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

    deck_map = load_deck_map(cur)

    sql_all = """
    SELECT
        cards.id AS card_id,
        cards.did AS deck_id,
        notes.id AS note_id,
        notes.flds,
        notes.tags
    FROM cards
    JOIN notes ON cards.nid = notes.id
    """

    rows = cur.execute(sql_all).fetchall()
    conn.close()

    def to_card(row):
        fields = row["flds"].split("\x1f")
        return {
            "card_id": row["card_id"],
            "note_id": row["note_id"],
            "deck": deck_map.get(row["deck_id"], ""),
            "front": fields[0] if len(fields) > 0 else "",
            "back": fields[1] if len(fields) > 1 else "",
            "tags": row["tags"].split() if row["tags"] else []
        }

    all_cards = [to_card(r) for r in rows]

    # 短答 = デッキ名に「短答」を含む / 論証 = それ以外（論証・要件事実 等）
    tanto = [c for c in all_cards if "短答" in c["deck"]]
    ronsho = [c for c in all_cards if "短答" not in c["deck"]]

    TANTO_N = 100
    RONSHO_N = 50
    n_tanto = min(TANTO_N, len(tanto))
    n_ronsho = min(RONSHO_N, len(ronsho))

    cards = random.sample(tanto, n_tanto) + random.sample(ronsho, n_ronsho)
    random.shuffle(cards)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(cards)} cards (短答{n_tanto} + 論証{n_ronsho}) → {OUT_PATH}")

if __name__ == "__main__":
    main()