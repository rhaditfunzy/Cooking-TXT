"""Regression tests for v0.3.1b transactional cooking."""

import tempfile
import unittest
from pathlib import Path

from src.entities.player import Player
from src.systems.cooking_system import CookingSystem
from src.systems.inventory_system import InventorySystem
from src.systems.recipe_system import RecipeSystem
from src.utils.json_loader import load_ingredients
from src.utils.save_manager import SaveManager

ROOT = Path(__file__).resolve().parents[1]


class TransactionalCookingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ingredients = load_ingredients(ROOT / "data" / "ingredients")
        cls.recipes = RecipeSystem(
            ROOT / "data" / "recipes", set(cls.ingredients.keys())
        )
        cls.recipe = cls.recipes.get("egg_fried_rice")

    def make_player(self):
        player = Player(money=250)
        player.add_ingredient("rice", 3)
        player.add_ingredient("egg", 2)
        return player

    def finish_recipe(self, cooking, recipe):
        cooking.start(recipe, 100.0)
        cooking.update(103.0)
        cooking.submit_action(105.0)  # rice
        cooking.submit_action(115.0)  # egg
        return cooking.submit_action(135.0)  # take food

    def test_start_and_cancel_do_not_consume_ingredients(self):
        player = self.make_player()
        inventory = InventorySystem(player)
        before = dict(player.ingredient_stock)
        cooking = CookingSystem()

        cooking.start(self.recipe, 100.0)
        self.assertEqual(player.ingredient_stock, before)

        cooking.reset()  # equivalent to player cancelling the active session
        self.assertEqual(player.ingredient_stock, before)
        self.assertEqual(player.food_inventory, [])

    def test_crash_before_completion_keeps_saved_ingredients(self):
        player = self.make_player()
        with tempfile.TemporaryDirectory() as folder:
            save_path = Path(folder) / "player_save.json"
            manager = SaveManager(save_path)
            manager.save(player)

            cooking = CookingSystem()
            cooking.start(self.recipe, 100.0)
            cooking.update(cooking.countdown_end)
            cooking.submit_action(cooking.target_time)
            # Simulated process crash: no completion transaction is committed.

            restored = SaveManager(save_path).load()

        self.assertIsNotNone(restored)
        self.assertEqual(restored.ingredient_stock, {"rice": 3, "egg": 2})
        self.assertEqual(restored.food_inventory, [])

    def test_completed_recipe_consumes_ingredients_and_adds_one_food(self):
        player = self.make_player()
        inventory = InventorySystem(player)
        cooking = CookingSystem()

        food = self.finish_recipe(cooking, self.recipe)
        self.assertIsNotNone(food)
        self.assertEqual(player.ingredient_stock, {"rice": 3, "egg": 2})

        inventory.complete_recipe(self.recipe, food)

        self.assertEqual(player.ingredient_stock, {"rice": 2, "egg": 1})
        self.assertEqual(len(player.food_inventory), 1)
        self.assertEqual(player.food_inventory[0].instance_id, food.instance_id)

    def test_failed_persistence_rolls_back_ingredients_and_food(self):
        player = self.make_player()
        inventory = InventorySystem(player)
        cooking = CookingSystem()
        food = self.finish_recipe(cooking, self.recipe)
        before = dict(player.ingredient_stock)

        committed = inventory.complete_recipe(
            self.recipe, food, persist=lambda: False
        )

        self.assertFalse(committed)
        self.assertEqual(player.ingredient_stock, before)
        self.assertEqual(player.food_inventory, [])

    def test_persistence_exception_rolls_back_ingredients_and_food(self):
        player = self.make_player()
        inventory = InventorySystem(player)
        cooking = CookingSystem()
        food = self.finish_recipe(cooking, self.recipe)
        before = dict(player.ingredient_stock)

        def fail_save():
            raise OSError("simulated disk failure")

        with self.assertRaises(OSError):
            inventory.complete_recipe(self.recipe, food, persist=fail_save)

        self.assertEqual(player.ingredient_stock, before)
        self.assertEqual(player.food_inventory, [])

    def test_completed_transaction_survives_save_and_reload(self):
        player = self.make_player()
        inventory = InventorySystem(player)
        cooking = CookingSystem()
        food = self.finish_recipe(cooking, self.recipe)
        inventory.complete_recipe(self.recipe, food)

        with tempfile.TemporaryDirectory() as folder:
            save_path = Path(folder) / "player_save.json"
            SaveManager(save_path).save(player)
            restored = SaveManager(save_path).load()

        self.assertEqual(restored.ingredient_stock, {"rice": 2, "egg": 1})
        self.assertEqual(len(restored.food_inventory), 1)
        self.assertEqual(restored.food_inventory[0].instance_id, food.instance_id)

    def test_duplicate_completion_is_rejected_without_mutation(self):
        player = self.make_player()
        inventory = InventorySystem(player)
        cooking = CookingSystem()
        food = self.finish_recipe(cooking, self.recipe)
        inventory.complete_recipe(self.recipe, food)
        after_first_commit = dict(player.ingredient_stock)

        with self.assertRaises(ValueError):
            inventory.complete_recipe(self.recipe, food)

        self.assertEqual(player.ingredient_stock, after_first_commit)
        self.assertEqual(len(player.food_inventory), 1)

    def test_insufficient_ingredients_do_not_partially_consume_stock(self):
        player = Player(money=100)
        player.add_ingredient("rice", 1)
        # Resep membutuhkan rice dan egg; stok egg sengaja tidak tersedia.
        inventory = InventorySystem(player)
        cooking = CookingSystem()
        food = self.finish_recipe(cooking, self.recipe)
        before = dict(player.ingredient_stock)

        with self.assertRaises(ValueError):
            inventory.complete_recipe(self.recipe, food)

        self.assertEqual(player.ingredient_stock, before)
        self.assertEqual(player.food_inventory, [])

    def test_repeated_ingredient_steps_are_aggregated(self):
        player = Player()
        player.add_ingredient("rice", 2)
        inventory = InventorySystem(player)
        recipe = {
            "ingredients": [
                {"id": "rice", "quantity": 1},
                {"id": "rice", "quantity": 2},
            ]
        }

        enough, missing = inventory.has_ingredients(recipe)

        self.assertFalse(enough)
        self.assertEqual(missing, ["rice: perlu 3, tersedia 2"])
        self.assertEqual(player.ingredient_stock, {"rice": 2})


if __name__ == "__main__":
    unittest.main()
