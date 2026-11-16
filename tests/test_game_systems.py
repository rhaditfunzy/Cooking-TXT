
"""Tes otomatis untuk logika permainan tanpa membuka jendela Pygame."""

import unittest
import tempfile
from pathlib import Path

from src.entities.player import Player
from src.entities.food import Food
from src.systems.cooking_system import CookingSystem
from src.systems.day_system import DaySystem
from src.systems.economy_system import EconomySystem
from src.systems.market_system import MarketSystem
from src.systems.recipe_system import RecipeSystem
from src.utils.json_loader import load_ingredients
from src.utils.save_manager import SaveManager


ROOT = Path(__file__).resolve().parents[1]


class GameSystemsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ingredients = load_ingredients(
            ROOT / "data" / "ingredients"
        )

        cls.recipes = RecipeSystem(
            ROOT / "data" / "recipes",
            set(cls.ingredients)
        )

    def test_json_data_loads(self):
        # Bahan bawaan yang wajib tersedia.
        required_ingredients = {
            "beef",
            "chicken_leg",
            "salmon_fillet",
            "shrimp",
            "lemon",
            "lettuce",
            "potato",
            "rice",
            "dough",
            "egg",
            "milk",
        }

        loaded_ingredients = set(self.ingredients)

        missing_ingredients = (
            required_ingredients - loaded_ingredients
        )

        self.assertFalse(
            missing_ingredients,
            f"Missing ingredients: {missing_ingredients}"
        )

        # Resep bawaan yang wajib tersedia.
        required_recipes = {
            "egg_fried_rice",
            "lemon_chicken",
            "shrimp_salad",
            "beef_fried_rice",
            "salmon_pie",
            "creamy_lemon_shrimp_rice",
        }

        loaded_recipes = {
            recipe["id"] for recipe in self.recipes.all()
        }

        missing_recipes = required_recipes - loaded_recipes

        self.assertFalse(
            missing_recipes,
            f"Missing recipes: {missing_recipes}"
        )

        # Pastikan tidak ada JSON resep yang gagal dimuat.
        self.assertEqual(
            self.recipes.errors,
            [],
            f"Recipe loading errors: {self.recipes.errors}"
        )

    def test_market_checkout_success(self):
        player = Player(money=100)
        market = MarketSystem(self.ingredients)

        market.add_to_cart("rice", 2)

        success, _, total = market.checkout(player)

        self.assertTrue(success)
        self.assertEqual(total, 8)
        self.assertEqual(player.money, 92)
        self.assertEqual(player.ingredient_stock["rice"], 2)
        self.assertEqual(player.total_expenses, 8)
        self.assertEqual(market.cart, {})

    def test_market_checkout_failure_is_atomic(self):
        player = Player(money=1)
        market = MarketSystem(self.ingredients)

        market.add_to_cart("beef", 1)

        success, _, _ = market.checkout(player)

        self.assertFalse(success)
        self.assertEqual(player.money, 1)
        self.assertEqual(player.ingredient_stock, {})
        self.assertEqual(market.cart, {"beef": 1})

    def test_recipe_cooking_perfect_timing_is_good(self):
        recipe = self.recipes.get("egg_fried_rice")

        cooking = CookingSystem()
        cooking.start(recipe, 100.0)

        cooking.update(103.0)
        cooking.submit_action(105.0)
        cooking.submit_action(115.0)

        food = cooking.submit_action(135.0)

        self.assertIsNotNone(food)
        self.assertEqual(food.quality, "good")
        self.assertEqual(cooking.phase, "finished")

    def test_recipe_cooking_late_timing_is_poor(self):
        recipe = self.recipes.get("egg_fried_rice")

        cooking = CookingSystem()
        cooking.start(recipe, 0.0)

        cooking.update(3.0)
        cooking.submit_action(5.0 + 1.2)
        cooking.submit_action(16.2)

        food = cooking.submit_action(36.2)

        self.assertIsNotNone(food)
        self.assertEqual(food.quality, "poor")

    def test_daily_sales_limit(self):
        player = Player(daily_sell_limit=5)

        for _ in range(5):
            DaySystem.register_sale(player)

        self.assertFalse(DaySystem.can_sell(player))

        DaySystem.end_day(player)

        self.assertTrue(DaySystem.can_sell(player))
        self.assertEqual(player.day, 2)
        self.assertEqual(player.daily_sales, 0)

    def test_selling_price_uses_difficulty_and_quality(self):
        self.assertEqual(
            EconomySystem.selling_price(100, "easy", "good"),
            115
        )

        self.assertEqual(
            EconomySystem.selling_price(100, "hard", "poor"),
            112
        )

    def test_bankruptcy_requires_no_money_no_food_and_no_ingredients(self):
        player = Player(money=0)

        self.assertTrue(EconomySystem.is_bankrupt(player))

        player.add_ingredient("rice", 1)

        self.assertFalse(EconomySystem.is_bankrupt(player))

        player.remove_ingredient("rice", 1)

        player.food_inventory.append(
            Food(
                "x",
                "egg_fried_rice",
                "Egg Fried Rice",
                "easy",
                "good",
                45
            )
        )

        self.assertFalse(EconomySystem.is_bankrupt(player))

    def test_save_manager_round_trip(self):
        player = Player(money=123, day=4)

        player.add_ingredient("rice", 3)

        with tempfile.TemporaryDirectory() as folder:
            manager = SaveManager(
                Path(folder) / "player.json"
            )

            manager.save(player)
            restored = manager.load()

        self.assertIsNotNone(restored)
        self.assertEqual(restored.money, 123)
        self.assertEqual(restored.day, 4)
        self.assertEqual(restored.ingredient_stock["rice"], 3)


if __name__ == "__main__":
    unittest.main()
