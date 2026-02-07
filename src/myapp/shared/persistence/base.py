"""Abstract base for all persistence stores."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseStore(ABC, Generic[T]):
    """Interface that every store backend must implement."""

    @abstractmethod
    def get(self, record_id: str) -> T | None:
        """Fetch a single record by ID, or None."""

    @abstractmethod
    def list_all(self) -> list[T]:
        """Return every record in the store."""

    @abstractmethod
    def save(self, item: T) -> T:
        """Create or update a record. Returns the saved item."""

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """Delete a record. Returns True if it existed."""
