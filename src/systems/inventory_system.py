"""Operasi stok bahan dan inventori makanan."""
from src.entities.food import Food
from src.entities.player import Player


class InventorySystem:
    def __init__(self, player: Player):
        self.player = player

    def has_ingredients(self, recipe: dict) -> tuple[bool, list[str]]:
        missing = []
        for step in recipe["ingredients"]:
            ingredient_id = step["id"]
            needed = int(step.get("quantity", 1))
            available = self.player.ingredient_stock.get(ingredient_id, 0)
            if available < needed:
                missing.append(f"{ingredient_id}: perlu {needed}, tersedia {available}")
        return not missing, missing

    def consume_recipe_ingredients(self, recipe: dict) -> None:
        available, missing = self.has_ingredients(recipe)
        if not available:
            raise ValueError("Bahan tidak cukup: " + "; ".join(missing))
        for step in recipe["ingredients"]:
            self.player.remove_ingredient(step["id"], int(step.get("quantity", 1)))

    def add_food(self, food: Food) -> None:
        self.player.food_inventory.append(food)

    def find_food(self, instance_id: str) -> Food | None:
        return next((food for food in self.player.food_inventory if food.instance_id == instance_id), None)
