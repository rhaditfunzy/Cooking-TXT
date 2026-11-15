# 09 — UI/UX Guide

## Tampilan

Build pertama menggunakan layout desktop 1280×800 dengan panel gelap, aksen oranye, dan tombol berbasis mouse. Tidak ada artwork eksternal yang wajib dipasang.

## Navigasi

Navigation bar atas memiliki layar:

- **Home:** dashboard dan ringkasan hari.
- **Market:** katalog bahan, quantity selector, cart, dan checkout.
- **Recipes:** daftar resep dan ketersediaan bahan.
- **Inventory:** stok bahan dan daftar hasil masakan.
- **Profile:** statistik ekonomi dan aturan bisnis.

Cooking Station dibuka dari tombol Cook pada Recipe Book.

## Kontrol

- Mouse kiri: memilih tombol.
- `Esc`: kembali dari Cooking Station hanya bila sesi tidak sedang berjalan; dari layar lain keluar dari aplikasi.
- Mouse wheel di Inventory: scroll daftar makanan atau bahan (tergantung sisi panel).
- Mouse wheel di Market: scroll katalog atau keranjang.
- Mouse wheel di Recipe Book: scroll daftar resep.
- Tombol panah di panel membantu berpindah halaman jika konten JSON lebih banyak dari ruang tampilan.
- Tombol **Akhiri Hari** di Dashboard/Profile: pindah hari dan reset kuota.

## Feedback

Pesan status di bagian bawah layar menampilkan hasil transaksi, kesalahan, atau status memasak. Harga ditampilkan dalam format rupiah. Timer menggunakan presisi dua angka desimal.

## Arah pengembangan UI

Folder `assets/images/ingredients`, `assets/images/recipes`, `assets/images/ui`, `assets/images/backgrounds`, `assets/fonts`, dan `assets/sounds` sudah disiapkan. Market dan Recipe Book menampilkan gambar dari path JSON jika file tersedia, lalu menampilkan placeholder jika belum ada. Integrasi aset lain sebaiknya tetap opsional sehingga game tidak gagal berjalan ketika file belum ditambahkan.
