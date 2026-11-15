# 07 — API Reference

Dokumen ini merujuk ke API internal Python pada build awal. Parameter `now` pada cooking menggunakan satuan detik dari clock monoton, bukan tanggal/jam kalender.

## `Player` — `src/entities/player.py`

### `Player(...)`
Data utama pemain. Default diambil dari `config.py`.

Field:

- `money: int`: saldo sekarang.
- `day: int`: hari permainan.
- `daily_sales: int`: item terjual hari ini.
- `daily_sell_limit: int`: batas item yang boleh dijual per hari.
- `ingredient_stock: dict[str, int]`: jumlah bahan per ID.
- `food_inventory: list[Food]`: masakan yang belum dijual.
- `total_revenue: int`: akumulasi pendapatan.
- `total_expenses: int`: akumulasi pembelian bahan.
- `total_items_sold: int`: total item yang sudah terjual.

Property:

- `net_profit -> int`: revenue dikurangi expenses.

Methods:

- `add_ingredient(ingredient_id, quantity) -> None`: menambah stok; quantity harus positif.
- `remove_ingredient(ingredient_id, quantity) -> None`: mengurangi stok; melempar `ValueError` jika stok tidak cukup.
- `to_dict() -> dict`: mengubah player menjadi data JSON-compatible.
- `from_dict(data) -> Player`: membuat player dari dictionary save.

## `Ingredient` — `src/entities/ingredient.py`

`Ingredient.from_dict(data) -> Ingredient` memvalidasi field `id`, `name`, `category`, `market_price`. Harga tidak boleh negatif. Field opsional: `image`, `description`.

## `Food` — `src/entities/food.py`

Field: `instance_id`, `recipe_id`, `name`, `difficulty`, `quality`, `base_price`, `image`, `sold_price`. `to_dict()` dan `from_dict(data)` digunakan oleh save manager. `sold_price` disediakan untuk perluasan; item yang terjual pada build ini dihapus dari inventori.

## `RecipeSystem` — `src/systems/recipe_system.py`

- Constructor `RecipeSystem(recipes_dir, ingredient_ids)` membaca seluruh recipe JSON.
- `reload() -> None` membaca ulang file dan mengisi `recipes` serta `errors`.
- `get(recipe_id) -> dict | None` mencari satu resep.
- `all() -> list[dict]` mengembalikan semua resep valid.

Validator memastikan difficulty, jumlah step 1–5, ID bahan, quantity, timing, cooking time, dan base price valid. File yang salah dilewati dan ditulis ke `errors`; file resep lain tetap dapat dimuat.

## `MarketSystem` — `src/systems/market_system.py`

- `add_to_cart(ingredient_id, quantity) -> None`
- `change_cart_quantity(ingredient_id, delta) -> None`
- `clear_cart() -> None`
- `cart_total() -> int`
- `checkout(player) -> (success: bool, message: str, total: int)`

Lihat [Market System](04_MARKET_SYSTEM.md) untuk urutan transaksi dan efek ke Player.

## `InventorySystem` — `src/systems/inventory_system.py`

- `has_ingredients(recipe) -> (bool, list[str])`
- `consume_recipe_ingredients(recipe) -> None`
- `add_food(food) -> None`
- `find_food(instance_id) -> Food | None`

## `CookingSystem` — `src/systems/cooking_system.py`

- `reset() -> None`
- `start(recipe, now) -> None`
- `update(now) -> None`
- `expected_ingredient() -> dict | None`
- `seconds_until_target(now) -> float`
- `submit_action(now) -> Food | None`
- `countdown_number(now) -> int`

Lihat [Cooking System](03_COOKING_SYSTEM.md) untuk state machine, timing, dan kualitas.

## `EconomySystem` — `src/systems/economy_system.py`

- `selling_price(base_price, difficulty, quality) -> int`: rumus harga jual.
- `is_bankrupt(player) -> bool`: memeriksa kondisi bangkrut.

## `DaySystem` — `src/systems/day_system.py`

- `can_sell(player) -> bool`: memeriksa kuota.
- `register_sale(player) -> None`: menambah satu item ke hitungan hari ini; melempar `ValueError` jika kuota penuh.
- `end_day(player) -> None`: menambah hari dan mereset daily sales.

## `SaveManager` — `src/utils/save_manager.py`

- `SaveManager(save_path)` menentukan file save.
- `save(player) -> None`: menulis file sementara lalu mengganti file utama untuk mengurangi risiko file setengah tertulis.
- `load() -> Player | None`: memuat Player; mengembalikan `None` bila belum ada atau format tidak valid.

## `load_ingredients` — `src/utils/json_loader.py`

`load_ingredients(directory) -> dict[str, Ingredient]` membaca semua file JSON bahan. Kesalahan data dihimpun dan dilempar sebagai `ValueError` agar game tidak berjalan dengan ingredient data yang ambigu.

## `Game` — `src/core/game.py`

- `Game.__init__()`: inisialisasi Pygame, data, systems, save, dan layar awal.
- `Game.run() -> None`: main loop.
- `Game.handle_event(event) -> None`: dispatch event keyboard/mouse.
- `Game.handle_action(action) -> None`: dispatch ID tombol ke sistem.
- `Game.save_game() -> None`: simpan Player.
- `Game.start_selected_recipe() -> None`: validasi stok, konsumsi bahan, mulai sesi.
- `Game.sell_food(instance_id) -> None`: menjual item dan memperbarui statistik.

`Game` adalah UI/controller layer. Jangan memasukkan rumus harga atau validasi transaksi baru ke method drawing; implementasikan pada system yang sesuai.
