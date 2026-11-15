"""Loader JSON untuk data bahan dan konfigurasi data."""
import json
from pathlib import Path
from src.entities.ingredient import Ingredient


def load_ingredients(directory: str | Path) -> dict[str, Ingredient]:
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    loaded: dict[str, Ingredient] = {}
    errors: list[str] = []
    for path in sorted(folder.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as file:
                item = Ingredient.from_dict(json.load(file))
            if item.id in loaded:
                raise ValueError(f"duplicate ingredient id: {item.id}")
            loaded[item.id] = item
        except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
            errors.append(f"{path.name}: {exc}")
    if errors:
        raise ValueError("Ingredient data error(s):\n" + "\n".join(errors))
    return loaded
