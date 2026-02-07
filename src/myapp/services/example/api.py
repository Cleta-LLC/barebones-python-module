"""Public API for the example service.

Other services and the CLI should *only* import from this module.
Never import internals (storage, etc.) from outside the service.
"""

import uuid

from myapp.services.example.schemas import Item, ItemCreate
from myapp.services.example.storage import ExampleJsonStore, ExampleSqliteStore
from myapp.shared.persistence.base import BaseStore
from myapp.shared.schemas import ServiceResponse, utcnow


class ExampleService:
    """Facade that owns all example-service business logic."""

    def __init__(self, store: BaseStore[Item] | None = None) -> None:
        self._store = store or ExampleSqliteStore()

    # -- CRUD --------------------------------------------------------------

    def create(self, data: ItemCreate) -> ServiceResponse:
        item = Item(
            id=data.id or uuid.uuid4().hex[:12],
            name=data.name,
            description=data.description,
            tags=data.tags,
            schema_version=data.schema_version,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        saved = self._store.save(item)
        return ServiceResponse(success=True, message="Item created", data=saved.model_dump())

    def get(self, item_id: str) -> ServiceResponse:
        item = self._store.get(item_id)
        if item is None:
            return ServiceResponse(success=False, message="Not found", errors=[f"id={item_id}"])
        return ServiceResponse(success=True, data=item.model_dump())

    def list_items(self) -> ServiceResponse:
        items = self._store.list_all()
        return ServiceResponse(
            success=True,
            data=[i.model_dump() for i in items],
            message=f"{len(items)} item(s)",
        )

    def delete(self, item_id: str) -> ServiceResponse:
        deleted = self._store.delete(item_id)
        if not deleted:
            return ServiceResponse(success=False, message="Not found", errors=[f"id={item_id}"])
        return ServiceResponse(success=True, message="Item deleted")

    # -- Export / Import ---------------------------------------------------

    def export_json(self) -> ServiceResponse:
        """Export current store contents to the JSON backend."""
        json_store = ExampleJsonStore()
        items = self._store.list_all()
        for item in items:
            json_store.save(item)
        path = str(json_store.path)
        return ServiceResponse(
            success=True,
            message=f"Exported {len(items)} item(s) to {path}",
            data={"path": path, "count": len(items)},
        )

    def import_json(self) -> ServiceResponse:
        """Import items from the JSON backend into the current store."""
        json_store = ExampleJsonStore()
        items = json_store.list_all()
        for item in items:
            self._store.save(item)
        return ServiceResponse(
            success=True,
            message=f"Imported {len(items)} item(s) from JSON",
            data={"count": len(items)},
        )
