# 01 — Architecture

## Struktur

```text
Cooking-TXT/
├── main.py                  # entry point
├── config.py                # nilai konfigurasi dan warna
├── data/
│   ├── ingredients/         # satu JSON per bahan
│   └── recipes/             # satu JSON per resep
├── assets/
│   ├── images/ingredients/  # ikon bahan (opsional)
│   ├── images/recipes/      # gambar masakan (opsional)
│   ├── images/ui/           # aset UI
│   ├── images/backgrounds/  # latar
│   ├── fonts/               # font tambahan
│   └── sounds/              # efek audio
├── saves/                   # save pemain
├── docs/                    # dokumentasi
├── tests/                   # unit tests
└── src/
    ├── core/                # loop game dan state layar
    ├── entities/            # model Player, Ingredient, Food
    ├── systems/             # aturan gameplay
    ├── ui/                  # reserved untuk pemisahan UI lanjutan
    └── utils/               # JSON, save, asset loader
```

## Peran lapisan

- **Core:** `Game` menginisialisasi Pygame, membuat objek sistem, menjalankan event loop, memanggil update, dan menggambar layar.
- **Entities:** menyimpan data objek tanpa mengatur tampilan.
- **Systems:** menjalankan aturan bisnis dan game. Modul ini sebisa mungkin tidak bergantung pada Pygame.
- **Utils:** menangani pekerjaan lintas sistem seperti membaca JSON dan menyimpan progres.
- **Data:** konten dapat ditambah tanpa menulis ulang logic Python.
- **Assets:** media opsional; path disimpan sebagai string relatif di JSON.

## Alur inisialisasi

1. `main.py` memanggil `src.core.game.main()`.
2. `Game.__init__()` menginisialisasi Pygame dan window.
3. `load_ingredients()` membaca semua `data/ingredients/*.json`.
4. `RecipeSystem` membaca dan memvalidasi semua JSON resep menggunakan ID bahan yang tersedia.
5. `SaveManager.load()` mencoba membaca pemain; jika belum ada atau save tidak valid, pemain baru dibuat dengan modal awal.
6. `MarketSystem`, `InventorySystem`, `CookingSystem`, dan `AssetLoader` disiapkan.
7. `Game.run()` menjalankan loop event → update timer → draw.

## Dependency utama

```text
Game
 ├── Ingredient loader ──> Ingredient data
 ├── RecipeSystem ───────> Ingredient IDs + Recipe JSON
 ├── MarketSystem ───────> Ingredient data + Player
 ├── InventorySystem ────> Player + Food
 ├── CookingSystem ──────> Recipe dict + Food
 ├── EconomySystem ──────> config multipliers
 ├── DaySystem ──────────> Player
 └── SaveManager ────────> Player JSON
```

`Game` adalah orchestration layer. Aturan market, cooking, dan ekonomi tidak seharusnya dipindahkan ke event handler UI kecuali sebagai validasi tampilan.

## Prinsip perubahan

- Hindari menaruh seluruh logic ke `main.py`.
- Jangan membuat duplikasi data resep di kode Python.
- Sistem gameplay menerima data dari entity atau dictionary tervalidasi.
- UI memanggil method sistem, bukan mengubah saldo/stok tanpa melalui sistem.
- Ketika menambahkan field JSON, update validator, guide, contoh, dan tests.
