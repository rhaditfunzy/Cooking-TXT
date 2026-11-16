# v0.3.1b — Transactional Cooking & Ingredient Protection

## Ringkasan

Mulai memasak tidak lagi mengurangi stok bahan. Bahan baru dikonsumsi saat hasil masakan selesai dan transaksi inventori berhasil disimpan.

## Perilaku

- Start: validasi stok dan mulai state machine; stok tetap utuh.
- Cancel: reset sesi; stok tetap utuh.
- Crash/force close sebelum selesai: save terakhir masih memiliki stok bahan. Sesi timer tidak dilanjutkan; pemain dapat memulai resep lagi.
- Complete: validasi semua bahan, konsumsi bahan, tambahkan satu `Food`, lalu simpan satu kali.
- Save gagal: perubahan inventori dalam memori di-rollback, hasil masakan ditahan sebagai pending, dan UI menawarkan `Coba Simpan Lagi`.

## Konsistensi dan duplikasi

`InventorySystem.ingredient_requirements()` menggabungkan step yang memakai ID bahan sama. `complete_recipe()` memvalidasi seluruh kebutuhan sebelum mutasi dan menolak `Food.instance_id` yang sudah ada. Perubahan stok dan daftar makanan di-rollback jika operasi inventori gagal.

SaveManager v0.3.1a tetap menjadi lapisan persistensi: temporary file ditulis lebih dulu, save valid lama dicadangkan, lalu `os.replace()` mengganti save utama secara atomik. Dengan urutan tersebut, crash ketika cooking belum selesai meninggalkan save lama dengan bahan utuh; crash ketika commit selesai meninggalkan save baru dengan bahan berkurang dan makanan tercatat.

## Batasan

Patch ini tidak menyimpan timer atau posisi step memasak untuk dilanjutkan setelah restart. Sesi yang belum selesai dibatalkan saat proses mati, tetapi bahan tidak hilang. Resume sesi memasak lintas restart dapat dibuat sebagai fitur terpisah jika nanti dibutuhkan.

## Verifikasi

Jalankan:

```powershell
python -m unittest tests.test_transactional_cooking -v
python -m unittest discover -s tests -v
```
