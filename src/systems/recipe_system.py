"""Memuat dan memvalidasi resep dari file JSON individual."""
import json
from pathlib import Path
from typing import Any


class RecipeSystem:
    def __init__(self, recipes_dir: str | Path, ingredient_ids: set[str]):
        self.recipes_dir = Path(recipes_dir)
        self.ingredient_ids = ingredient_ids
        self.recipes: dict[str, dict[str, Any]] = {}
        self.errors: list[str] = []
        self.reload()

    def reload(self) -> None:
        self.recipes.clear()
        self.errors.clear()
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(self.recipes_dir.glob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                self._validate(data, path.name)
                recipe_id = data["id"]
                if recipe_id in self.recipes:
                    raise ValueError(f"Duplicate recipe id: {recipe_id}")
                self.recipes[recipe_id] = data
            except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
                self.errors.append(f"{path.name}: {exc}")

    def _validate(self, data: dict[str, Any], filename: str) -> None:
        required = ("id", "name", "difficulty", "ingredients", "cooking_time", "base_price")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        if data["difficulty"] not in {"easy", "normal", "hard"}:
            raise ValueError("difficulty must be easy, normal, or hard")
        ingredients = data["ingredients"]
        if not isinstance(ingredients, list) or not 1 <= len(ingredients) <= 5:
            raise ValueError("a recipe must contain between 1 and 5 ingredient steps")
        for step in ingredients:
            if not isinstance(step, dict):
                raise ValueError("each ingredient step must be an object")
            if "id" not in step or "timing" not in step:
                raise ValueError("each ingredient step needs id and timing")
            if step["id"] not in self.ingredient_ids:
                raise ValueError(f"unknown ingredient id: {step['id']}")
            if int(step.get("quantity", 1)) < 1 or float(step["timing"]) < 0:
                raise ValueError("quantity must be >= 1 and timing must be >= 0")
        if float(data["cooking_time"]) < 0 or int(data["base_price"]) < 1:
            raise ValueError("cooking_time must be >= 0 and base_price must be >= 1")

    def get(self, recipe_id: str) -> dict[str, Any] | None:
        return self.recipes.get(recipe_id)

    def all(self) -> list[dict[str, Any]]:
        return list(self.recipes.values())
