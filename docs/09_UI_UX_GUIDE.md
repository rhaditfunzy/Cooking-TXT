# 09 — UI/UX Guide (Cozy Rustic Update)

## Arah visual

Cooking TXT menggunakan gaya **Cozy Rustic Restaurant Management** dalam 2D Pygame. UI dibangun dengan `pygame.draw`, font TTF lokal, dan PNG transparan opsional. Tidak ada kebutuhan untuk aset 3D, glassmorphism, blur, atau shadow berat.

## Token warna

| Token | HEX | Peran |
|---|---|---|
| Blue | `#3874AA` | Aksen informasi dan tautan sekunder |
| Terracotta | `#BC6040` | Aksi utama dan status penting |
| Mustard | `#DD984D` | Penanda, aksen hangat, harga |
| Roasted Brown | `#573B30` | Teks utama |
| Sage | `#8DA28F` | Status positif dan progres |
| Muted Teal | `#527978` | Navigasi dan elemen sekunder |
| Parchment | `#F3EBDC` | Latar utama turunan |
| Warm Paper | `#FFF9EE` | Panel dan kartu turunan |

## Tipografi

- **Fraunces SemiBold** untuk judul halaman dan heading display.
- **Nunito Sans Regular** untuk teks UI.
- **Nunito Sans Bold** untuk tombol dan informasi penting.

Letakkan file font di `assets/fonts/` dengan nama persis:

- `Fraunces-SemiBold.ttf`
- `NunitoSans-Regular.ttf`
- `NunitoSans-Bold.ttf`

Font tidak disertakan di repository; unduh dari sumber resmi Google Fonts dan periksa lisensi distribusinya sebelum memasukkan font ke repo. Jika file font belum ada, game tetap jalan memakai fallback Pygame bawaan dan menampilkan peringatan di terminal.

## Komponen dan spacing

- Sidebar tetap: 212 px.
- Top bar: 88 px.
- Konten utama dimulai pada x=242 px.
- Jarak antar panel sekitar 16–20 px.
- Panel menggunakan radius kecil, garis tepi tipis, dan garis mustard sebagai aksen kertas.
- Tombol aksi utama berwarna terracotta; tombol navigasi/sekunder menggunakan teal atau blue.
- Ikon dekoratif dibuat dari bentuk Pygame sederhana; sprite makanan tetap berasal dari PNG JSON masing-masing.

## Layar

- **Beranda:** ringkasan kas, keuntungan, penjualan, stok masakan, dan langkah operasional.
- **Market:** katalog bahan di kiri dan keranjang di kanan.
- **Buku Resep:** kartu resep dua kolom dengan gambar, kesulitan, timing, dan tombol masak.
- **Cooking Station:** urutan bahan di panel kiri dan timer/aksi di panel kanan.
- **Inventori:** makanan jadi di kiri dan stok bahan mentah di kanan.
- **Profil Bisnis:** statistik keuangan dan aturan operasional.

## Prinsip kompatibilitas

Perubahan ini hanya mengganti lapisan rendering dan posisi kontrol. ID aksi tombol, sistem market, resep, inventory, cooking, ekonomi, dan penyimpanan tetap menggunakan API sistem yang sudah ada. Ukuran target UI adalah 1280×800; bila resolusi diubah, posisi layout perlu diuji ulang.
