"""Representasi bahan makanan yang dibaca dari JSON."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Ingredient:
    id: str
    name: str
    category: str
    market_price: int
    image: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ingredient":
        required = ("id", "name", "category", "market_price")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Ingredient JSON missing fields: {', '.join(missing)}")
        price = int(data["market_price"])
        if price < 0:
            raise ValueError("market_price cannot be negative")
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            market_price=price,
            image=str(data.get("image", "")),
            description=str(data.get("description", "")),
        )
