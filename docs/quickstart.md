# Quickstart

Three commands to a running project:

```bash
git clone <your-fork-url> && cd myapp
just init
just test
```

You now have:

- a working CLI (`uv run project --help`)
- passing tests
- an example service with JSON + SQLite persistence

## Run things

```bash
just run          # run the default service
just cli --help   # explore CLI commands
just ui           # launch Streamlit UI (requires `ui` extra)
```

## Day-to-day development

```bash
just fmt          # format code
just lint         # lint
just typecheck    # mypy
just test         # pytest
just check        # all of the above in one shot
```

## What's inside

```
src/myapp/
  cli/            # top-level CLI (Click)
  shared/         # config, logging, schemas, persistence
  services/
    example/      # example service — copy this to start a new one
      api.py      # public interface
      schemas.py  # I/O models
      storage/    # JSON + SQLite adapters
      cli.py      # service CLI commands
      tests/      # service tests
ui/               # optional Streamlit app
data/             # runtime data (json/, db/)
```

Next: [Architecture](architecture.md) | [CLI Reference](cli-reference.md) | [Persistence Guide](persistence.md)
