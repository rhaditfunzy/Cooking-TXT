# 13 — Content Editor (Tanpa Menulis JSON)

Cooking TXT memiliki aplikasi desktop terpisah bernama **Content Editor**. Aplikasi ini menggunakan Tkinter (umumnya disertakan bersama Python di Windows), sehingga tidak membutuhkan package tambahan.

## Cara membuka

1. Pastikan Python 3 terpasang.
2. Buka folder utama `Cooking-TXT`.
3. Klik dua kali `open-content-editor.bat`, atau jalankan `python content_editor.py` dari terminal VS Code.
4. Pilih tab **Bahan Makanan** atau **Resep**.

File `content_editor.py` harus tetap berada di folder utama project, sejajar dengan `main.py`, agar folder `data/` dan `assets/` terdeteksi.

## Tab Bahan Makanan

- **Nama bahan:** nama yang ditampilkan di dalam game.
- **ID bahan:** ID unik. Jika dikosongkan, editor membuat ID dari nama (huruf kecil dan underscore). ID dapat diedit.
- **Kategori:** kategori teks bahan. Kategori umum adalah `meat`, `vegetable`, dan `other`.
- **Harga beli per unit:** harga bahan di Market. Nilai 0 diperbolehkan oleh model bahan saat ini.
- **Path gambar:** opsional. Tombol `Pilih & salin...` menyalin gambar ke `assets/images/ingredients/` dan mengisi path relatif secara otomatis.
- **Deskripsi:** keterangan opsional.

Pilih bahan di daftar untuk mengeditnya. Klik **Simpan Bahan** untuk membuat atau memperbarui file `data/ingredients/<id>.json`. Tombol **Hapus** menghapus file bahan. Sebelum menghapus bahan, periksa resep yang mungkin menggunakannya.

## Tab Resep

- **Nama masakan** dan **ID resep:** identitas resep.
- **Tingkat kesulitan:** harus `easy`, `normal`, atau `hard`.
- **Waktu mengambil makanan:** `cooking_time`, yaitu jeda setelah bahan terakhir dimasukkan hingga pemain mengambil hasil masakan.
- **Harga dasar jual:** `base_price`, sebelum pengali difficulty dan quality di `config.py`.
- **Gambar dan deskripsi:** opsional. Gambar disalin ke `assets/images/recipes/`.

### Menambahkan bahan ke resep

1. Pada bagian **Urutan bahan saat memasak**, klik pilihan **Bahan makanan** dan pilih bahan dari daftar.
2. Isi **Jumlah** untuk banyaknya unit bahan yang digunakan.
3. Isi **Timing (detik)** sebagai jeda dari aksi memasak sebelumnya. Timing step pertama dihitung dari awal sesi memasak. Nilai 0 dan desimal diperbolehkan.
4. Klik **＋ Tambah**. Bahan akan muncul di tabel urutan memasak.
5. Ulangi hingga maksimal 5 langkah bahan, lalu klik **Simpan resep**.

Untuk mengubah langkah, klik baris bahan di tabel. Nilai bahan, jumlah, dan timing akan dimuat kembali ke kolom input. Ubah nilainya lalu klik **Perbarui**. Gunakan **Hapus** untuk membuang baris terpilih, serta tombol **↑** dan **↓** untuk mengubah urutan. **Reset pilihan** mengosongkan kolom input.

Jika daftar bahan kosong, buat bahan terlebih dahulu melalui tab **Bahan Makanan**. Saat kembali ke tab Resep, daftar pilihan bahan akan diperbarui otomatis.

## Validasi dan penyimpanan

- File disimpan langsung ke `data/ingredients/` atau `data/recipes/` dengan format JSON yang dibaca game.
- Editor memeriksa ID duplikat, nilai numerik, tingkat kesulitan, jumlah bahan, dan ketersediaan ID bahan sebelum menyimpan resep.
- Penyimpanan menggunakan file sementara sebelum menggantikan file tujuan untuk mengurangi risiko file setengah tertulis.
- Jika ID item yang diedit berubah, editor menyimpan file dengan ID baru lalu menghapus file lama.
- Menghapus bahan dapat membuat resep lama tidak valid. Editor memberikan peringatan, tetapi tidak mengubah resep secara otomatis.
- Tutup lalu jalankan ulang game agar perubahan data dimuat kembali.
- Untuk mengirim perubahan ke GitHub, gunakan script project seperti `update-cooking-txt.bat "Add new recipe"` jika file tersebut tersedia di root project.

## Batasan versi awal

Editor ini mengelola data bahan dan resep. Editor tidak mengubah kode gameplay, formula harga di `config.py`, atau data save pemain. Gambar yang dipilih disalin ke folder aset; gambar bersifat opsional.

## Catatan UI versi 0.1.2–0.1.3

- Header aplikasi menggunakan panel navy dengan judul dan label Content Studio.
- Area kerja menggunakan tab yang lebih jelas, latar abu-abu lembut, dan panel form putih.
- Tab Bahan Makanan tetap menggunakan alur form yang sama.
- Tab Resep memakai panel daftar tetap di kiri (grid layout), bukan sash `Panedwindow`, sehingga panel tidak bisa terlipat menjadi sangat sempit.
- Builder bahan resep sekarang berada langsung di halaman: pilih bahan, jumlah, timing, lalu klik **＋ Tambah**. Tidak perlu membuka dialog pop-up.
- Tombol perbarui, hapus, pindah urutan, dan jumlah langkah ditempatkan dekat tabel bahan.
- Tombol Simpan resep dan Bersihkan form dipasang di bagian bawah panel agar tidak ikut terdorong keluar oleh tabel.
- Ukuran awal jendela 1180 × 800 dan ukuran minimum 1180 × 720 supaya seluruh kontrol builder tetap terlihat.
