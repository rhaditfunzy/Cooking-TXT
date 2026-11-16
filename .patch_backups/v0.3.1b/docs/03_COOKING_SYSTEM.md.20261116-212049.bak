# 03 — Cooking System

## File utama

- `src/systems/cooking_system.py`: state machine memasak, perhitungan timer, kualitas, dan hasil Food.
- `src/core/game.py`: memanggil update timer dan menghubungkan input tombol UI.
- `src/systems/inventory_system.py`: memvalidasi dan mengurangi bahan sebelum sesi dimulai.

## State sesi

| State | Arti |
|---|---|
| `idle` | Belum ada sesi aktif |
| `countdown` | Menunggu countdown 3 detik selesai |
| `ingredient_timing` | Menunggu pemain memasukkan bahan pada urutan resep |
| `final_cooking` | Semua bahan masuk; timer masak akhir berjalan |
| `finished` | Makanan dibuat dan tersedia untuk dimasukkan ke inventori |

## API

### `CookingSystem.start(recipe, now) -> None`
Memulai sesi. `recipe` adalah dictionary resep hasil load/validasi dan `now` adalah waktu monoton dalam detik. Method mengatur countdown dan membersihkan hasil sesi sebelumnya. Akan melempar `RuntimeError` jika sesi lain masih berjalan.

### `CookingSystem.update(now) -> None`
Memindahkan state dari `countdown` ke `ingredient_timing` ketika countdown berakhir. Method ini tidak memasukkan bahan otomatis.

### `CookingSystem.expected_ingredient() -> dict | None`
Mengembalikan step bahan saat ini jika sesi sedang menunggu input bahan.

### `CookingSystem.seconds_until_target(now) -> float`
Nilai positif berarti target masih di depan; nilai negatif berarti pemain sudah melewati target.

### `CookingSystem.submit_action(now) -> Food | None`
Saat `ingredient_timing`, mencatat deviasi waktu dan maju ke bahan berikutnya. Setelah bahan terakhir, berpindah ke `final_cooking`. Saat `final_cooking`, membuat `Food`, mengubah state menjadi `finished`, dan mengembalikan objek tersebut. Selain kondisi itu, mengembalikan `None`.

### `CookingSystem.reset() -> None`
Mengembalikan state ke `idle` dan menghapus sesi sebelumnya.

## Ketepatan waktu

Deviasi adalah `abs(now - target_time)`. Deviasi dikumpulkan untuk setiap bahan dan aksi mengambil makanan. Kualitas akhir ditentukan oleh nilai maksimum deviasi, bukan rata-rata. Dengan demikian satu kesalahan timing besar dapat menurunkan kualitas seluruh masakan.

## Konsumsi bahan

`Game.start_selected_recipe()` memeriksa stok melalui `InventorySystem.has_ingredients()`. Jika cukup, `consume_recipe_ingredients()` mengurangi bahan, lalu `CookingSystem.start()` memulai sesi. Bahan dikonsumsi saat mulai memasak, bukan saat setiap tombol bahan ditekan.

## Kontrol pemain

Tombol utama di Cooking Station berubah sesuai state:

- `START COOKING` ketika idle.
- `MASUKKAN BAHAN` selama ingredient timing.
- `AMBIL MAKANAN` selama final cooking.
- `Buka Inventory` setelah sesi finished.

Pemain boleh menekan tombol lebih awal atau terlambat. Aksi tetap diterima dan deviasi waktu menurunkan kualitas; tidak ada tombol yang dikunci hanya karena timer belum mencapai nol.
