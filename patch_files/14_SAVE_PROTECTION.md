# v0.3.1a — Backup Corrupted Save & Save Protection

## Tujuan

Melindungi progres pemain ketika file save rusak, tidak dapat dibaca, atau penyimpanan gagal. Patch ini mempertahankan format save versi 1 agar kompatibel dengan save Cooking TXT yang sudah ada.

## Perilaku load

`SaveManager.load()` mengisi `last_load_status` dengan salah satu nilai berikut:

- `loaded`: save berhasil dibaca.
- `missing`: belum ada save; game boleh membuat pemain baru.
- `corrupt_backed_up`: save tidak valid dan berhasil dipindahkan ke file karantina.
- `corrupt_backup_failed`: save tidak valid tetapi gagal dipindahkan; penulisan otomatis diblokir.
- `read_error`: file ada tetapi tidak dapat dibaca; penulisan otomatis diblokir.

File rusak tidak dihapus. File dipindahkan dengan nama seperti:

`player_save.corrupt-20261116-203000-123456.json`

Jika proses pemindahan gagal, file asli dibiarkan di tempatnya dan `write_protected=True`. Game tetap dapat membuka sesi sementara, tetapi tidak boleh menulis pemain baru ke lokasi save lama.

## Perilaku save

1. Data pemain diserialisasi sebelum save lama disentuh.
2. Data baru ditulis ke file sementara dalam folder yang sama.
3. Jika save utama sebelumnya ada, isinya divalidasi terlebih dahulu.
4. Save lama yang valid disalin secara atomik ke `player_save.json.bak`.
5. File sementara menggantikan save utama menggunakan `os.replace()`.
6. Jika backup atau penulisan gagal, save utama sebelumnya tidak diganti.

`SaveManager.save()` melempar `SaveError` ketika gagal. `Game.save_game()` menangkap error ini, menampilkan peringatan, mencatat detail ke terminal, dan mengembalikan `False`.

## Pemulihan manual

- File `*.corrupt-*.json`: salinan save yang gagal dibaca; jangan dihapus sebelum diperiksa.
- File `player_save.json.bak`: save valid satu langkah sebelum save utama terakhir ditulis.
- Untuk pemulihan manual, tutup game terlebih dahulu, lalu salin backup yang ingin dipulihkan menjadi `player_save.json` setelah menyimpan salinan file saat ini.

Patch ini belum otomatis memulihkan `.bak`, agar game tidak memilih progres lama secara diam-diam. Pemulihan otomatis/antarmuka pemulihan dapat menjadi pekerjaan terpisah.

## Pengujian

Jalankan:

```powershell
python -m unittest tests.test_save_protection -v
python -m unittest discover -s tests -v
```

Tes tambahan mencakup save hilang, save JSON rusak, payload pemain salah, versi save tidak didukung, kegagalan karantina, backup save valid, kegagalan backup, dan save rusak yang ditemukan saat operasi save.

## Batasan milestone

Patch ini berfokus pada proteksi file save. Pemulihan bahan ketika proses memasak dibatalkan/crash merupakan v0.3.1b dan belum termasuk di sini.
