# myapp

[![CI](https://github.com/OWNER/myapp/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/myapp/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A fork-ready, microservice-friendly Python template.

Clone, init, test, run — then extend with your own services.

## Use This Template

**Option A — GitHub template button:** Click **Use this template** on GitHub, then:

```bash
git clone <your-new-repo-url> && cd <your-new-repo>
just rename myapp yourproject   # renames everything in one shot
just init
```

**Option B — Fork and rename:**

```bash
git clone <your-fork-url> && cd myapp
just rename myapp yourproject
just init && just test
```

The `just rename` command replaces all occurrences of `myapp` with your project name across the entire codebase — pyproject.toml, imports, config, docs, and more.

## Quickstart

```bash
just init       # install deps, create data dirs, check environment
just test       # run all tests
just run        # run the default service
```

Requires [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just). See `just doctor` for environment checks.

## What You Get

- **uv-native** workflows — `pyproject.toml` as single source of truth, `uv.lock` committed
- **Microservice architecture** — each service in `src/myapp/services/` with clear boundaries
- **Typed schemas** — Pydantic models at every boundary, versioned with `schema_version`
- **Dual persistence** — JSON (atomic file writes) + SQLite (WAL mode), independent by design
- **CLI** — Click-based, auto-discovers service commands (`project svc <name> <cmd>`)
- **Optional Streamlit UI** — wraps the same service APIs as the CLI
- **Quality gates** — ruff, mypy, pytest, all runnable via `just check`
- **CI/CD** — GitHub Actions matrix testing across Python 3.11–3.13
- **Docker** — multi-stage Dockerfile with uv for minimal images
- **PEP 561** — `py.typed` marker for downstream type checking

## Project Structure

```
src/myapp/
├── cli/              # top-level CLI entrypoint
├── shared/           # config, logging, base schemas, persistence
│   └── persistence/  # BaseStore, JsonStore, SqliteStore
└── services/
    └── example/      # example service (copy to create new ones)
        ├── api.py        # public interface
        ├── schemas.py    # I/O models
        ├── cli.py        # service CLI commands
        ├── storage/      # JSON + SQLite adapters
        └── tests/        # service tests
ui/                   # optional Streamlit app
data/                 # runtime data (gitignored contents)
docs/                 # guides and reference
```

## Commands

```bash
just --list           # see all available commands
just init             # bootstrap project
just doctor           # verify environment
just fmt              # format code
just lint             # lint code
just typecheck        # run mypy
just test             # run pytest
just check            # all quality gates
just cov              # test with coverage report
just run              # run default service
just cli <args>       # run any CLI command
just ui               # launch Streamlit
just scaffold <name>  # scaffold a new service
just rename OLD NEW   # rename the project
just clean            # remove build artifacts and caches
just build            # build wheel + sdist
just docker-build     # build Docker image
just docker-run       # run Docker container
```

## Adding a New Service

```bash
just scaffold billing
# That's it — creates the full service directory with all required files.
# The CLI auto-discovers it — no registration needed.
project svc billing --help
```

Or manually:

```bash
mkdir -p src/myapp/services/myservice/{storage,tests}
# Copy and adapt from services/example/
project svc myservice --help
```

See [Extending](docs/extending.md) for the full walkthrough.

## Documentation

| Guide | Description |
|-------|-------------|
| [Quickstart](docs/quickstart.md) | Get running in 3 commands |
| [Architecture](docs/architecture.md) | Services, boundaries, data flow |
| [CLI Reference](docs/cli-reference.md) | All commands and options |
| [Persistence](docs/persistence.md) | JSON vs SQLite, no-sync explained |
| [Extending](docs/extending.md) | Add services, commands, schemas, UI pages |
| [Contributing](CONTRIBUTING.md) | Development workflow and conventions |

## License

MIT — see [LICENSE](LICENSE) for details.
