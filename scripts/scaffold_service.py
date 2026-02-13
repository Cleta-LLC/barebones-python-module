#!/usr/bin/env python3
"""Scaffold a new service directory with all required files.

Usage: python scripts/scaffold_service.py <service_name>
   or: just scaffold <service_name>
"""

import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "myapp" / "services"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"  created {path.relative_to(ROOT)}")


def scaffold(name: str) -> None:
    base = SRC / name
    if base.exists():
        print(f"Error: service '{name}' already exists at {base}")
        sys.exit(1)

    title = name.replace("_", " ").title()
    class_name = name.replace("_", " ").title().replace(" ", "")
    record_name = f"{class_name}Record"
    record_create = f"{class_name}RecordCreate"
    service_class = f"{class_name}Service"

    # __init__.py
    _write(base / "__init__.py", f'"""{title} service."""\n')

    # schemas.py
    _write(
        base / "schemas.py",
        f'''\
        """{title} service schemas."""

        from pydantic import Field

        from myapp.shared.schemas import BaseRecord


        class {record_name}(BaseRecord):
            """{title} domain record."""

            name: str = Field(..., min_length=1, max_length=200)
            description: str = Field(default="")


        class {record_create}({record_name}):
            """Input model for creating a {name} record."""

            id: str = Field(default="")
            schema_version: int = 1
        ''',
    )

    # api.py
    _write(
        base / "api.py",
        f'''\
        """Public API for the {name} service."""

        import uuid

        from myapp.services.{name}.schemas import {record_name}, {record_create}
        from myapp.services.{name}.storage import {class_name}JsonStore, {class_name}SqliteStore
        from myapp.shared.persistence.base import BaseStore
        from myapp.shared.schemas import ServiceResponse, utcnow


        class {service_class}:
            """Facade for {name} service business logic."""

            def __init__(self, store: BaseStore[{record_name}] | None = None) -> None:
                self._store = store or {class_name}SqliteStore()

            def create(self, data: {record_create}) -> ServiceResponse:
                record = {record_name}(
                    id=data.id or uuid.uuid4().hex[:12],
                    name=data.name,
                    description=data.description,
                    schema_version=data.schema_version,
                    created_at=utcnow(),
                    updated_at=utcnow(),
                )
                saved = self._store.save(record)
                return ServiceResponse(success=True, message="Record created", data=saved.model_dump())

            def get(self, record_id: str) -> ServiceResponse:
                record = self._store.get(record_id)
                if record is None:
                    return ServiceResponse(success=False, message="Not found", errors=[f"id={{record_id}}"])
                return ServiceResponse(success=True, data=record.model_dump())

            def list_records(self) -> ServiceResponse:
                records = self._store.list_all()
                return ServiceResponse(
                    success=True,
                    data=[r.model_dump() for r in records],
                    message=f"{{len(records)}} record(s)",
                )

            def delete(self, record_id: str) -> ServiceResponse:
                deleted = self._store.delete(record_id)
                if not deleted:
                    return ServiceResponse(success=False, message="Not found", errors=[f"id={{record_id}}"])
                return ServiceResponse(success=True, message="Record deleted")
        ''',
    )

    # cli.py
    _write(
        base / "cli.py",
        f'''\
        """CLI commands for the {name} service."""

        import json

        import click

        from myapp.services.{name}.api import {service_class}
        from myapp.services.{name}.schemas import {record_create}
        from myapp.services.{name}.storage import {class_name}JsonStore, {class_name}SqliteStore


        def _get_service(backend: str) -> {service_class}:
            if backend == "json":
                return {service_class}(store={class_name}JsonStore())
            return {service_class}(store={class_name}SqliteStore())


        @click.group("{name}")
        def commands() -> None:
            """{title} service commands."""


        @commands.command("list")
        @click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
        def list_records(backend: str) -> None:
            """List all records."""
            svc = _get_service(backend)
            resp = svc.list_records()
            click.echo(json.dumps(resp.data, indent=2, default=str))


        @commands.command("get")
        @click.argument("record_id")
        @click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
        def get_record(record_id: str, backend: str) -> None:
            """Get a single record by ID."""
            svc = _get_service(backend)
            resp = svc.get(record_id)
            if not resp.success:
                raise click.ClickException(resp.message)
            click.echo(json.dumps(resp.data, indent=2, default=str))


        @commands.command("add")
        @click.option("--name", required=True, help="Record name")
        @click.option("--description", default="", help="Record description")
        @click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
        def add_record(name: str, description: str, backend: str) -> None:
            """Create a new record."""
            svc = _get_service(backend)
            data = {record_create}(name=name, description=description)
            resp = svc.create(data)
            if not resp.success:
                raise click.ClickException(resp.message)
            click.echo(f"Created: {{resp.data['id']}}")


        @commands.command("delete")
        @click.argument("record_id")
        @click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
        def delete_record(record_id: str, backend: str) -> None:
            """Delete a record by ID."""
            svc = _get_service(backend)
            resp = svc.delete(record_id)
            if not resp.success:
                raise click.ClickException(resp.message)
            click.echo("Deleted.")
        ''',
    )

    # storage/__init__.py
    _write(
        base / "storage" / "__init__.py",
        f'''\
        """Storage adapters for the {name} service."""

        from myapp.services.{name}.storage.json_adapter import {class_name}JsonStore
        from myapp.services.{name}.storage.sqlite_adapter import {class_name}SqliteStore

        __all__ = ["{class_name}JsonStore", "{class_name}SqliteStore"]
        ''',
    )

    # storage/json_adapter.py
    _write(
        base / "storage" / "json_adapter.py",
        f'''\
        """JSON persistence adapter for the {name} service."""

        from pathlib import Path

        from myapp.services.{name}.schemas import {record_name}
        from myapp.shared.config import JSON_DIR
        from myapp.shared.persistence.json_store import JsonStore

        DEFAULT_PATH = JSON_DIR / "{name}_records.json"


        class {class_name}JsonStore(JsonStore[{record_name}]):
            """Concrete JSON store for {name} records."""

            def __init__(self, path: Path | None = None) -> None:
                super().__init__(path or DEFAULT_PATH, {record_name})
        ''',
    )

    # storage/sqlite_adapter.py
    _write(
        base / "storage" / "sqlite_adapter.py",
        f'''\
        """SQLite persistence adapter for the {name} service."""

        from pathlib import Path

        from myapp.services.{name}.schemas import {record_name}
        from myapp.shared.config import DEFAULT_DB_PATH
        from myapp.shared.persistence.sqlite_store import SqliteStore

        TABLE_NAME = "{name}_records"


        class {class_name}SqliteStore(SqliteStore[{record_name}]):
            """Concrete SQLite store for {name} records."""

            def __init__(self, db_path: Path | None = None) -> None:
                super().__init__(db_path or DEFAULT_DB_PATH, TABLE_NAME, {record_name})
        ''',
    )

    # tests/__init__.py
    _write(base / "tests" / "__init__.py", "")

    # tests/test_schemas.py
    _write(
        base / "tests" / "test_schemas.py",
        f'''\
        """Tests for {name} service schemas."""

        import pytest
        from pydantic import ValidationError

        from myapp.services.{name}.schemas import {record_name}, {record_create}


        class Test{record_name}:
            def test_valid_record(self) -> None:
                record = {record_name}(id="abc123", name="Test")
                assert record.id == "abc123"
                assert record.name == "Test"
                assert record.schema_version == 1

            def test_requires_name(self) -> None:
                with pytest.raises(ValidationError):
                    {record_name}(id="x", name="")

            def test_roundtrip_json(self) -> None:
                record = {record_name}(id="rt", name="Roundtrip", description="desc")
                raw = record.model_dump_json()
                restored = {record_name}.model_validate_json(raw)
                assert restored.id == record.id
                assert restored.name == record.name


        class Test{record_create}:
            def test_id_defaults_to_empty(self) -> None:
                rc = {record_create}(name="New")
                assert rc.id == ""
        ''',
    )

    # tests/test_api.py
    _write(
        base / "tests" / "test_api.py",
        f'''\
        """Tests for the {name} service API."""

        from pathlib import Path

        import pytest

        from myapp.services.{name}.api import {service_class}
        from myapp.services.{name}.schemas import {record_name}, {record_create}
        from myapp.shared.persistence.json_store import JsonStore


        @pytest.fixture()
        def svc(tmp_path: Path) -> {service_class}:
            store = JsonStore(tmp_path / "records.json", {record_name})
            return {service_class}(store=store)


        class Test{service_class}:
            def test_create(self, svc: {service_class}) -> None:
                resp = svc.create({record_create}(name="Hello"))
                assert resp.success
                assert resp.data["name"] == "Hello"

            def test_get(self, svc: {service_class}) -> None:
                create_resp = svc.create({record_create}(name="Fetch me"))
                record_id = create_resp.data["id"]
                resp = svc.get(record_id)
                assert resp.success

            def test_get_missing(self, svc: {service_class}) -> None:
                resp = svc.get("nope")
                assert not resp.success

            def test_list(self, svc: {service_class}) -> None:
                svc.create({record_create}(name="A"))
                svc.create({record_create}(name="B"))
                resp = svc.list_records()
                assert resp.success
                assert len(resp.data) == 2

            def test_delete(self, svc: {service_class}) -> None:
                create_resp = svc.create({record_create}(name="Gone"))
                record_id = create_resp.data["id"]
                resp = svc.delete(record_id)
                assert resp.success
        ''',
    )

    print(f"\nService '{name}' scaffolded at src/myapp/services/{name}/")
    print(f"Run: uv run project svc {name} --help")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/scaffold_service.py <service_name>")
        sys.exit(1)

    name = sys.argv[1].lower().replace("-", "_")
    if not name.isidentifier():
        print(f"Error: '{name}' is not a valid Python identifier")
        sys.exit(1)

    scaffold(name)
