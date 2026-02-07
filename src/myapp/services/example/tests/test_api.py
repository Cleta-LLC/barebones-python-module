"""Tests for the example service public API."""

from pathlib import Path

import pytest

from myapp.services.example.api import ExampleService
from myapp.services.example.schemas import Item, ItemCreate
from myapp.shared.persistence.json_store import JsonStore


@pytest.fixture()
def svc(tmp_path: Path) -> ExampleService:
    store = JsonStore(tmp_path / "items.json", Item)
    return ExampleService(store=store)


class TestExampleService:
    def test_create_item(self, svc: ExampleService) -> None:
        resp = svc.create(ItemCreate(name="Hello"))
        assert resp.success
        assert resp.data["name"] == "Hello"
        assert resp.data["id"]  # auto-generated

    def test_create_with_explicit_id(self, svc: ExampleService) -> None:
        resp = svc.create(ItemCreate(id="custom", name="Custom"))
        assert resp.success
        assert resp.data["id"] == "custom"

    def test_get_item(self, svc: ExampleService) -> None:
        create_resp = svc.create(ItemCreate(name="Fetch me"))
        item_id = create_resp.data["id"]
        resp = svc.get(item_id)
        assert resp.success
        assert resp.data["name"] == "Fetch me"

    def test_get_missing(self, svc: ExampleService) -> None:
        resp = svc.get("nope")
        assert not resp.success

    def test_list_items(self, svc: ExampleService) -> None:
        svc.create(ItemCreate(name="A"))
        svc.create(ItemCreate(name="B"))
        resp = svc.list_items()
        assert resp.success
        assert len(resp.data) == 2

    def test_delete_item(self, svc: ExampleService) -> None:
        create_resp = svc.create(ItemCreate(name="Gone"))
        item_id = create_resp.data["id"]
        resp = svc.delete(item_id)
        assert resp.success
        assert svc.get(item_id).success is False

    def test_delete_missing(self, svc: ExampleService) -> None:
        resp = svc.delete("nope")
        assert not resp.success


class TestExportImport:
    def test_export_and_import(self, tmp_path: Path) -> None:
        """Round-trip: create in sqlite-backed store -> export -> import into another store."""
        from myapp.shared.persistence.sqlite_store import SqliteStore

        # source store (SQLite)
        src_store = SqliteStore(tmp_path / "src.db", "items", Item)
        src_svc = ExampleService(store=src_store)
        src_svc.create(ItemCreate(id="e1", name="Export me"))

        # Manually do the export/import using JSON store in tmp
        json_store = JsonStore(tmp_path / "export.json", Item)
        for item in src_store.list_all():
            json_store.save(item)

        # destination store
        dst_store = JsonStore(tmp_path / "dst.json", Item)
        for item in json_store.list_all():
            dst_store.save(item)

        dst_svc = ExampleService(store=dst_store)
        resp = dst_svc.get("e1")
        assert resp.success
        assert resp.data["name"] == "Export me"
