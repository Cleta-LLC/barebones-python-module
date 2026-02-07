"""SQLite persistence backend.

Uses WAL journal mode for safe concurrent reads and
wraps all mutations in transactions.
"""

import sqlite3
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from myapp.shared.persistence.base import BaseStore

T = TypeVar("T", bound=BaseModel)


class SqliteStore(BaseStore[T], Generic[T]):
    """Store records in a SQLite table as JSON blobs."""

    def __init__(self, db_path: Path, table_name: str, model_class: type[T]) -> None:
        self.db_path = db_path
        self.table_name = table_name
        self.model_class = model_class
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS [{self.table_name}] ("
                "  id TEXT PRIMARY KEY,"
                "  data TEXT NOT NULL,"
                "  created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
                "  updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
                ")"
            )

    # -- public API --------------------------------------------------------

    def get(self, record_id: str) -> T | None:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT data FROM [{self.table_name}] WHERE id = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            return None
        return self.model_class.model_validate_json(row[0])

    def list_all(self) -> list[T]:
        with self._connect() as conn:
            rows = conn.execute(f"SELECT data FROM [{self.table_name}]").fetchall()
        return [self.model_class.model_validate_json(r[0]) for r in rows]

    def save(self, item: T) -> T:
        item_json = item.model_dump_json()
        item_dict = item.model_dump()
        with self._connect() as conn:
            conn.execute(
                f"INSERT INTO [{self.table_name}] (id, data, updated_at) "
                "VALUES (?, ?, CURRENT_TIMESTAMP) "
                "ON CONFLICT(id) DO UPDATE SET "
                "  data = excluded.data,"
                "  updated_at = CURRENT_TIMESTAMP",
                (item_dict["id"], item_json),
            )
        return item

    def delete(self, record_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                f"DELETE FROM [{self.table_name}] WHERE id = ?",
                (record_id,),
            )
        return cursor.rowcount > 0
