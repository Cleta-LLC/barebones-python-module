"""SQLite persistence adapter for the recipes service."""

from pathlib import Path

from myapp.services.recipes.schemas import Recipe
from myapp.shared.config import DEFAULT_DB_PATH
from myapp.shared.persistence.sqlite_store import SqliteStore

TABLE_NAME = "recipes"


class RecipesSqliteStore(SqliteStore[Recipe]):
    """Concrete SQLite store for baking recipes."""

    def __init__(self, db_path: Path | None = None) -> None:
        super().__init__(db_path or DEFAULT_DB_PATH, TABLE_NAME, Recipe)
