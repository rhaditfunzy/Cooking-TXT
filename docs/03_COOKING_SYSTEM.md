# 03 — Cooking System

## File utama

- `src/systems/cooking_system.py`: state machine memasak, perhitungan timer, kualitas, dan hasil `Food`.
- `src/systems/inventory_system.py`: validasi kebutuhan bahan dan commit konsumsi bahan + hasil masakan.
- `src/core/game.py`: menghubungkan input UI, transaksi inventori, dan penyimpanan.

## State sesi

| State | Arti |
|---|---|
| `idle` | Belum ada sesi aktif |
| `countdown` | Menunggu countdown selesai |
| `ingredient_timing` | Menunggu pemain memasukkan bahan sesuai urutan resep |
| `final_cooking` | Semua bahan masuk; timer masak akhir berjalan |
| `finished` | Cooking System menghasilkan objek `Food`; Game mencoba commit ke inventori dan save |

## API CookingSystem

### `CookingSystem.start(recipe, now) -> None`
Memulai sesi dan mengatur countdown. Method ini hanya mengelola state/timer; tidak mengubah stok pemain.

### `CookingSystem.update(now) -> None`
Memindahkan state dari `countdown` ke `ingredient_timing` ketika countdown selesai.

### `CookingSystem.expected_ingredient() -> dict | None`
Mengembalikan step bahan yang sedang ditunggu.

### `CookingSystem.seconds_until_target(now) -> float`
Nilai positif berarti target masih di depan; nilai negatif berarti pemain terlambat.

### `CookingSystem.submit_action(now) -> Food | None`
Memajukan urutan aksi dan, pada aksi terakhir, menghasilkan objek `Food`. Method ini tidak mengurangi bahan atau menyimpan pemain.

### `CookingSystem.reset() -> None`
Mengembalikan state memasak ke `idle`. Saat sesi aktif dibatalkan, stok pemain tetap sama karena bahan belum dikonsumsi.

## Transaksi bahan — v0.3.1b

Bahan **tidak dikurangi ketika pemain menekan Mulai Memasak**. `Game.start_selected_recipe()` hanya memvalidasi stok dan memulai timer.

Ketika masakan selesai:

1. `CookingSystem.submit_action()` menghasilkan satu objek `Food`.
2. `InventorySystem.complete_recipe(recipe, food)` memvalidasi seluruh kebutuhan bahan.
3. Kebutuhan dengan ID bahan yang sama dijumlahkan terlebih dahulu.
4. Bahan dikonsumsi dan `Food` ditambahkan ke inventori sebagai satu transaksi di memori.
5. `Game.save_game()` menyimpan hasil transaksi melalui SaveManager yang sudah memakai temporary file + `os.replace()`.
6. Jika penyimpanan gagal, Game mengembalikan stok dan inventori di memori ke kondisi sebelum commit. Hasil masakan ditahan sebagai pending dan pemain mendapat tombol **Coba Simpan Lagi**.

Karena save terakhir sebelum penyelesaian masih berisi bahan yang belum dikonsumsi, crash atau penutupan paksa sebelum commit tidak menghilangkan bahan. Saat game dibuka lagi, sesi memasak yang belum selesai **dimulai ulang dari awal oleh pemain**; timer tidak dilanjutkan. Ini disengaja agar tidak ada sesi parsial yang dapat mengonsumsi atau menghasilkan makanan dua kali.

## Pembatalan

Selama state `countdown`, `ingredient_timing`, atau `final_cooking`, tombol **Batalkan** mereset sesi. Tidak diperlukan refund karena stok belum pernah dikurangi.

## Batas transaksi

- `InventorySystem.complete_recipe()` menjaga perubahan inventori tetap all-or-nothing di memori.
- Penyimpanan pemain dilakukan satu kali setelah bahan dikonsumsi dan makanan ditambahkan.
- Jika save gagal, perubahan inventori di memori di-rollback dan hasil masakan dapat dicoba disimpan ulang.
- Jika proses mati sebelum save atomik selesai, file save utama tetap berisi kondisi sebelum transaksi atau kondisi sesudah transaksi, bukan setengah transaksi.

## Ketepatan waktu

Deviasi setiap aksi adalah `abs(now - target_time)`. Kualitas masih memakai deviasi terburuk sesuai mekanik yang berjalan saat ini.

## Pengujian

```powershell
python -m unittest tests.test_transactional_cooking -v
python -m unittest discover -s tests -v
```
