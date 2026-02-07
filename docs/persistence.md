# Persistence Guide

## Two Backends, No Sync

The template ships with two independent persistence backends:

| Backend | Storage | Location | Use case |
|---------|---------|----------|----------|
| **JSON** | File on disk | `data/json/` | Human-readable snapshots, portability, debugging |
| **SQLite** | Database file | `data/db/myapp.db` | Structured queries, transactions, production use |

**Critical rule:** JSON and SQLite are **separate sources of truth**. Writing to one does **not** write to the other. They are independent I/O surfaces.

## Why No Sync?

Automatic synchronization between stores introduces:

- Race conditions and ordering bugs
- Ambiguity about which store is "correct"
- Hidden writes that surprise developers

Instead, explicit `export` and `import` commands move data between backends when the developer chooses.

## JSON Store

- Records stored as `{ "id": { ...record... } }` in a single JSON file
- **Atomic writes**: data writes to a temp file first, then `os.replace()` swaps it in
- Safe against partial writes and crashes
- Human-editable — useful for debugging and seeding data

```bash
# Write to JSON store
project svc example add --name "Test" --backend json

# List from JSON store
project svc example list --backend json
```

File location: `data/json/example_items.json`

## SQLite Store

- Records stored as JSON blobs in a table with `id`, `data`, `created_at`, `updated_at`
- **WAL journal mode** for safe concurrent reads
- All writes are transactional
- Supports upsert (insert or update on conflict)

```bash
# Write to SQLite store (default)
project svc example add --name "Test"

# List from SQLite store
project svc example list
```

File location: `data/db/myapp.db`

## Export & Import

```bash
# Export: copy all items from SQLite → JSON file
project svc example export

# Import: copy all items from JSON file → SQLite (or json)
project svc example import --target sqlite
```

## Choosing a Source

When both JSON and SQLite contain data, the system does **not** merge or pick one automatically. You must:

1. Specify `--backend sqlite` or `--backend json` on each command, **or**
2. Use the default (`sqlite`) and only use JSON for export/import workflows

## Adding Persistence to a New Service

1. Create `storage/json_adapter.py`:

```python
from myapp.shared.persistence.json_store import JsonStore
from myapp.shared.config import JSON_DIR
from .schemas import MyRecord

class MyJsonStore(JsonStore[MyRecord]):
    def __init__(self):
        super().__init__(JSON_DIR / "my_records.json", MyRecord)
```

2. Create `storage/sqlite_adapter.py`:

```python
from myapp.shared.persistence.sqlite_store import SqliteStore
from myapp.shared.config import DEFAULT_DB_PATH
from .schemas import MyRecord

class MySqliteStore(SqliteStore[MyRecord]):
    def __init__(self):
        super().__init__(DEFAULT_DB_PATH, "my_records", MyRecord)
```

3. Wire them into your service's `api.py` constructor.
