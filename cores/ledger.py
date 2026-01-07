import sqlite3
from datetime import date
from pathlib import Path

from .structure import datastruct

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    note TEXT NOT NULL,
    date TEXT NOT NULL
);
"""


class Ledger:
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(SCHEMA_SQL)

    def add(self, tx: datastruct) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO transactions (amount, type, category, note, date) "
                "VALUES (?, ?, ?, ?, ?)",
                (tx.amount, tx.type, tx.category, tx.note, tx.date.isoformat()),
            )

    def list(self) -> list[datastruct]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, amount, type, category, note, date "
                "FROM transactions ORDER BY id"
            ).fetchall()
        return [
            datastruct(
                id=row["id"],
                amount=row["amount"],
                type=row["type"],
                category=row["category"],
                note=row["note"],
                date=date.fromisoformat(row["date"]),
            )
            for row in rows
        ]

    def delete(self, tx_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
            return cur.rowcount > 0
