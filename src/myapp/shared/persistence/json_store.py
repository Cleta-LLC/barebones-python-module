"""JSON file-based persistence backend.

Writes are atomic: data is written to a temporary file first,
then atomically moved into place via ``os.replace``.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from myapp.shared.persistence.base import BaseStore

T = TypeVar("T", bound=BaseModel)


class JsonStore(BaseStore[T], Generic[T]):
    """Store records as a JSON object keyed by ``id``."""

    def __init__(self, path: Path, model_class: type[T]) -> None:
        self.path = path
        self.model_class = model_class
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # -- internal helpers --------------------------------------------------

    def _read_all(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        text = self.path.read_text(encoding="utf-8")
        if not text.strip():
            return {}
        return json.loads(text)  # type: ignore[no-any-return]

    def _write_all(self, data: dict[str, dict]) -> None:
        """Atomic write: tmp file -> os.replace."""
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, default=str)
                fh.write("\n")
            os.replace(tmp, self.path)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    # -- public API --------------------------------------------------------

    def get(self, record_id: str) -> T | None:
        data = self._read_all()
        raw = data.get(record_id)
        if raw is None:
            return None
        return self.model_class.model_validate(raw)

    def list_all(self) -> list[T]:
        data = self._read_all()
        return [self.model_class.model_validate(v) for v in data.values()]

    def save(self, item: T) -> T:
        data = self._read_all()
        item_dict = item.model_dump(mode="json")
        data[item_dict["id"]] = item_dict
        self._write_all(data)
        return item

    def delete(self, record_id: str) -> bool:
        data = self._read_all()
        if record_id not in data:
            return False
        del data[record_id]
        self._write_all(data)
        return True
