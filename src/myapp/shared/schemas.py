"""Base schema definitions shared across services."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    """Return current UTC time."""
    return datetime.now(UTC)


class BaseRecord(BaseModel):
    """Base for all persisted records.

    Every record that crosses a service boundary or gets stored
    must inherit from this model.
    """

    id: str = Field(..., description="Unique identifier")
    schema_version: int = Field(default=1, description="Schema version for migrations")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def model_post_init(self, __context: Any) -> None:
        """Ensure updated_at is refreshed on mutation."""


class ServiceResponse(BaseModel):
    """Standard response wrapper for service API calls."""

    success: bool
    message: str = ""
    data: Any = None
    errors: list[str] = Field(default_factory=list)
