"""Perhitungan harga jual dan kondisi kebangkrutan."""
from config import DIFFICULTY_MULTIPLIERS, QUALITY_MULTIPLIERS


class EconomySystem:
    @staticmethod
    def selling_price(base_price: int, difficulty: str, quality: str) -> int:
        difficulty_factor = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
        quality_factor = QUALITY_MULTIPLIERS.get(quality, 0.7)
        return max(1, round(base_price * difficulty_factor * quality_factor))

    @staticmethod
    def is_bankrupt(player) -> bool:
        """Kalah ketika tidak ada uang, hasil masakan, atau stok bahan tersisa."""
        has_food = bool(player.food_inventory)
        has_ingredients = any(qty > 0 for qty in player.ingredient_stock.values())
        return player.money <= 0 and not has_food and not has_ingredients
