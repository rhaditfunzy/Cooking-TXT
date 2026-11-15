"""Keranjang belanja dan transaksi market."""
from typing import Any
from src.entities.player import Player


class MarketSystem:
    def __init__(self, ingredients: dict[str, Any]):
        self.ingredients = ingredients
        self.cart: dict[str, int] = {}

    def add_to_cart(self, ingredient_id: str, quantity: int) -> None:
        if ingredient_id not in self.ingredients:
            raise ValueError(f"Unknown ingredient: {ingredient_id}")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.cart[ingredient_id] = self.cart.get(ingredient_id, 0) + quantity

    def change_cart_quantity(self, ingredient_id: str, delta: int) -> None:
        updated = self.cart.get(ingredient_id, 0) + delta
        if updated <= 0:
            self.cart.pop(ingredient_id, None)
        else:
            self.cart[ingredient_id] = updated

    def clear_cart(self) -> None:
        self.cart.clear()

    def cart_total(self) -> int:
        return sum(self.ingredients[key].market_price * qty for key, qty in self.cart.items())

    def checkout(self, player: Player) -> tuple[bool, str, int]:
        """Checkout atomik: saldo dan stok berubah hanya jika dana mencukupi."""
        if not self.cart:
            return False, "Keranjang masih kosong.", 0
        total = self.cart_total()
        if player.money < total:
            return False, f"Uang tidak cukup. Total Rp{total:,}.", total
        for ingredient_id, quantity in self.cart.items():
            player.add_ingredient(ingredient_id, quantity)
        player.money -= total
        player.total_expenses += total
        self.clear_cart()
        return True, f"Pembelian berhasil. Total Rp{total:,}.", total
