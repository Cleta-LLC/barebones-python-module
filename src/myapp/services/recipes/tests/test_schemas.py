"""Tests for recipe schemas."""

import pytest
from pydantic import ValidationError

from myapp.services.recipes.schemas import Ingredient, Recipe, RecipeCreate, Unit


class TestIngredient:
    def test_valid_ingredient(self) -> None:
        ing = Ingredient(id="i1", name="flour", quantity=2, unit=Unit.CUP)
        assert ing.name == "flour"
        assert ing.quantity == 2
        assert ing.unit == Unit.CUP

    def test_quantity_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            Ingredient(id="i1", name="flour", quantity=0, unit=Unit.CUP)

    def test_name_required(self) -> None:
        with pytest.raises(ValidationError):
            Ingredient(id="i1", name="", quantity=1)


class TestRecipe:
    def test_minimal_recipe(self) -> None:
        r = Recipe(id="r1", name="Test Bread")
        assert r.name == "Test Bread"
        assert r.category == "other"
        assert r.servings == 1
        assert r.ingredients == []
        assert r.steps == []
        assert r.schema_version == 1

    def test_full_recipe(self) -> None:
        r = Recipe(
            id="r2",
            name="Cake",
            description="Chocolate cake",
            category="cake",
            ingredients=[Ingredient(id="i1", name="flour", quantity=2, unit=Unit.CUP)],
            steps=["Mix", "Bake"],
            prep_time_minutes=15,
            cook_time_minutes=30,
            servings=8,
            temperature_f=350,
            tags=["chocolate"],
        )
        assert len(r.ingredients) == 1
        assert len(r.steps) == 2
        assert r.total_time_minutes == 45
        assert r.temperature_c == 177

    def test_temperature_conversion(self) -> None:
        r = Recipe(id="r3", name="Bread", temperature_f=450)
        assert r.temperature_c == 232

    def test_temperature_none(self) -> None:
        r = Recipe(id="r4", name="No-bake")
        assert r.temperature_f is None
        assert r.temperature_c is None

    def test_empty_steps_filtered(self) -> None:
        r = Recipe(id="r5", name="Test", steps=["Mix", "", "  ", "Bake"])
        assert r.steps == ["Mix", "Bake"]

    def test_roundtrip_json(self) -> None:
        r = Recipe(
            id="rt",
            name="Roundtrip",
            ingredients=[Ingredient(id="i1", name="sugar", quantity=1, unit=Unit.CUP)],
            steps=["Step 1"],
            tags=["test"],
        )
        raw = r.model_dump_json()
        restored = Recipe.model_validate_json(raw)
        assert restored.id == r.id
        assert restored.name == r.name
        assert len(restored.ingredients) == 1
        assert restored.ingredients[0].name == "sugar"

    def test_schema_version_present(self) -> None:
        r = Recipe(id="v", name="Versioned")
        dumped = r.model_dump()
        assert "schema_version" in dumped
        assert dumped["schema_version"] == 1


class TestRecipeCreate:
    def test_id_defaults_to_empty(self) -> None:
        rc = RecipeCreate(name="New")
        assert rc.id == ""

    def test_explicit_id(self) -> None:
        rc = RecipeCreate(id="custom", name="Custom")
        assert rc.id == "custom"
