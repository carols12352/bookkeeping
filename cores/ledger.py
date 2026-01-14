import sqlite3
from datetime import date
from pathlib import Path

from .structure import Transaction

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

    def add(self, tx: Transaction) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO transactions (amount, type, category, note, date) "
                "VALUES (?, ?, ?, ?, ?)",
                (tx.amount, tx.type, tx.category, tx.note, tx.date.isoformat()),
            )

    def list(
        self,
        tx_type: str | None = None,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int | None = None,
    ) -> list[Transaction]:
        where = []
        params: list[object] = []
        if tx_type:
            where.append("type = ?")
            params.append(tx_type)
        if category:
            where.append("category = ?")
            params.append(category)
        if start_date:
            where.append("date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            where.append("date <= ?")
            params.append(end_date.isoformat())

        query = (
            "SELECT id, amount, type, category, note, date "
            "FROM transactions"
        )
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY date, id"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            Transaction(
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

    def summary(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, object]:
        where = []
        params: list[object] = []
        if start_date:
            where.append("date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            where.append("date <= ?")
            params.append(end_date.isoformat())
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        with self._connect() as conn:
            totals_rows = conn.execute(
                "SELECT type, SUM(amount) AS total "
                "FROM transactions"
                f"{where_sql} "
                "GROUP BY type",
                params,
            ).fetchall()
            category_rows = conn.execute(
                "SELECT category, type, SUM(amount) AS total "
                "FROM transactions"
                f"{where_sql} "
                "GROUP BY category, type "
                "ORDER BY category",
                params,
            ).fetchall()

        income_total = 0.0
        expense_total = 0.0
        for row in totals_rows:
            if row["type"] == "income":
                income_total = row["total"] or 0.0
            elif row["type"] == "expense":
                expense_total = row["total"] or 0.0

        categories: dict[str, dict[str, float]] = {}
        for row in category_rows:
            category = row["category"]
            categories.setdefault(
                category, {"income": 0.0, "expense": 0.0, "balance": 0.0}
            )
            if row["type"] == "income":
                categories[category]["income"] = row["total"] or 0.0
            elif row["type"] == "expense":
                categories[category]["expense"] = row["total"] or 0.0
            categories[category]["balance"] = (
                categories[category]["income"] - categories[category]["expense"]
            )

        return {
            "income": income_total,
            "expense": expense_total,
            "balance": income_total - expense_total,
            "categories": categories,
        }
