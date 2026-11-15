"""Representasi satu hasil masakan di inventori pemain."""
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Food:
    instance_id: str
    recipe_id: str
    name: str
    difficulty: str
    quality: str
    base_price: int
    image: str = ""
    sold_price: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Food":
        return cls(
            instance_id=str(data["instance_id"]),
            recipe_id=str(data["recipe_id"]),
            name=str(data["name"]),
            difficulty=str(data["difficulty"]),
            quality=str(data["quality"]),
            base_price=int(data["base_price"]),
            image=str(data.get("image", "")),
            sold_price=data.get("sold_price"),
        )
