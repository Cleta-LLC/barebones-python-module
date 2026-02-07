"""Tests for JSON and SQLite storage backends."""

from pathlib import Path

import pytest

from myapp.services.example.schemas import Item
from myapp.shared.persistence.json_store import JsonStore
from myapp.shared.persistence.sqlite_store import SqliteStore


def _make_item(id: str = "t1", name: str = "Test") -> Item:
    return Item(id=id, name=name, description="desc", tags=["a"])


# ── JSON store ────────────────────────────────────────────────────────


class TestJsonStore:
    @pytest.fixture()
    def store(self, tmp_path: Path) -> JsonStore[Item]:
        return JsonStore(tmp_path / "items.json", Item)

    def test_save_and_get(self, store: JsonStore[Item]) -> None:
        item = _make_item()
        store.save(item)
        fetched = store.get("t1")
        assert fetched is not None
        assert fetched.id == "t1"
        assert fetched.name == "Test"

    def test_list_all(self, store: JsonStore[Item]) -> None:
        store.save(_make_item("a", "A"))
        store.save(_make_item("b", "B"))
        assert len(store.list_all()) == 2

    def test_delete(self, store: JsonStore[Item]) -> None:
        store.save(_make_item())
        assert store.delete("t1") is True
        assert store.get("t1") is None
        assert store.delete("t1") is False

    def test_get_missing(self, store: JsonStore[Item]) -> None:
        assert store.get("nope") is None

    def test_atomic_write_no_corruption(self, tmp_path: Path) -> None:
        """File should always be valid JSON after a write."""
        store = JsonStore(tmp_path / "atomic.json", Item)
        store.save(_make_item("1", "One"))
        store.save(_make_item("2", "Two"))
        import json

        raw = json.loads((tmp_path / "atomic.json").read_text())
        assert "1" in raw
        assert "2" in raw

    def test_roundtrip_preserves_data(self, store: JsonStore[Item]) -> None:
        original = _make_item("rt", "Roundtrip")
        store.save(original)
        restored = store.get("rt")
        assert restored is not None
        assert restored.name == original.name
        assert restored.tags == original.tags


# ── SQLite store ──────────────────────────────────────────────────────


class TestSqliteStore:
    @pytest.fixture()
    def store(self, tmp_path: Path) -> SqliteStore[Item]:
        return SqliteStore(tmp_path / "test.db", "items", Item)

    def test_save_and_get(self, store: SqliteStore[Item]) -> None:
        item = _make_item()
        store.save(item)
        fetched = store.get("t1")
        assert fetched is not None
        assert fetched.id == "t1"

    def test_list_all(self, store: SqliteStore[Item]) -> None:
        store.save(_make_item("a", "A"))
        store.save(_make_item("b", "B"))
        assert len(store.list_all()) == 2

    def test_delete(self, store: SqliteStore[Item]) -> None:
        store.save(_make_item())
        assert store.delete("t1") is True
        assert store.get("t1") is None
        assert store.delete("t1") is False

    def test_get_missing(self, store: SqliteStore[Item]) -> None:
        assert store.get("nope") is None

    def test_upsert(self, store: SqliteStore[Item]) -> None:
        store.save(_make_item("u", "V1"))
        store.save(Item(id="u", name="V2"))
        fetched = store.get("u")
        assert fetched is not None
        assert fetched.name == "V2"

    def test_roundtrip_preserves_data(self, store: SqliteStore[Item]) -> None:
        original = _make_item("rt", "Roundtrip")
        store.save(original)
        restored = store.get("rt")
        assert restored is not None
        assert restored.name == original.name
        assert restored.tags == original.tags
