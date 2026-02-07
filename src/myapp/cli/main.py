"""Top-level CLI entrypoint.

Services register their commands automatically via ``cli.py`` modules.
Usage: ``project <command>`` or ``uv run project <command>``.
"""

import importlib
import pkgutil
import shutil
import sys

import click

import myapp
import myapp.services as _svc_pkg
from myapp.shared.config import DATA_DIR, DB_DIR, JSON_DIR, ensure_data_dirs


@click.group()
@click.version_option(version=myapp.__version__, prog_name="project")
def cli() -> None:
    """project — microservice template CLI."""
    ensure_data_dirs()


# ── core commands ─────────────────────────────────────────────────────


@cli.command()
def run() -> None:
    """Run the default service (example)."""
    from myapp.services.example.api import ExampleService

    svc = ExampleService()
    resp = svc.list_items()
    click.echo(f"Example service ready — {resp.message}")


@cli.command()
def doctor() -> None:
    """Check that the development environment is healthy."""
    ok = True

    def _check(label: str, result: bool, hint: str = "") -> None:
        nonlocal ok
        status = "ok" if result else "FAIL"
        click.echo(f"  [{status}] {label}")
        if not result:
            ok = False
            if hint:
                click.echo(f"         -> {hint}")

    click.echo("Environment check:\n")
    _check("Python >= 3.11", sys.version_info >= (3, 11), "Upgrade Python")
    _check(
        "uv available",
        shutil.which("uv") is not None,
        "Install: curl -LsSf https://astral.sh/uv/install.sh | sh",
    )
    _check(
        "just available",
        shutil.which("just") is not None,
        "Install: cargo install just  OR  brew install just",
    )
    _check("data/json/ exists", JSON_DIR.is_dir())
    _check("data/db/ exists", DB_DIR.is_dir())

    writable = DATA_DIR.is_dir()
    if writable:
        (DATA_DIR / ".probe").write_text("ok")
    _check("data/ writable", writable)

    # clean probe file
    probe = DATA_DIR / ".probe"
    if probe.exists():
        probe.unlink()

    click.echo()
    if ok:
        click.echo("All checks passed.")
    else:
        click.echo("Some checks failed — see hints above.")
        raise SystemExit(1)


# ── service subgroup (auto-discovered) ────────────────────────────────


@cli.group("svc")
def svc_group() -> None:
    """Service commands — one subgroup per service."""


def _discover_service_commands() -> None:
    """Walk ``myapp.services.*`` looking for ``cli.commands`` groups."""
    for _importer, name, _ispkg in pkgutil.iter_modules(_svc_pkg.__path__):
        try:
            mod = importlib.import_module(f"myapp.services.{name}.cli")
            group = getattr(mod, "commands", None)
            if group is not None:
                svc_group.add_command(group, name)
        except ImportError:
            pass  # service has no CLI — that is fine


_discover_service_commands()
