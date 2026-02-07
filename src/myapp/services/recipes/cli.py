"""CLI commands for the recipes service.

Discovered automatically by the top-level CLI via the ``commands`` group.
"""

import json
import textwrap

import click

from myapp.services.recipes.api import RecipesService
from myapp.services.recipes.schemas import RecipeCreate
from myapp.services.recipes.storage import RecipesJsonStore, RecipesSqliteStore


def _get_service(backend: str) -> RecipesService:
    if backend == "json":
        return RecipesService(store=RecipesJsonStore())
    return RecipesService(store=RecipesSqliteStore())


def _format_recipe(r: dict) -> str:  # type: ignore[type-arg]
    """Pretty-print a single recipe for the terminal."""
    lines = []
    lines.append(f"  {r['name']}  ({r['id']})")
    if r.get("description"):
        lines.append(f"  {r['description']}")
    lines.append(f"  Category: {r['category']}   Servings: {r['servings']}")
    prep = r.get("prep_time_minutes", 0)
    cook = r.get("cook_time_minutes", 0)
    lines.append(f"  Prep: {prep} min   Cook: {cook} min   Total: {prep + cook} min")
    if r.get("temperature_f"):
        c = round((r["temperature_f"] - 32) * 5 / 9)
        lines.append(f"  Oven: {r['temperature_f']}°F / {c}°C")
    if r.get("tags"):
        lines.append(f"  Tags: {', '.join(r['tags'])}")

    if r.get("ingredients"):
        lines.append("")
        lines.append("  Ingredients:")
        for ing in r["ingredients"]:
            unit = ing.get("unit", "whole")
            notes = f" ({ing['notes']})" if ing.get("notes") else ""
            lines.append(f"    - {ing['quantity']} {unit} {ing['name']}{notes}")

    if r.get("steps"):
        lines.append("")
        lines.append("  Steps:")
        for i, step in enumerate(r["steps"], 1):
            wrapped = textwrap.fill(
                step, width=72, initial_indent=f"    {i}. ", subsequent_indent="       "
            )
            lines.append(wrapped)

    return "\n".join(lines)


@click.group("recipes")
def commands() -> None:
    """Baking recipes — browse, add, and manage recipes."""


@commands.command("list")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
@click.option("--json-output", "as_json", is_flag=True, help="Output raw JSON")
def list_recipes(backend: str, as_json: bool) -> None:
    """List all recipes."""
    svc = _get_service(backend)
    resp = svc.list_recipes()
    if as_json:
        click.echo(json.dumps(resp.data, indent=2, default=str))
        return
    if not resp.data:
        click.echo("No recipes yet. Run 'project svc recipes seed' to load sample recipes.")
        return
    click.echo(f"\n{resp.message}:\n")
    for r in resp.data:
        click.echo(f"  [{r['id']}] {r['name']}  ({r['category']}, {r['servings']} servings)")
    click.echo()


@commands.command("show")
@click.argument("recipe_id")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
@click.option("--json-output", "as_json", is_flag=True, help="Output raw JSON")
def show_recipe(recipe_id: str, backend: str, as_json: bool) -> None:
    """Show full details of a recipe."""
    svc = _get_service(backend)
    resp = svc.get(recipe_id)
    if not resp.success:
        raise click.ClickException(resp.message)
    if as_json:
        click.echo(json.dumps(resp.data, indent=2, default=str))
        return
    click.echo()
    click.echo(_format_recipe(resp.data))
    click.echo()


@commands.command("search")
@click.argument("query")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def search_recipes(query: str, backend: str) -> None:
    """Search recipes by name, category, or tag."""
    svc = _get_service(backend)
    resp = svc.search(query)
    if not resp.data:
        click.echo(f"No recipes matching '{query}'.")
        return
    click.echo(f"\n{resp.message}:\n")
    for r in resp.data:
        click.echo(f"  [{r['id']}] {r['name']}  ({r['category']})")
    click.echo()


@commands.command("add")
@click.option("--name", required=True, help="Recipe name")
@click.option("--description", default="", help="Short description")
@click.option("--category", default="other", help="e.g. bread, cake, cookie, pastry")
@click.option("--prep", "prep_time", type=int, default=0, help="Prep time in minutes")
@click.option("--cook", "cook_time", type=int, default=0, help="Cook time in minutes")
@click.option("--servings", type=int, default=1)
@click.option("--temp", "temperature_f", type=int, default=None, help="Oven temp (°F)")
@click.option("--tag", multiple=True, help="Tag (repeatable)")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def add_recipe(
    name: str,
    description: str,
    category: str,
    prep_time: int,
    cook_time: int,
    servings: int,
    temperature_f: int | None,
    tag: tuple[str, ...],
    backend: str,
) -> None:
    """Create a new recipe (ingredients/steps can be added later via JSON import)."""
    svc = _get_service(backend)
    data = RecipeCreate(
        name=name,
        description=description,
        category=category,
        prep_time_minutes=prep_time,
        cook_time_minutes=cook_time,
        servings=servings,
        temperature_f=temperature_f,
        tags=list(tag),
    )
    resp = svc.create(data)
    if not resp.success:
        raise click.ClickException(resp.message)
    click.echo(f"Created: {resp.data['id']}  ({resp.data['name']})")


@commands.command("delete")
@click.argument("recipe_id")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def delete_recipe(recipe_id: str, backend: str) -> None:
    """Delete a recipe by ID."""
    svc = _get_service(backend)
    resp = svc.delete(recipe_id)
    if not resp.success:
        raise click.ClickException(resp.message)
    click.echo("Deleted.")


@commands.command("seed")
@click.option("--backend", type=click.Choice(["sqlite", "json"]), default="sqlite")
def seed_recipes(backend: str) -> None:
    """Load built-in sample recipes (banana bread, cookies, sourdough, etc.)."""
    svc = _get_service(backend)
    resp = svc.seed()
    click.echo(resp.message)


@commands.command("export")
def export_recipes() -> None:
    """Export recipes from SQLite to a JSON snapshot."""
    svc = RecipesService(store=RecipesSqliteStore())
    resp = svc.export_json()
    click.echo(resp.message)


@commands.command("import")
@click.option(
    "--target",
    type=click.Choice(["sqlite", "json"]),
    default="sqlite",
    help="Store to import INTO (source is always the JSON file)",
)
def import_recipes(target: str) -> None:
    """Import recipes from JSON snapshot into a store."""
    svc = _get_service(target)
    resp = svc.import_json()
    click.echo(resp.message)


@commands.command("schema")
def show_schema() -> None:
    """Print the Recipe JSON schema."""
    from myapp.services.recipes.schemas import Recipe

    click.echo(json.dumps(Recipe.model_json_schema(), indent=2))
