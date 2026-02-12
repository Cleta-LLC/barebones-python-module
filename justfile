# ──────────────────────────────────────────────────────────────────────
#  myapp — project control plane
#  Run `just --list` for a quick overview of available commands.
# ──────────────────────────────────────────────────────────────────────

set dotenv-load := false

# Default recipe shown when you run `just` with no arguments
default:
    @just --list

# ── Onboarding ────────────────────────────────────────────────────────

# Bootstrap the project: install deps, create data dirs, run doctor
init:
    uv sync --all-extras
    mkdir -p data/json data/db
    @just doctor

# Sync dependencies from lockfile
sync:
    uv sync --all-extras

# Verify environment health
doctor:
    uv run project doctor

# ── Development ───────────────────────────────────────────────────────

# Format code
fmt:
    uv run ruff format src/

# Lint code
lint:
    uv run ruff check src/

# Lint and auto-fix
lint-fix:
    uv run ruff check --fix src/

# Type-check code
typecheck:
    uv run mypy src/myapp/

# Run tests
test *ARGS:
    uv run pytest {{ARGS}}

# Run tests with coverage
cov:
    uv run pytest --cov=myapp --cov-report=term-missing

# Run all quality checks (fmt check + lint + typecheck + tests)
check:
    uv run ruff format --check src/
    uv run ruff check src/
    uv run mypy src/myapp/
    uv run pytest

# ── Run ───────────────────────────────────────────────────────────────

# Run the default service
run:
    uv run project run

# Run a CLI command (pass any args)
cli *ARGS:
    uv run project {{ARGS}}

# Run Streamlit UI
ui:
    uv run streamlit run ui/streamlit_app.py

# ── Scaffolding ─────────────────────────────────────────────────────

# Scaffold a new service with all required files
scaffold NAME:
    uv run python scripts/scaffold_service.py {{NAME}}

# Rename the project (replaces all occurrences of OLD with NEW)
rename OLD NEW:
    @echo "Renaming '{{OLD}}' → '{{NEW}}' across the codebase..."
    find src/ docs/ ui/ scripts/ -type f -name '*.py' -o -name '*.md' -o -name '*.toml' -o -name '*.yml' | xargs sed -i 's/{{OLD}}/{{NEW}}/g'
    sed -i 's/{{OLD}}/{{NEW}}/g' pyproject.toml justfile README.md CONTRIBUTING.md
    mv src/{{OLD}} src/{{NEW}} 2>/dev/null || true
    @echo "Done. Run 'just init' to re-sync."

# ── Build & Release ──────────────────────────────────────────────────

# Build wheel + sdist
build:
    uv build

# Publish to PyPI (configure credentials first)
publish:
    uv publish

# Build Docker image
docker-build:
    docker build -t myapp:latest .

# Run Docker container
docker-run:
    docker run --rm -it myapp:latest

# ── Clean ───────────────────────────────────────────────────────────

# Remove build artifacts and caches
clean:
    rm -rf dist/ build/ *.egg-info/
    rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/
    find src/ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @echo "Cleaned."

# ── Docs ──────────────────────────────────────────────────────────────

# Open the quickstart guide
docs:
    @echo "Documentation is in docs/ — start with docs/quickstart.md"
    @echo ""
    @echo "  docs/quickstart.md     Get running in 3 commands"
    @echo "  docs/architecture.md   Services, boundaries, data flow"
    @echo "  docs/cli-reference.md  All commands and options"
    @echo "  docs/persistence.md    JSON vs SQLite, no-sync explained"
    @echo "  docs/extending.md      Add services, commands, schemas, UI pages"

# ── Service patterns ─────────────────────────────────────────────────
# To add commands for a new service, copy one of the patterns below
# and replace "example" with your service name.

# Run example service
svc-example-run:
    uv run project svc example list

# Test example service
svc-example-test:
    uv run pytest src/myapp/services/example/tests/

# Show example service schema
svc-example-schema:
    uv run project svc example schema
