# CLI Reference

The CLI entrypoint is `project`. Run via `uv run project` or (after `just init`) directly as `project`.

## Top-level Commands

```bash
project --version          # show version
project --help             # show help
project run                # run the default service
project doctor             # check environment health
project svc <service> ...  # service sub-commands
```

## Service Commands

Services register CLI commands automatically. The pattern is:

```
project svc <service-name> <command> [options]
```

### Example Service

```bash
# List all items
project svc example list [--backend sqlite|json]

# Get a single item
project svc example get ITEM_ID [--backend sqlite|json]

# Add a new item
project svc example add --name "My Item" [--description "..."] [--tag foo --tag bar] [--backend sqlite|json]

# Delete an item
project svc example delete ITEM_ID [--backend sqlite|json]

# Export items from SQLite to JSON
project svc example export

# Import items from JSON into a store
project svc example import [--target sqlite|json]

# Show the Item JSON schema
project svc example schema
```

### Backend Selection

Most commands accept `--backend sqlite|json` (default: `sqlite`).

- `sqlite` — reads/writes `data/db/myapp.db`
- `json` — reads/writes `data/json/example_items.json`

These are **independent** stores. Writing to one does not affect the other.

## Justfile Shortcuts

The `justfile` provides convenient wrappers:

```bash
just cli --help                   # same as: uv run project --help
just cli svc example list         # same as: uv run project svc example list
just run                          # same as: uv run project run
just doctor                       # same as: uv run project doctor
```
