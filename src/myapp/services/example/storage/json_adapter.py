"""JSON persistence adapter for the example service."""

from pathlib import Path

from myapp.services.example.schemas import Item
from myapp.shared.config import JSON_DIR
from myapp.shared.persistence.json_store import JsonStore

DEFAULT_PATH = JSON_DIR / "example_items.json"


class ExampleJsonStore(JsonStore[Item]):
    """Concrete JSON store for example items."""

    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or DEFAULT_PATH, Item)
