"""Tests for the recipes service public API."""

from pathlib import Path

import pytest

from myapp.services.recipes.api import RecipesService
from myapp.services.recipes.schemas import Ingredient, Recipe, RecipeCreate, Unit
from myapp.shared.persistence.json_store import JsonStore


@pytest.fixture()
def svc(tmp_path: Path) -> RecipesService:
    store = JsonStore(tmp_path / "recipes.json", Recipe)
    return RecipesService(store=store)


class TestRecipesService:
    def test_create_recipe(self, svc: RecipesService) -> None:
        resp = svc.create(RecipeCreate(name="Quick Bread", category="bread"))
        assert resp.success
        assert resp.data["name"] == "Quick Bread"
        assert resp.data["id"]

    def test_create_with_ingredients(self, svc: RecipesService) -> None:
        resp = svc.create(
            RecipeCreate(
                name="Sugar Cookies",
                category="cookie",
                ingredients=[
                    Ingredient(id="i1", name="flour", quantity=2, unit=Unit.CUP),
                    Ingredient(id="i2", name="sugar", quantity=1, unit=Unit.CUP),
                ],
                steps=["Mix", "Bake"],
            )
        )
        assert resp.success
        assert len(resp.data["ingredients"]) == 2

    def test_get_recipe(self, svc: RecipesService) -> None:
        create_resp = svc.create(RecipeCreate(name="Cake"))
        recipe_id = create_resp.data["id"]
        resp = svc.get(recipe_id)
        assert resp.success
        assert resp.data["name"] == "Cake"

    def test_get_missing(self, svc: RecipesService) -> None:
        resp = svc.get("nope")
        assert not resp.success

    def test_list_recipes(self, svc: RecipesService) -> None:
        svc.create(RecipeCreate(name="A"))
        svc.create(RecipeCreate(name="B"))
        resp = svc.list_recipes()
        assert resp.success
        assert len(resp.data) == 2

    def test_delete_recipe(self, svc: RecipesService) -> None:
        create_resp = svc.create(RecipeCreate(name="Gone"))
        recipe_id = create_resp.data["id"]
        resp = svc.delete(recipe_id)
        assert resp.success
        assert svc.get(recipe_id).success is False

    def test_search_by_name(self, svc: RecipesService) -> None:
        svc.create(RecipeCreate(name="Banana Bread", category="bread"))
        svc.create(RecipeCreate(name="Chocolate Cake", category="cake"))
        resp = svc.search("banana")
        assert resp.success
        assert len(resp.data) == 1
        assert resp.data[0]["name"] == "Banana Bread"

    def test_search_by_category(self, svc: RecipesService) -> None:
        svc.create(RecipeCreate(name="A", category="bread"))
        svc.create(RecipeCreate(name="B", category="cake"))
        resp = svc.search("bread")
        assert len(resp.data) == 1

    def test_search_by_tag(self, svc: RecipesService) -> None:
        svc.create(RecipeCreate(name="A", tags=["beginner"]))
        svc.create(RecipeCreate(name="B", tags=["advanced"]))
        resp = svc.search("beginner")
        assert len(resp.data) == 1

    def test_search_no_matches(self, svc: RecipesService) -> None:
        resp = svc.search("nonexistent")
        assert resp.success
        assert len(resp.data) == 0


class TestSeed:
    def test_seed_loads_recipes(self, svc: RecipesService) -> None:
        resp = svc.seed()
        assert resp.success
        assert resp.data["seeded"] > 0

        all_resp = svc.list_recipes()
        assert len(all_resp.data) >= 5

    def test_seed_is_idempotent(self, svc: RecipesService) -> None:
        svc.seed()
        resp = svc.seed()
        assert resp.data["seeded"] == 0
        assert resp.data["skipped"] > 0


class TestExportImport:
    def test_roundtrip(self, tmp_path: Path) -> None:
        from myapp.shared.persistence.sqlite_store import SqliteStore

        src_store = SqliteStore(tmp_path / "src.db", "recipes", Recipe)
        src_svc = RecipesService(store=src_store)
        src_svc.create(
            RecipeCreate(
                id="export-test",
                name="Export Bread",
                ingredients=[Ingredient(id="i1", name="flour", quantity=3, unit=Unit.CUP)],
            )
        )

        json_store = JsonStore(tmp_path / "export.json", Recipe)
        for recipe in src_store.list_all():
            json_store.save(recipe)

        dst_store = JsonStore(tmp_path / "dst.json", Recipe)
        for recipe in json_store.list_all():
            dst_store.save(recipe)

        dst_svc = RecipesService(store=dst_store)
        resp = dst_svc.get("export-test")
        assert resp.success
        assert resp.data["name"] == "Export Bread"
        assert len(resp.data["ingredients"]) == 1
