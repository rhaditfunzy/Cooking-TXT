"""Data pemain dan serialisasi untuk save game."""
from dataclasses import dataclass, field
from typing import Any
from config import STARTING_MONEY, STARTING_DAY, DAILY_SELL_LIMIT
from .food import Food


@dataclass
class Player:
    money: int = STARTING_MONEY
    day: int = STARTING_DAY
    daily_sales: int = 0
    daily_sell_limit: int = DAILY_SELL_LIMIT
    ingredient_stock: dict[str, int] = field(default_factory=dict)
    food_inventory: list[Food] = field(default_factory=list)
    total_revenue: int = 0
    total_expenses: int = 0
    total_items_sold: int = 0

    @property
    def net_profit(self) -> int:
        """Akumulasi pendapatan penjualan dikurangi biaya belanja bahan."""
        return self.total_revenue - self.total_expenses

    def add_ingredient(self, ingredient_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.ingredient_stock[ingredient_id] = self.ingredient_stock.get(ingredient_id, 0) + quantity

    def remove_ingredient(self, ingredient_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        current = self.ingredient_stock.get(ingredient_id, 0)
        if current < quantity:
            raise ValueError(f"Not enough {ingredient_id}: need {quantity}, have {current}")
        remaining = current - quantity
        if remaining:
            self.ingredient_stock[ingredient_id] = remaining
        else:
            self.ingredient_stock.pop(ingredient_id, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "money": self.money,
            "day": self.day,
            "daily_sales": self.daily_sales,
            "daily_sell_limit": self.daily_sell_limit,
            "ingredient_stock": self.ingredient_stock,
            "food_inventory": [food.to_dict() for food in self.food_inventory],
            "total_revenue": self.total_revenue,
            "total_expenses": self.total_expenses,
            "total_items_sold": self.total_items_sold,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Player":
        player = cls(
            money=int(data.get("money", STARTING_MONEY)),
            day=int(data.get("day", STARTING_DAY)),
            daily_sales=int(data.get("daily_sales", 0)),
            daily_sell_limit=int(data.get("daily_sell_limit", DAILY_SELL_LIMIT)),
            ingredient_stock={str(k): int(v) for k, v in data.get("ingredient_stock", {}).items()},
            food_inventory=[Food.from_dict(item) for item in data.get("food_inventory", [])],
            total_revenue=int(data.get("total_revenue", 0)),
            total_expenses=int(data.get("total_expenses", 0)),
            total_items_sold=int(data.get("total_items_sold", 0)),
        )
        if player.money < 0 or player.day < 1 or player.daily_sales < 0:
            raise ValueError("Invalid player save values")
        return player
