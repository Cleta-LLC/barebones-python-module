"""Tests for example service schemas."""

import pytest
from pydantic import ValidationError

from myapp.services.example.schemas import Item, ItemCreate


class TestItem:
    def test_valid_item(self) -> None:
        item = Item(id="abc123", name="Test Item")
        assert item.id == "abc123"
        assert item.name == "Test Item"
        assert item.schema_version == 1
        assert item.tags == []

    def test_item_with_tags(self) -> None:
        item = Item(id="x", name="Tagged", tags=["a", "b"])
        assert item.tags == ["a", "b"]

    def test_item_requires_name(self) -> None:
        with pytest.raises(ValidationError):
            Item(id="x", name="")  # min_length=1

    def test_item_roundtrip_json(self) -> None:
        item = Item(id="rt", name="Roundtrip", description="desc", tags=["t"])
        raw = item.model_dump_json()
        restored = Item.model_validate_json(raw)
        assert restored.id == item.id
        assert restored.name == item.name
        assert restored.tags == item.tags

    def test_schema_version_present(self) -> None:
        item = Item(id="v", name="Versioned")
        dumped = item.model_dump()
        assert "schema_version" in dumped
        assert dumped["schema_version"] == 1


class TestItemCreate:
    def test_id_defaults_to_empty(self) -> None:
        ic = ItemCreate(name="New")
        assert ic.id == ""

    def test_explicit_id(self) -> None:
        ic = ItemCreate(id="custom", name="Custom")
        assert ic.id == "custom"
