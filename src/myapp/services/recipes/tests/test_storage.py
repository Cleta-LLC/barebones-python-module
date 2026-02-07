"""Tests for recipes JSON and SQLite storage backends."""

import json
from pathlib import Path

import pytest

from myapp.services.recipes.schemas import Ingredient, Recipe, Unit
from myapp.shared.persistence.json_store import JsonStore
from myapp.shared.persistence.sqlite_store import SqliteStore


def _make_recipe(id: str = "r1", name: str = "Test Bread") -> Recipe:
    return Recipe(
        id=id,
        name=name,
        category="bread",
        ingredients=[Ingredient(id="i1", name="flour", quantity=2, unit=Unit.CUP)],
        steps=["Mix", "Bake"],
        prep_time_minutes=10,
        cook_time_minutes=30,
        servings=4,
        temperature_f=350,
        tags=["test"],
    )


# ── JSON store ────────────────────────────────────────────────────────


class TestRecipeJsonStore:
    @pytest.fixture()
    def store(self, tmp_path: Path) -> JsonStore[Recipe]:
        return JsonStore(tmp_path / "recipes.json", Recipe)

    def test_save_and_get(self, store: JsonStore[Recipe]) -> None:
        store.save(_make_recipe())
        fetched = store.get("r1")
        assert fetched is not None
        assert fetched.name == "Test Bread"
        assert len(fetched.ingredients) == 1

    def test_list_all(self, store: JsonStore[Recipe]) -> None:
        store.save(_make_recipe("a", "A"))
        store.save(_make_recipe("b", "B"))
        assert len(store.list_all()) == 2

    def test_delete(self, store: JsonStore[Recipe]) -> None:
        store.save(_make_recipe())
        assert store.delete("r1") is True
        assert store.get("r1") is None

    def test_roundtrip_preserves_nested(self, store: JsonStore[Recipe]) -> None:
        original = _make_recipe()
        store.save(original)
        restored = store.get("r1")
        assert restored is not None
        assert restored.ingredients[0].name == "flour"
        assert restored.ingredients[0].unit == Unit.CUP
        assert restored.steps == ["Mix", "Bake"]
        assert restored.tags == ["test"]

    def test_atomic_write(self, tmp_path: Path) -> None:
        store = JsonStore(tmp_path / "atomic.json", Recipe)
        store.save(_make_recipe("1", "One"))
        store.save(_make_recipe("2", "Two"))
        raw = json.loads((tmp_path / "atomic.json").read_text())
        assert "1" in raw
        assert "2" in raw


# ── SQLite store ──────────────────────────────────────────────────────


class TestRecipeSqliteStore:
    @pytest.fixture()
    def store(self, tmp_path: Path) -> SqliteStore[Recipe]:
        return SqliteStore(tmp_path / "test.db", "recipes", Recipe)

    def test_save_and_get(self, store: SqliteStore[Recipe]) -> None:
        store.save(_make_recipe())
        fetched = store.get("r1")
        assert fetched is not None
        assert fetched.name == "Test Bread"

    def test_list_all(self, store: SqliteStore[Recipe]) -> None:
        store.save(_make_recipe("a", "A"))
        store.save(_make_recipe("b", "B"))
        assert len(store.list_all()) == 2

    def test_delete(self, store: SqliteStore[Recipe]) -> None:
        store.save(_make_recipe())
        assert store.delete("r1") is True
        assert store.get("r1") is None

    def test_upsert(self, store: SqliteStore[Recipe]) -> None:
        store.save(_make_recipe("u", "V1"))
        store.save(Recipe(id="u", name="V2"))
        fetched = store.get("u")
        assert fetched is not None
        assert fetched.name == "V2"

    def test_roundtrip_preserves_nested(self, store: SqliteStore[Recipe]) -> None:
        original = _make_recipe()
        store.save(original)
        restored = store.get("r1")
        assert restored is not None
        assert len(restored.ingredients) == 1
        assert restored.ingredients[0].unit == Unit.CUP
        assert restored.steps == ["Mix", "Bake"]
