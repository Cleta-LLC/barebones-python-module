"""Schemas for the example service.

Every service defines its own I/O models here.
These schemas are the *only* types that cross the service boundary.
"""

from pydantic import Field

from myapp.shared.schemas import BaseRecord


class Item(BaseRecord):
    """An example domain record."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    tags: list[str] = Field(default_factory=list)


class ItemCreate(Item):
    """Input model for creating an item (id is auto-generated if blank)."""

    id: str = Field(default="")  # allow caller to omit; API fills it in
    schema_version: int = 1
