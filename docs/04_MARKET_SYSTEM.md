# 04 — Market System

## File

`src/systems/market_system.py` mengelola keranjang dan checkout. UI Market berada di `Game.draw_market()` dan event action `market_*` di `Game.handle_action()`.

## Perilaku

1. Pemain mengatur quantity bahan di layar Market.
2. `add_to_cart(ingredient_id, quantity)` menambahkan kuantitas ke keranjang.
3. Keranjang dapat berisi banyak ingredient ID.
4. `cart_total()` menghitung jumlah `market_price × quantity`.
5. `checkout(player)` memeriksa saldo.
6. Jika saldo cukup, semua bahan ditambahkan, saldo dikurangi, biaya bertambah, dan keranjang dibersihkan.
7. Jika saldo tidak cukup, stok, saldo, biaya, dan keranjang tidak berubah.

## API

- `MarketSystem(ingredients)`: menerima dictionary `{ingredient_id: Ingredient}`.
- `add_to_cart(ingredient_id, quantity) -> None`: menambah item; validasi ID dan quantity positif.
- `change_cart_quantity(ingredient_id, delta) -> None`: mengubah kuantitas keranjang; jika hasilnya nol atau kurang, item dihapus.
- `clear_cart() -> None`: mengosongkan keranjang.
- `cart_total() -> int`: mengembalikan total harga keranjang.
- `checkout(player) -> tuple[bool, str, int]`: mengembalikan status, pesan, dan total transaksi.

## Catatan desain

Checkout sengaja dibuat atomik dari sudut pandang gameplay: pemeriksaan uang dilakukan sebelum perubahan stok dan saldo. Keranjang tidak disimpan saat aplikasi ditutup; keranjang hanyalah draft transaksi, bukan progres pemain.
