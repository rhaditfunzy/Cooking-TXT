# 00 — Project Overview

## Identitas

- **Nama:** Cooking TXT
- **Platform:** Desktop
- **Teknologi:** Python 3.10+ dan Pygame 2.x
- **Genre:** Cooking / business simulation
- **Tujuan bisnis:** memperoleh keuntungan sebanyak mungkin dari penjualan makanan
- **Kondisi kalah:** toko bangkrut

## Gameplay loop

`Market → Recipe Book → Cooking Station → Inventory → Sell → Profit → ulangi`

Pemain membeli bahan dengan uang yang tersedia. Setiap resep memiliki urutan bahan dan waktu pemicu. Ketika seluruh tahapan selesai, hasil masakan disimpan ke inventori dengan kualitas Poor, Mid, atau Good. Harga jual ditentukan oleh harga dasar resep, kesulitan, dan kualitas. Batas penjualan adalah lima makanan per hari.

## Fitur dalam build ini

1. Dashboard saldo, keuntungan bersih, total penjualan, dan stok makanan.
2. Market dengan jumlah pembelian, keranjang multi-bahan, checkout, dan validasi saldo.
3. Recipe Book yang memuat resep dari file JSON.
4. Cooking Station dengan countdown, timer berurutan, input aksi, dan penilaian kualitas.
5. Inventory bahan dan hasil masakan, termasuk penjualan per item.
6. Batas penjualan harian dan tombol pergantian hari manual.
7. Profile dan ringkasan finansial.
8. Auto-save progres pemain.
9. Unit test untuk logika data, market, cooking, sales limit, dan harga.

## Konten awal

Ada 11 bahan dan 5 resep sesuai konsep awal: Egg Fried Rice, Lemon Chicken, Shrimp Salad, Beef Fried Rice, dan Salmon Pie. Ejaan `lettuce` digunakan secara konsisten pada ID dan nama bahan, meskipun dokumen konsep menuliskan `Letucce`.

## Batasan versi awal

- Tidak ada pelanggan/NPC, antrean pelanggan, atau permintaan pesanan. Pemain menjual langsung dari Inventory.
- Tidak ada sistem level, upgrade peralatan, atau reputasi.
- Hari tidak berjalan otomatis; pemain menekan **Akhiri Hari**.
- Tidak ada gambar bawaan. Folder dan referensi file gambar sudah disiapkan, tetapi tampilan awal tetap dapat berjalan tanpa gambar.
- Tidak ada target kemenangan numerik. Permainan berjalan sebagai sandbox untuk memaksimalkan keuntungan; kondisi bangkrut ditentukan oleh aturan yang dijelaskan di Game Mechanics.
