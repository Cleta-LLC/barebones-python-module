"""Public API for the recipes service.

Other services and the CLI should only import from this module.
"""

import uuid

from myapp.services.recipes.schemas import Ingredient, Recipe, RecipeCreate, Unit  # noqa: F401
from myapp.services.recipes.storage import RecipesJsonStore, RecipesSqliteStore
from myapp.shared.persistence.base import BaseStore
from myapp.shared.schemas import ServiceResponse, utcnow

# Re-export schema types for convenience (they're used in SEED_RECIPES below)
__all__ = ["RecipesService", "Ingredient", "Recipe", "RecipeCreate", "Unit"]


# ── built-in seed recipes ─────────────────────────────────────────────

SEED_RECIPES: list[RecipeCreate] = [
    RecipeCreate(
        id="banana-bread",
        name="Classic Banana Bread",
        description="Moist banana bread with a golden crust. Perfect for overripe bananas.",
        category="bread",
        ingredients=[
            Ingredient(id="i1", name="ripe bananas", quantity=3, unit=Unit.WHOLE),
            Ingredient(id="i2", name="all-purpose flour", quantity=1.5, unit=Unit.CUP),
            Ingredient(id="i3", name="sugar", quantity=0.75, unit=Unit.CUP),
            Ingredient(id="i4", name="butter, melted", quantity=0.33, unit=Unit.CUP),
            Ingredient(id="i5", name="egg", quantity=1, unit=Unit.WHOLE),
            Ingredient(id="i6", name="baking soda", quantity=1, unit=Unit.TSP),
            Ingredient(id="i7", name="salt", quantity=1, unit=Unit.PINCH),
            Ingredient(id="i8", name="vanilla extract", quantity=1, unit=Unit.TSP),
        ],
        steps=[
            "Preheat oven to 350°F (175°C). Grease a 9x5 loaf pan.",
            "Mash bananas in a large bowl until smooth.",
            "Mix in melted butter, sugar, egg, and vanilla.",
            "Sprinkle baking soda and salt over the mixture, then stir in.",
            "Fold in flour until just combined — do not overmix.",
            "Pour batter into prepared pan.",
            "Bake 55-65 minutes until a toothpick comes out clean.",
            "Cool in pan for 10 minutes, then turn out onto a wire rack.",
        ],
        prep_time_minutes=15,
        cook_time_minutes=60,
        servings=10,
        temperature_f=350,
        tags=["quick", "beginner", "freezer-friendly"],
    ),
    RecipeCreate(
        id="chocolate-chip-cookies",
        name="Chocolate Chip Cookies",
        description="Crispy edges, chewy center. The one recipe you'll memorize.",
        category="cookie",
        ingredients=[
            Ingredient(id="i1", name="all-purpose flour", quantity=2.25, unit=Unit.CUP),
            Ingredient(id="i2", name="butter, softened", quantity=1, unit=Unit.CUP),
            Ingredient(id="i3", name="granulated sugar", quantity=0.75, unit=Unit.CUP),
            Ingredient(id="i4", name="brown sugar, packed", quantity=0.75, unit=Unit.CUP),
            Ingredient(id="i5", name="eggs", quantity=2, unit=Unit.WHOLE),
            Ingredient(id="i6", name="vanilla extract", quantity=1, unit=Unit.TSP),
            Ingredient(id="i7", name="baking soda", quantity=1, unit=Unit.TSP),
            Ingredient(id="i8", name="salt", quantity=1, unit=Unit.TSP),
            Ingredient(id="i9", name="chocolate chips", quantity=2, unit=Unit.CUP),
        ],
        steps=[
            "Preheat oven to 375°F (190°C).",
            "Whisk flour, baking soda, and salt in a bowl. Set aside.",
            "Beat butter and both sugars until creamy (about 3 minutes).",
            "Beat in eggs one at a time, then vanilla.",
            "Gradually stir in the flour mixture until just blended.",
            "Fold in chocolate chips.",
            "Drop rounded tablespoons onto ungreased baking sheets.",
            "Bake 9-11 minutes until golden brown.",
            "Cool on baking sheet for 2 minutes, then transfer to wire rack.",
        ],
        prep_time_minutes=20,
        cook_time_minutes=10,
        servings=48,
        temperature_f=375,
        tags=["classic", "beginner", "crowd-pleaser"],
    ),
    RecipeCreate(
        id="sourdough-bread",
        name="Simple Sourdough Bread",
        description="A basic sourdough loaf with open crumb. Requires an active starter.",
        category="bread",
        ingredients=[
            Ingredient(id="i1", name="bread flour", quantity=500, unit=Unit.G),
            Ingredient(id="i2", name="water (warm)", quantity=350, unit=Unit.ML),
            Ingredient(id="i3", name="sourdough starter (active)", quantity=100, unit=Unit.G),
            Ingredient(id="i4", name="salt", quantity=10, unit=Unit.G),
        ],
        steps=[
            "Mix flour, water, and starter. Rest 30 minutes (autolyse).",
            "Add salt and a splash of water. Pinch and fold to incorporate.",
            "Stretch and fold every 30 minutes for 2 hours (4 sets).",
            "Bulk ferment at room temperature 4-6 hours until doubled.",
            "Shape into a round and place seam-side up in a floured banneton.",
            "Cold-proof in the refrigerator 8-16 hours.",
            "Preheat oven to 500°F (260°C) with a Dutch oven inside.",
            "Score the dough. Bake covered 20 minutes.",
            "Remove lid, reduce to 450°F (230°C), bake 20-25 more minutes.",
            "Cool on a wire rack at least 1 hour before slicing.",
        ],
        prep_time_minutes=30,
        cook_time_minutes=45,
        servings=1,
        temperature_f=500,
        tags=["sourdough", "advanced", "artisan"],
    ),
    RecipeCreate(
        id="blueberry-muffins",
        name="Blueberry Muffins",
        description="Tender, fluffy muffins bursting with blueberries and a sugar-crunch top.",
        category="pastry",
        ingredients=[
            Ingredient(id="i1", name="all-purpose flour", quantity=2, unit=Unit.CUP),
            Ingredient(id="i2", name="sugar", quantity=0.75, unit=Unit.CUP),
            Ingredient(id="i3", name="butter, melted", quantity=0.33, unit=Unit.CUP),
            Ingredient(id="i4", name="egg", quantity=1, unit=Unit.WHOLE),
            Ingredient(id="i5", name="milk", quantity=0.5, unit=Unit.CUP),
            Ingredient(id="i6", name="baking powder", quantity=2, unit=Unit.TSP),
            Ingredient(id="i7", name="salt", quantity=0.5, unit=Unit.TSP),
            Ingredient(id="i8", name="vanilla extract", quantity=1, unit=Unit.TSP),
            Ingredient(id="i9", name="fresh blueberries", quantity=1, unit=Unit.CUP),
            Ingredient(id="i10", name="coarse sugar (topping)", quantity=2, unit=Unit.TBSP),
        ],
        steps=[
            "Preheat oven to 375°F (190°C). Line a 12-cup muffin tin.",
            "Whisk flour, sugar, baking powder, and salt.",
            "In a separate bowl, mix melted butter, egg, milk, and vanilla.",
            "Pour wet ingredients into dry. Stir until just combined.",
            "Gently fold in blueberries — toss them in a little flour first to prevent sinking.",
            "Divide batter among muffin cups. Sprinkle coarse sugar on top.",
            "Bake 20-25 minutes until tops are golden and a toothpick comes out clean.",
            "Cool in pan 5 minutes, then transfer to a wire rack.",
        ],
        prep_time_minutes=10,
        cook_time_minutes=22,
        servings=12,
        temperature_f=375,
        tags=["quick", "beginner", "breakfast"],
    ),
    RecipeCreate(
        id="cinnamon-rolls",
        name="Cinnamon Rolls",
        description="Soft, pillowy rolls with swirls of cinnamon sugar and cream cheese frosting.",
        category="pastry",
        ingredients=[
            Ingredient(id="i1", name="all-purpose flour", quantity=4, unit=Unit.CUP),
            Ingredient(id="i2", name="whole milk (warm)", quantity=1, unit=Unit.CUP),
            Ingredient(id="i3", name="butter, softened", quantity=0.33, unit=Unit.CUP),
            Ingredient(id="i4", name="sugar", quantity=0.5, unit=Unit.CUP),
            Ingredient(id="i5", name="instant yeast", quantity=2.25, unit=Unit.TSP),
            Ingredient(id="i6", name="egg", quantity=1, unit=Unit.WHOLE),
            Ingredient(id="i7", name="salt", quantity=0.75, unit=Unit.TSP),
            Ingredient(id="i8", name="brown sugar (filling)", quantity=0.75, unit=Unit.CUP),
            Ingredient(id="i9", name="cinnamon (filling)", quantity=2, unit=Unit.TBSP),
            Ingredient(id="i10", name="butter, softened (filling)", quantity=0.25, unit=Unit.CUP),
            Ingredient(id="i11", name="cream cheese (frosting)", quantity=4, unit=Unit.OZ),
            Ingredient(id="i12", name="powdered sugar (frosting)", quantity=1, unit=Unit.CUP),
            Ingredient(id="i13", name="vanilla extract (frosting)", quantity=0.5, unit=Unit.TSP),
        ],
        steps=[
            "Warm milk to 110°F. Stir in yeast and a pinch of sugar. Let bloom 5 minutes.",
            "Mix flour, sugar, salt, egg, butter, and yeast mixture into a soft dough.",
            "Knead 8-10 minutes until smooth and elastic.",
            "Cover and let rise in a warm place 1 hour until doubled.",
            "Mix brown sugar and cinnamon for the filling.",
            "Roll dough into a large rectangle (~16x12 inches).",
            "Spread softened butter over dough. Sprinkle cinnamon sugar evenly.",
            "Roll tightly from the long side. Cut into 12 equal pieces.",
            "Place in a greased 9x13 pan. Cover and let rise 30 minutes.",
            "Preheat oven to 350°F (175°C). Bake 25-30 minutes until golden.",
            "While baking, beat cream cheese, powdered sugar, and vanilla for frosting.",
            "Spread frosting over warm rolls. Serve immediately.",
        ],
        prep_time_minutes=40,
        cook_time_minutes=28,
        servings=12,
        temperature_f=350,
        tags=["brunch", "intermediate", "crowd-pleaser"],
    ),
]


