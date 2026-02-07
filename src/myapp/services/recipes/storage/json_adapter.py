"""JSON persistence adapter for the recipes service."""

from pathlib import Path

from myapp.services.recipes.schemas import Recipe
from myapp.shared.config import JSON_DIR
from myapp.shared.persistence.json_store import JsonStore

DEFAULT_PATH = JSON_DIR / "recipes.json"


class RecipesJsonStore(JsonStore[Recipe]):
    """Concrete JSON store for baking recipes."""

    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or DEFAULT_PATH, Recipe)
