"""SQLite persistence adapter for the example service."""

from pathlib import Path

from myapp.services.example.schemas import Item
from myapp.shared.config import DEFAULT_DB_PATH
from myapp.shared.persistence.sqlite_store import SqliteStore

TABLE_NAME = "example_items"


class ExampleSqliteStore(SqliteStore[Item]):
    """Concrete SQLite store for example items."""

    def __init__(self, db_path: Path | None = None) -> None:
        super().__init__(db_path or DEFAULT_DB_PATH, TABLE_NAME, Item)
