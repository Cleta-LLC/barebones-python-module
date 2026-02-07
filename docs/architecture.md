# Architecture

## Design Principles

1. **Service-first** — every feature lives inside a service directory
2. **Shared, not coupled** — common code in `shared/`, imported as a library
3. **Schema-enforced boundaries** — services exchange Pydantic models, never raw dicts
4. **Independent persistence** — JSON and SQLite are separate backends, not synced

## Directory Layout

```
src/myapp/
├── __init__.py              # package root, version
├── cli/
│   ├── __init__.py
│   └── main.py              # top-level CLI, auto-discovers services
├── shared/
│   ├── config.py            # paths, data dirs
│   ├── logging.py           # centralized logger
│   ├── schemas.py           # BaseRecord, ServiceResponse
│   └── persistence/
│       ├── base.py          # BaseStore[T] ABC
│       ├── json_store.py    # atomic JSON file backend
│       └── sqlite_store.py  # WAL-mode SQLite backend
└── services/
    └── example/             # one service = one subdirectory
        ├── api.py           # ExampleService (public facade)
        ├── schemas.py       # Item, ItemCreate
        ├── cli.py           # Click group, auto-registered
        ├── storage/
        │   ├── json_adapter.py
        │   └── sqlite_adapter.py
        └── tests/
```

## Service Contract

Every service **must** expose:

| File | Purpose |
|------|---------|
| `api.py` | Public interface — the only file other code imports |
| `schemas.py` | Pydantic models for inputs, outputs, records |
| `storage/` | Persistence adapters (JSON and/or SQLite) |
| `cli.py` | Click command group named `commands` |
| `tests/` | pytest tests for the service |

## Boundary Rules

- Services **never** import another service's internals
- Cross-service communication uses schemas from `api.py` only
- Shared code (config, persistence, schemas) lives in `shared/`
- The CLI auto-discovers services — no manual registration needed

## Data Flow

```
User → CLI/UI → ExampleService (api.py)
                    ↓
              schemas.py (validates I/O)
                    ↓
              storage/ (JsonStore or SqliteStore)
                    ↓
              data/json/ or data/db/
```

## Persistence Architecture

See [Persistence Guide](persistence.md) for full details.

Key rule: **JSON and SQLite are independent stores.** Writing to one does not write to the other. The `export` and `import` commands move data between them explicitly.
