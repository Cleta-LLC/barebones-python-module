"""Storage adapters for the example service."""

from myapp.services.example.storage.json_adapter import ExampleJsonStore
from myapp.services.example.storage.sqlite_adapter import ExampleSqliteStore

__all__ = ["ExampleJsonStore", "ExampleSqliteStore"]
