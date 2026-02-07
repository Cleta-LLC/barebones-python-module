# Extending the Template

## Add a Dependency

```bash
# Runtime dependency
uv add requests

# Dev-only dependency
uv add --group dev httpx

# Optional group (e.g., UI)
uv add --group ui plotly
```

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

For pip users: `pip install -e ".[dev,ui]"` works but `uv sync` is canonical.

## Add a New Service

1. **Create the directory:**

```bash
mkdir -p src/myapp/services/billing/{storage,tests}
```

2. **Create the required files** (copy from `example/`):

```
services/billing/
├── __init__.py      # """Billing service."""
├── schemas.py       # define your models (extend BaseRecord)
├── api.py           # BillingService class (public interface)
├── cli.py           # Click group named `commands`
├── storage/
│   ├── __init__.py
│   ├── json_adapter.py
│   └── sqlite_adapter.py
└── tests/
    ├── __init__.py
    ├── test_schemas.py
    ├── test_storage.py
    └── test_api.py
```

3. **Define your schema** in `schemas.py`:

```python
from myapp.shared.schemas import BaseRecord
from pydantic import Field

class Invoice(BaseRecord):
    customer_id: str
    amount_cents: int = Field(ge=0)
    status: str = "draft"
```

4. **Create your CLI** in `cli.py`:

```python
import click

@click.group("billing")
def commands():
    """Billing service commands."""

@commands.command("list")
def list_invoices():
    """List all invoices."""
    from .api import BillingService
    svc = BillingService()
    ...
```

5. **That's it.** The CLI auto-discovers the service:

```bash
project svc billing list    # works immediately
```

6. **Optional — add justfile recipes:**

```just
svc-billing-run:
    uv run project svc billing list

svc-billing-test:
    uv run pytest src/myapp/services/billing/tests/
```

## Add a New CLI Command

To add a command to an existing service, add it to that service's `cli.py`:

```python
@commands.command("status")
def show_status():
    """Show billing status."""
    click.echo("All clear")
```

To add a top-level command, edit `src/myapp/cli/main.py`:

```python
@cli.command()
def my_command():
    """A new top-level command."""
    ...
```

## Add a New Schema / Model

1. Define the model in the service's `schemas.py` (extend `BaseRecord`)
2. Include `schema_version` (inherited from `BaseRecord`)
3. Add tests for serialization/deserialization in `tests/test_schemas.py`
4. Create storage adapters if the model needs persistence

```python
from myapp.shared.schemas import BaseRecord

class MyModel(BaseRecord):
    field_a: str
    field_b: int = 0
```

## Add a New Streamlit Page

1. Create a new file in `ui/` (e.g., `ui/pages/billing.py`)
2. Import and use the service API:

```python
import streamlit as st
from myapp.services.billing.api import BillingService

st.title("Billing")
svc = BillingService()
resp = svc.list_invoices()
# ... render data
```

3. Streamlit auto-discovers pages in `ui/pages/`.

## pip Compatibility

While `uv` is the canonical tool, pip still works:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,ui]"
pytest
```

The `pyproject.toml` is fully PEP 621 compliant.
