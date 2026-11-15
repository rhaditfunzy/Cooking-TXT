# 05 — Inventory & Selling

## Model data

`Player.ingredient_stock` menyimpan jumlah bahan dalam dictionary berdasarkan ingredient ID. `Player.food_inventory` menyimpan daftar objek `Food`. Setiap Food memiliki `instance_id` unik sehingga dua masakan dari resep sama bisa dijual secara terpisah.

## InventorySystem API

- `has_ingredients(recipe) -> tuple[bool, list[str]]`: memeriksa jumlah seluruh bahan yang diperlukan.
- `consume_recipe_ingredients(recipe) -> None`: validasi semua bahan dahulu, lalu mengurangi stok. Jika ada bahan kurang, method melempar `ValueError` tanpa mengurangi sebagian stok.
- `add_food(food) -> None`: menambahkan hasil masakan ke inventori.
- `find_food(instance_id) -> Food | None`: mencari satu hasil masakan.

## Penjualan

`Game.sell_food(instance_id)` melakukan langkah berikut:

1. Cari Food.
2. Pastikan kuota penjualan harian masih tersedia.
3. Hitung harga lewat `EconomySystem.selling_price()`.
4. Naikkan hitungan kuota melalui `DaySystem.register_sale()`.
5. Hapus Food dari inventori.
6. Tambahkan uang pemain dan total revenue.
7. Simpan progres.

Setiap Food yang dijual dihitung sebagai satu penjualan. Maksimal lima item per hari, tidak peduli apakah resepnya sama atau berbeda. Jika kuota habis, tombol Sell dinonaktifkan dan transaksi ditolak oleh logic.

## Bahan tersisa

Bahan yang tidak terpakai tetap berada di inventory pemain dan dapat digunakan untuk memasak pada hari berikutnya. Tidak ada spoilage atau batas kapasitas pada versi ini.
