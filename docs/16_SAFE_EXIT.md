# 16 — Safe Exit & ESC Handling (v0.3.1c)

## Tujuan

Mencegah aplikasi tertutup tanpa sengaja dan memastikan progres disimpan sebelum aplikasi benar-benar keluar.

## Perilaku tombol

- **ESC di layar selain Cooking Station:** membuka konfirmasi keluar aplikasi.
- **ESC saat fullscreen:** tetap keluar dari fullscreen, mengikuti perilaku sebelumnya.
- **ESC di Cooking Station saat sesi idle/selesai:** kembali ke Buku Resep.
- **ESC atau tombol Batalkan saat timer memasak berjalan:** meminta konfirmasi pembatalan sesi.
- **Tombol X pada jendela:** membuka konfirmasi keluar, bukan langsung mematikan aplikasi.
- **ESC ketika dialog terbuka:** menutup dialog dan tetap berada di game.
- **Enter ketika dialog terbuka:** menjalankan tindakan utama pada dialog.

## Keamanan penyimpanan

Saat pemain memilih **Simpan & Keluar**, game menyimpan progres terlebih dahulu. Jika penyimpanan gagal, aplikasi tetap terbuka dan dialog menyediakan pilihan untuk mencoba lagi, kembali ke game, atau keluar tanpa menyimpan setelah menerima peringatan.

Jika hasil masakan sudah selesai tetapi transaksi belum berhasil disimpan, pilihan utama akan mencoba menyimpan hasil tersebut terlebih dahulu. Keluar tanpa menyimpan dapat membuang hasil masakan yang masih tertahan di sesi, tetapi stok bahan tetap aman karena transaksi v0.3.1b melakukan rollback ketika save gagal.

Sesi memasak yang belum selesai tidak dilanjutkan setelah aplikasi dibuka kembali. Sesuai DEC-007 dan v0.3.1b, stok bahan tetap tersimpan sehingga pemain dapat memulai resep dari awal.

## Implementasi

`ExitSystem` adalah state manager tanpa dependensi Pygame. Kelas ini mengatur routing ESC, status dialog, percobaan save terakhir, dan pilihan keluar tanpa save. `CookingSystem` menjeda deadline timer selama dialog konfirmasi terbuka dan menggeser deadline saat pemain memilih lanjut. `Game` menangani rendering dialog dan menghubungkan callback penyimpanan.

## Regression tests

Jalankan:

```bash
python -m unittest discover -s tests -p "test_safe_exit.py" -v
```

Tes mencakup routing ESC, keluar fullscreen, pembatalan sesi memasak, hasil masakan yang belum tersimpan, save sukses, save gagal, retry, exception penyimpanan, dan pilihan keluar tanpa save.
