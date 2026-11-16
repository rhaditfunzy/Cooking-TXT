"""Update unsold foods in the local save to the rebalanced recipe base prices.

Run once from the Cooking-TXT project root:
    python migrate_economy_save.py
A timestamped backup is created before the save is changed.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAVE_PATH = ROOT / "saves" / "player_save.json"
RECIPES_PATH = ROOT / "data" / "recipes"


def main() -> int:
    if not SAVE_PATH.exists():
        print("Tidak ada saves/player_save.json. Tidak ada data save yang perlu dimigrasikan.")
        return 0

    recipes = {}
    for path in RECIPES_PATH.glob("*.json"):
        with path.open("r", encoding="utf-8") as handle:
            recipe = json.load(handle)
        recipes[recipe["id"]] = recipe

    with SAVE_PATH.open("r", encoding="utf-8") as handle:
        save_data = json.load(handle)

    foods = save_data.get("food_inventory", [])
    if not isinstance(foods, list):
        raise SystemExit("Format save tidak valid: food_inventory bukan list.")

    changed = 0
    for food in foods:
        recipe = recipes.get(food.get("recipe_id"))
        if recipe is None:
            continue
        new_base_price = int(recipe["base_price"])
        if int(food.get("base_price", -1)) != new_base_price:
            food["base_price"] = new_base_price
            changed += 1

    if changed == 0:
        print("Save sudah sesuai dengan harga ekonomi baru; tidak ada perubahan.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = SAVE_PATH.with_name(f"player_save.before_economy_rebalance_{stamp}.json")
    shutil.copy2(SAVE_PATH, backup_path)

    temp_path = SAVE_PATH.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(save_data, handle, ensure_ascii=False, indent=4)
        handle.write("\n")
    temp_path.replace(SAVE_PATH)

    print(f"Berhasil memperbarui {changed} makanan di inventori.")
    print(f"Backup save: {backup_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
