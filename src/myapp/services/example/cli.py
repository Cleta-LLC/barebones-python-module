"""CLI commands for the example service.

Discovered automatically by the top-level CLI via the ``commands`` group.
"""

import json

import click

from myapp.services.example.api import ExampleService
from myapp.services.example.schemas import ItemCreate
from myapp.services.example.storage import ExampleJsonStore, ExampleSqliteStore


def _get_service(backend: str) -> ExampleService:
    if backend == "json":
        return ExampleService(store=ExampleJsonStore())
    return ExampleService(store=ExampleSqliteStore())


@click.group("example")
def commands() -> None:
    """Example service — manage items."""


@commands.command("list")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def list_items(backend: str) -> None:
    """List all items."""
    svc = _get_service(backend)
    resp = svc.list_items()
    click.echo(json.dumps(resp.data, indent=2, default=str))


@commands.command("get")
@click.argument("item_id")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def get_item(item_id: str, backend: str) -> None:
    """Get a single item by ID."""
    svc = _get_service(backend)
    resp = svc.get(item_id)
    if not resp.success:
        raise click.ClickException(resp.message)
    click.echo(json.dumps(resp.data, indent=2, default=str))


@commands.command("add")
@click.option("--name", required=True, help="Item name")
@click.option("--description", default="", help="Item description")
@click.option("--tag", multiple=True, help="Tag (repeatable)")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def add_item(name: str, description: str, tag: tuple[str, ...], backend: str) -> None:
    """Create a new item."""
    svc = _get_service(backend)
    data = ItemCreate(name=name, description=description, tags=list(tag))
    resp = svc.create(data)
    if not resp.success:
        raise click.ClickException(resp.message)
    click.echo(f"Created: {resp.data['id']}")


@commands.command("delete")
@click.argument("item_id")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def delete_item(item_id: str, backend: str) -> None:
    """Delete an item by ID."""
    svc = _get_service(backend)
    resp = svc.delete(item_id)
    if not resp.success:
        raise click.ClickException(resp.message)
    click.echo("Deleted.")


@commands.command("export")
def export_items() -> None:
    """Export items from SQLite to a JSON snapshot."""
    svc = ExampleService(store=ExampleSqliteStore())
    resp = svc.export_json()
    click.echo(resp.message)


@commands.command("import")
@click.option(
    "--target",
    type=click.Choice(["sqlite", "json"]),
    default="sqlite",
    help="Store to import INTO (source is always the JSON file)",
)
def import_items(target: str) -> None:
    """Import items from JSON snapshot into a store."""
    svc = _get_service(target)
    resp = svc.import_json()
    click.echo(resp.message)


@commands.command("schema")
def show_schema() -> None:
    """Print the Item JSON schema."""
    from myapp.services.example.schemas import Item

    click.echo(json.dumps(Item.model_json_schema(), indent=2))
