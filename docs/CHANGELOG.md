# Changelog

## 0.1.0 — Initial playable build

- Membuat struktur modular Pygame.
- Menambahkan 11 data bahan dan 5 resep JSON.
- Menambahkan Market, Recipe Book, Cooking Station, Inventory, Dashboard, dan Profile.
- Menambahkan countdown, timer bahan, timer matang, dan kualitas Poor/Mid/Good.
- Menambahkan transaksi keranjang atomik, penjualan lima item per hari, dan pergantian hari manual.
- Menambahkan save/load pemain, dokumentasi teknis, API reference, decision log, dan unit test.

## 0.2.0 — Cozy Rustic UI Refresh
- Mengganti palet gelap-oranye menjadi palet Cozy Rustic sesuai style guide.
- Mengganti header horizontal menjadi sidebar navigasi dan top bar.
- Memperbarui layout Beranda, Market, Buku Resep, Cooking Station, Inventori, dan Profil Bisnis.
- Menambahkan pemuatan font lokal Fraunces dan Nunito Sans dengan fallback aman.
- Mempertahankan ID aksi dan pemanggilan sistem gameplay.


## 0.3.1b — Transactional Cooking & Ingredient Protection

- Bahan tidak lagi dikurangi saat memasak dimulai; bahan dikonsumsi saat hasil selesai dan berhasil disimpan.
- Menambahkan pembatalan sesi memasak tanpa refund manual karena stok belum pernah dikurangi.
- Menambahkan rollback inventori jika penyimpanan hasil masakan gagal dan tombol Coba Simpan Lagi.
- Menggabungkan kebutuhan bahan dengan ID berulang dan mencegah duplikasi `Food.instance_id`.
- Menambahkan regression tests untuk crash sebelum selesai, cancel, completion, save/reload, rollback, dan kebutuhan bahan berulang.


## 0.3.1c — Safe Exit & ESC Handling

- Tombol X dan ESC di luar Cooking Station membuka konfirmasi keluar, bukan menutup aplikasi langsung.
- ESC saat memasak dan tombol Batalkan meminta konfirmasi; timer dijeda selama dialog, dan stok bahan tetap aman.
- Progres disimpan sebelum keluar; kegagalan save membuat game tetap terbuka dengan opsi retry.
- Hasil masakan yang belum tersimpan ditangani secara eksplisit sebelum keluar.
- Menambahkan `ExitSystem` dan regression tests untuk routing ESC serta skenario save.
