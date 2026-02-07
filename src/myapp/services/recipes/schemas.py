"""Schemas for the recipes service.

These models are the only types that cross the service boundary.
"""

from enum import StrEnum

from pydantic import Field, field_validator

from myapp.shared.schemas import BaseRecord


class Unit(StrEnum):
    """Measurement units for ingredients."""

    CUP = "cup"
    TBSP = "tbsp"
    TSP = "tsp"
    OZ = "oz"
    G = "g"
    KG = "kg"
    ML = "ml"
    L = "l"
    LB = "lb"
    PIECE = "piece"
    PINCH = "pinch"
    WHOLE = "whole"


class Ingredient(BaseRecord):
    """A single ingredient line in a recipe."""

    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: Unit = Unit.WHOLE
    notes: str = ""


class Recipe(BaseRecord):
    """A baking recipe with ingredients and step-by-step instructions."""

    name: str = Field(..., min_length=1, max_length=300)
    description: str = ""
    category: str = Field(default="other", description="e.g. bread, cake, cookie, pastry")
    ingredients: list[Ingredient] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list, description="Ordered preparation steps")
    prep_time_minutes: int = Field(default=0, ge=0)
    cook_time_minutes: int = Field(default=0, ge=0)
    servings: int = Field(default=1, ge=1)
    temperature_f: int | None = Field(default=None, description="Oven temp in Fahrenheit")
    tags: list[str] = Field(default_factory=list)

    @field_validator("steps")
    @classmethod
    def steps_not_empty_strings(cls, v: list[str]) -> list[str]:
        return [s for s in v if s.strip()]

    @property
    def total_time_minutes(self) -> int:
        return self.prep_time_minutes + self.cook_time_minutes

    @property
    def temperature_c(self) -> int | None:
        if self.temperature_f is None:
            return None
        return round((self.temperature_f - 32) * 5 / 9)


class RecipeCreate(Recipe):
    """Input model for creating a recipe (id auto-generated if blank)."""

    id: str = Field(default="")
    schema_version: int = 1
