"""Regression tests for the default Cooking TXT ingredient/recipe economy."""
import json
import unittest
from pathlib import Path

from src.systems.economy_system import EconomySystem

ROOT = Path(__file__).resolve().parents[1]


def load_json_folder(folder: Path) -> dict[str, dict]:
    records = {}
    for path in sorted(folder.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            record = json.load(handle)
        records[record["id"]] = record
    return records


class EconomyBalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ingredients = load_json_folder(ROOT / "data" / "ingredients")
        cls.recipes = load_json_folder(ROOT / "data" / "recipes")

    def recipe_cost(self, recipe: dict) -> int:
        return sum(
            self.ingredients[step["id"]]["market_price"] * int(step.get("quantity", 1))
            for step in recipe["ingredients"]
        )

    def test_every_default_recipe_loses_money_at_poor_quality(self):
        default_ids = {
            "egg_fried_rice",
            "lemon_chicken",
            "shrimp_salad",
            "beef_fried_rice",
            "salmon_pie",
            "creamy_lemon_shrimp_rice",
        }
        for recipe_id in default_ids:
            with self.subTest(recipe=recipe_id):
                recipe = self.recipes[recipe_id]
                cost = self.recipe_cost(recipe)
                revenue = EconomySystem.selling_price(
                    recipe["base_price"], recipe["difficulty"], "poor"
                )
                self.assertLess(revenue, cost)

    def test_mid_and_good_quality_remain_profitable(self):
        default_ids = {
            "egg_fried_rice",
            "lemon_chicken",
            "shrimp_salad",
            "beef_fried_rice",
            "salmon_pie",
            "creamy_lemon_shrimp_rice",
        }
        for recipe_id in default_ids:
            with self.subTest(recipe=recipe_id):
                recipe = self.recipes[recipe_id]
                cost = self.recipe_cost(recipe)
                mid_revenue = EconomySystem.selling_price(
                    recipe["base_price"], recipe["difficulty"], "mid"
                )
                good_revenue = EconomySystem.selling_price(
                    recipe["base_price"], recipe["difficulty"], "good"
                )
                self.assertGreater(mid_revenue, cost)
                self.assertGreater(good_revenue, mid_revenue)

    def test_recipe_costs_match_balance_baseline(self):
        expected_costs = {
            "egg_fried_rice": 10,
            "lemon_chicken": 30,
            "shrimp_salad": 35,
            "beef_fried_rice": 50,
            "salmon_pie": 67,
            "creamy_lemon_shrimp_rice": 39,
        }
        for recipe_id, expected_cost in expected_costs.items():
            with self.subTest(recipe=recipe_id):
                self.assertEqual(self.recipe_cost(self.recipes[recipe_id]), expected_cost)


if __name__ == "__main__":
    unittest.main()
