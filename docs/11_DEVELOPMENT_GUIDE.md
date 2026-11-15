# 11 — Development Guide

## Setup

1. Instal Python 3.10 atau lebih baru.
2. Buka terminal di root `Cooking-TXT`.
3. Instal dependensi: `python -m pip install -r requirements.txt`.
4. Jalankan `python main.py`.

Di Windows, `run_game.bat` melakukan instalasi dependency lalu menjalankan game. Di Linux/macOS gunakan `./run_game.sh`.

## Menjalankan tes

```bash
python -m unittest discover -s tests -v
```

Unit test tidak membuka jendela Pygame; test fokus pada data dan aturan logic.

## Alur menambah fitur

1. Tentukan sistem yang bertanggung jawab.
2. Implementasikan aturan di `src/systems/` atau model di `src/entities/`.
3. Hubungkan kontrol/tampilan melalui `src/core/game.py`.
4. Tambahkan atau revisi unit test di `tests/`.
5. Perbarui dokumen API, mekanik, JSON, atau keputusan sesuai dampaknya.
6. Jalankan seluruh tes.
7. Jalankan game dan uji alur manual: Market → Cooking → Inventory → Sell → End Day.

## Menambah konten

Untuk bahan/resep baru, ikuti [JSON Data Guide](08_JSON_DATA_GUIDE.md). Tidak perlu membuat perubahan Python selama field JSON tetap sesuai schema.

## Troubleshooting

- **`ModuleNotFoundError: pygame`:** jalankan `python -m pip install -r requirements.txt`.
- **Game tidak terbuka:** pastikan Python dan Pygame menggunakan environment/interpreter yang sama.
- **Bahan tidak ditemukan:** pastikan `id` resep cocok dengan `id` JSON bahan.
- **Resep tidak muncul:** periksa `difficulty`, jumlah bahan (1–5), `quantity`, `timing`, `cooking_time`, `base_price`, dan JSON syntax. File invalid dilewati dan dicatat pada `RecipeSystem.errors`.
- **Save tampak kembali baru:** periksa `saves/player_save.json`; file yang invalid membuat game memulai Player baru.
- **Tidak bisa menjual:** pastikan ada Food di Inventory dan kuota harian belum habis.

## Standar kontribusi

- Gunakan nama modul dan fungsi bahasa Inggris yang konsisten.
- Tulis dokumentasi teknis dalam bahasa Indonesia.
- Jaga system logic tetap terpisah dari rendering.
- Tambahkan test untuk bug yang diperbaiki bila memungkinkan.
- Jangan menandai fitur di dokumentasi sebagai selesai bila belum ada di kode.
