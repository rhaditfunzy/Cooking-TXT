# Cooking TXT

Game simulasi bisnis restoran berbasis desktop menggunakan **Python 3.10+ dan Pygame 2**. Beli bahan dari Market, masak resep dengan mekanik ketepatan waktu, lalu jual hasilnya untuk mengembangkan bisnis restoran.

## Fitur

- Market dengan keranjang belanja dan validasi saldo.
- Resep dan bahan yang dimuat dari file JSON.
- Cooking Station dengan timer dan penilaian kualitas.
- Inventory, penjualan harian, dan ringkasan finansial.
- Auto-save progres pemain secara lokal.

## Mulai

**Persyaratan:** Python 3.10 atau lebih baru.

1. Unduh atau clone repository, lalu buka folder project di terminal.
2. Pasang dependency dan jalankan game:

```bash
python -m pip install -r requirements.txt
python main.py
```

Di Windows, Anda juga dapat menjalankan `run_game.bat`. Di Linux/macOS:

```bash
chmod +x run_game.sh
./run_game.sh
```

## Cara bermain

1. Buka **Market**, tentukan jumlah bahan, klik **Tambah**, kemudian **Buy**.
2. Buka **Recipes**, pilih resep yang bahannya tersedia.
3. Klik **Start Cooking**. Setelah countdown 3-2-1, tekan tombol aksi untuk memasukkan setiap bahan sesuai timer, lalu ambil makanan setelah waktu memasak akhir.
4. Buka **Inventory** dan klik **Sell**. Maksimal lima item dapat dijual per hari.
5. Klik **Akhiri Hari** dari Dashboard atau Profile untuk mengatur ulang kuota penjualan.

## Struktur project

```text
assets/       Aset gambar, font, dan suara
data/         Data bahan dan resep dalam JSON
docs/         Dokumentasi desain dan pengembangan
saves/        Penyimpanan progres lokal (tidak masuk Git)
src/          Kode game
tests/        Unit test
main.py       Entry point
config.py     Konfigurasi game
```

## Kustomisasi

- Bahan: satu file JSON per bahan di `data/ingredients/`.
- Resep: satu file JSON per resep di `data/recipes/`.
- Gambar: letakkan ikon bahan di `assets/images/ingredients/` dan gambar resep di `assets/images/recipes/`. File gambar bersifat opsional pada versi awal.
- Aturan global: ubah nilai di `config.py`.

Dokumentasi arsitektur, mekanik, format JSON, dan panduan pengembangan tersedia di [`docs/`](docs/README.md).

## Penyimpanan

Progres disimpan lokal di `saves/player_save.json`; file save dikecualikan dari Git agar data pribadi pemain tidak ikut terunggah. Keranjang Market dan sesi memasak yang sedang berlangsung tidak dapat dilanjutkan setelah aplikasi ditutup.

## Save dan tes

Jalankan tes logika tanpa membuka jendela game:

```bash
python -m unittest discover -s tests -v
```

## Lisensi

Repository ini belum menyertakan lisensi. Tentukan dan tambahkan file lisensi sebelum mengizinkan penggunaan atau distribusi ulang oleh pihak lain.
