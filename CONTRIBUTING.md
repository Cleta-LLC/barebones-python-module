# Contributing

## Setup

```bash
just init       # install all deps (including dev extras)
just doctor     # verify your environment
```

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Run quality gates: `just check`
4. Commit with a descriptive message
5. Open a pull request

## Quality Gates

All of these must pass before merging:

```bash
just fmt          # format code with ruff
just lint         # lint with ruff
just typecheck    # type check with mypy (strict mode)
just test         # run all tests with pytest
```

Run them all at once with `just check`.

## Code Style

- **Formatter**: ruff (100 char line length)
- **Linter**: ruff (E, F, I, N, W, UP rules)
- **Type checker**: mypy (strict — `disallow_untyped_defs`)
- **Imports**: sorted by isort (via ruff), first-party = `myapp`

## Adding a New Service

Use the scaffold command:

```bash
just scaffold myservice
```

This creates the full service directory structure with all required files. Then customize the generated schemas, API, CLI, and storage adapters.

See [docs/extending.md](docs/extending.md) for the full guide.

## Testing

- Every service has its own `tests/` directory
- Tests use `tmp_path` fixtures for isolation — no shared state
- Run a single service's tests: `just test src/myapp/services/example/tests/`
- Run with coverage: `just cov`

## Commit Messages

Use conventional-style prefixes:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation only
- `style:` formatting (no logic change)
- `refactor:` code restructuring
- `test:` adding or updating tests
- `chore:` maintenance tasks

## CI

GitHub Actions runs the same quality gates (`just check`) on every push and PR, across Python 3.11, 3.12, and 3.13. Formatting fixes are auto-committed on PRs.
