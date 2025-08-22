from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import sqlite3

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS cards(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question   TEXT NOT NULL,
  answer     TEXT NOT NULL,
  source_ref TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_id     INTEGER NOT NULL,
  quality     INTEGER NOT NULL CHECK(quality BETWEEN 0 AND 5),
  interval    INTEGER NOT NULL,
  ease        REAL    NOT NULL,
  next_due_at TIMESTAMP NOT NULL,
  reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(card_id) REFERENCES cards(id)
);
"""


class Store:
    def __init__(self, db_path: str | Path = "learn.db") -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as c:
            c.executescript(SCHEMA)

    def add_cards(self, cards: Iterable[tuple[str, str, str | None]]) -> int:
        """cards: iterable of (question, answer, source_ref)"""
        with sqlite3.connect(self.db_path) as c:
            cur = c.executemany(
                "INSERT INTO cards(question, answer, source_ref) VALUES(?,?,?)",
                cards,
            )
            return cur.rowcount or 0

    def get_due_cards(self, now_iso: str) -> list[tuple[int, str, str]]:
        q = """
        SELECT id, question, answer FROM cards
        WHERE id NOT IN (SELECT DISTINCT card_id FROM reviews)
           OR id IN (
                 SELECT card_id FROM reviews
                 GROUP BY card_id
                 HAVING MAX(next_due_at) <= ?
             )
        ORDER BY id
        """
        with sqlite3.connect(self.db_path) as c:
            return c.execute(q, (now_iso,)).fetchall()

    def get_last_state(self, card_id: int) -> tuple[int, float] | None:
        q = """
        SELECT interval, ease
        FROM reviews
        WHERE card_id=?
        ORDER BY reviewed_at DESC, id DESC
        LIMIT 1
        """
        with sqlite3.connect(self.db_path) as c:
            row = c.execute(q, (card_id,)).fetchone()
            return (row[0], row[1]) if row else None

    def add_review(
        self,
        card_id: int,
        quality: int,
        interval: int,
        ease: float,
        next_due_iso: str,
    ) -> None:
        with sqlite3.connect(self.db_path) as c:
            c.execute(
                (
                    "INSERT INTO reviews("
                    "card_id, quality, interval, ease, next_due_at"
                    ") VALUES(?,?,?,?,?)"
                ),
                (card_id, quality, interval, ease, next_due_iso),
            )
