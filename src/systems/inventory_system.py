"""Operasi stok bahan dan inventori makanan.

Bahan resep baru dikonsumsi ketika hasil masakan berhasil disimpan. Selama
sesi memasak berlangsung, stok pemain tetap utuh sehingga crash atau pembatalan
tidak menghilangkan bahan.
"""
from collections.abc import Callable

from src.entities.food import Food
from src.entities.player import Player


class InventorySystem:
    def __init__(self, player: Player):
        self.player = player

    @staticmethod
    def ingredient_requirements(recipe: dict) -> dict[str, int]:
        """Gabungkan kebutuhan bahan, termasuk jika ID yang sama muncul berulang."""
        requirements: dict[str, int] = {}
        for step in recipe.get("ingredients", []):
            ingredient_id = str(step["id"])
            quantity = int(step.get("quantity", 1))
            if quantity < 1:
                raise ValueError(f"Invalid ingredient quantity for {ingredient_id}")
            requirements[ingredient_id] = requirements.get(ingredient_id, 0) + quantity
        return requirements

    def has_ingredients(self, recipe: dict) -> tuple[bool, list[str]]:
        missing = []
        for ingredient_id, needed in self.ingredient_requirements(recipe).items():
            available = self.player.ingredient_stock.get(ingredient_id, 0)
            if available < needed:
                missing.append(
                    f"{ingredient_id}: perlu {needed}, tersedia {available}"
                )
        return not missing, missing

    def consume_recipe_ingredients(self, recipe: dict) -> None:
        """Konsumsi seluruh kebutuhan secara all-or-nothing."""
        requirements = self.ingredient_requirements(recipe)
        available, missing = self.has_ingredients(recipe)
        if not available:
            raise ValueError("Bahan tidak cukup: " + "; ".join(missing))
        # Semua kebutuhan telah divalidasi dan dijumlahkan sebelum stok diubah.
        for ingredient_id, quantity in requirements.items():
            self.player.remove_ingredient(ingredient_id, quantity)

    def complete_recipe(
        self,
        recipe: dict,
        food: Food,
        persist: Callable[[], bool] | None = None,
    ) -> bool:
        """Commit konsumsi bahan + makanan, dan opsional simpan sebelum sukses.

        Operasi ini atomik di memori. Jika callback persist mengembalikan False
        atau melempar exception, stok dan inventori dipulihkan.
        """
        if any(item.instance_id == food.instance_id for item in self.player.food_inventory):
            raise ValueError(f"Food instance already exists: {food.instance_id}")

        available, missing = self.has_ingredients(recipe)
        if not available:
            raise ValueError("Bahan tidak cukup untuk menyelesaikan masakan: " + "; ".join(missing))

        original_stock = dict(self.player.ingredient_stock)
        original_food_inventory = list(self.player.food_inventory)
        try:
            self.consume_recipe_ingredients(recipe)
            self.player.food_inventory.append(food)
            if persist is not None and not persist():
                self.player.ingredient_stock = original_stock
                self.player.food_inventory = original_food_inventory
                return False
        except Exception:
            self.player.ingredient_stock = original_stock
            self.player.food_inventory = original_food_inventory
            raise
        return True

    def add_food(self, food: Food) -> None:
        self.player.food_inventory.append(food)

    def find_food(self, instance_id: str) -> Food | None:
        return next(
            (food for food in self.player.food_inventory if food.instance_id == instance_id),
            None,
        )