class RecipesService:
    """Facade that owns all recipes-service business logic."""

    def __init__(self, store: BaseStore[Recipe] | None = None) -> None:
        self._store = store or RecipesSqliteStore()

    # ── CRUD ──────────────────────────────────────────────────────────

    def create(self, data: RecipeCreate) -> ServiceResponse:
        recipe = Recipe(
            id=data.id or uuid.uuid4().hex[:12],
            name=data.name,
            description=data.description,
            category=data.category,
            ingredients=data.ingredients,
            steps=data.steps,
            prep_time_minutes=data.prep_time_minutes,
            cook_time_minutes=data.cook_time_minutes,
            servings=data.servings,
            temperature_f=data.temperature_f,
            tags=data.tags,
            schema_version=data.schema_version,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        saved = self._store.save(recipe)
        return ServiceResponse(success=True, message="Recipe created", data=saved.model_dump())

    def get(self, recipe_id: str) -> ServiceResponse:
        recipe = self._store.get(recipe_id)
        if recipe is None:
            return ServiceResponse(success=False, message="Not found", errors=[f"id={recipe_id}"])
        return ServiceResponse(success=True, data=recipe.model_dump())

    def list_recipes(self) -> ServiceResponse:
        recipes = self._store.list_all()
        return ServiceResponse(
            success=True,
            data=[r.model_dump() for r in recipes],
            message=f"{len(recipes)} recipe(s)",
        )

    def delete(self, recipe_id: str) -> ServiceResponse:
        deleted = self._store.delete(recipe_id)
        if not deleted:
            return ServiceResponse(success=False, message="Not found", errors=[f"id={recipe_id}"])
        return ServiceResponse(success=True, message="Recipe deleted")

    def search(self, query: str) -> ServiceResponse:
        """Search recipes by name, category, or tag (case-insensitive)."""
        q = query.lower()
        recipes = self._store.list_all()
        matches = [
            r
            for r in recipes
            if q in r.name.lower() or q in r.category.lower() or any(q in t.lower() for t in r.tags)
        ]
        return ServiceResponse(
            success=True,
            data=[r.model_dump() for r in matches],
            message=f"{len(matches)} match(es) for '{query}'",
        )

    # ── seed ──────────────────────────────────────────────────────────

    def seed(self) -> ServiceResponse:
        """Load built-in seed recipes into the store."""
        count = 0
        for recipe_data in SEED_RECIPES:
            if self._store.get(recipe_data.id) is None:
                self.create(recipe_data)
                count += 1
        return ServiceResponse(
            success=True,
            message=f"Seeded {count} new recipe(s) ({len(SEED_RECIPES) - count} already existed)",
            data={"seeded": count, "skipped": len(SEED_RECIPES) - count},
        )

    # ── export / import ───────────────────────────────────────────────

    def export_json(self) -> ServiceResponse:
        """Export current store contents to the JSON backend."""
        json_store = RecipesJsonStore()
        recipes = self._store.list_all()
        for recipe in recipes:
            json_store.save(recipe)
        path = str(json_store.path)
        return ServiceResponse(
            success=True,
            message=f"Exported {len(recipes)} recipe(s) to {path}",
            data={"path": path, "count": len(recipes)},
        )

    def import_json(self) -> ServiceResponse:
        """Import recipes from the JSON backend into the current store."""
        json_store = RecipesJsonStore()
        recipes = json_store.list_all()
        for recipe in recipes:
            self._store.save(recipe)
        return ServiceResponse(
            success=True,
            message=f"Imported {len(recipes)} recipe(s) from JSON",
            data={"count": len(recipes)},
        )
