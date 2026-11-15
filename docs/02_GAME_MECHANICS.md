# 02 — Game Mechanics

## Aturan yang berasal dari dokumen konsep

- Pemain membeli semua bahan melalui Market.
- Satu resep menggabungkan satu sampai lima jenis bahan.
- Memasak dimulai dengan countdown 3–2–1.
- Setelah countdown, timer memberi tahu kapan bahan berikutnya harus dimasukkan.
- Terlalu cepat atau terlambat memengaruhi kualitas hasil masakan.
- Kualitas yang tersedia: Poor, Mid, Good.
- Hasil masakan masuk ke Inventory, kemudian dapat dijual kapan saja.
- Maksimal lima makanan dijual setiap hari.
- Market mendukung beberapa jenis bahan dalam satu keranjang.
- Transaksi gagal jika saldo tidak cukup.

## Asumsi implementasi versi awal

| Aturan | Nilai awal | Lokasi ubah |
|---|---|---|
| Modal pemain baru | Rp250 | `config.py: STARTING_MONEY` |
| Batas penjualan | 5 item/hari | `config.py: DAILY_SELL_LIMIT` |
| Jumlah tiap bahan per resep | 1 kecuali JSON menyatakan lain | field `quantity` di JSON resep |
| Waktu awal countdown | 3 detik | `config.py: COUNTDOWN_SECONDS` |
| Toleransi Good | maksimal 0,25 detik | `config.py: GOOD_TIMING_TOLERANCE` |
| Toleransi Mid | maksimal 1,00 detik | `config.py: MID_TIMING_TOLERANCE` |
| Hari baru | manual lewat tombol Akhiri Hari | `DaySystem.end_day()` |
| Bangkrut | saldo ≤ 0 dan tidak ada stok bahan atau makanan | `EconomySystem.is_bankrupt()` |

Harga market dan harga dasar resep juga merupakan nilai awal buatan untuk menyeimbangkan prototipe, bukan angka dari dokumen konsep. Angkanya berada pada file JSON masing-masing.

## Urutan memasak

Timer tiap bahan adalah interval dari aksi sebelumnya. Timer bahan pertama dimulai setelah countdown selesai. Setelah bahan terakhir diterima, `cooking_time` menjadi interval untuk aksi mengambil makanan.

Contoh Egg Fried Rice:

1. Countdown 3 detik.
2. Timer 2 detik: masukkan Rice.
3. Timer 10 detik sejak aksi Rice: masukkan Egg.
4. Timer 20 detik sejak aksi Egg: ambil makanan.

Jadwal berikutnya dimulai dari waktu aksi aktual pemain, bukan dari target lama. Ini menghindari satu keterlambatan kecil membuat semua tahap berikutnya langsung terlewat.

## Kualitas

Setiap aksi dibandingkan dengan target timer. Kualitas akhir menggunakan selisih terburuk dari seluruh aksi:

- Good: semua aksi berjarak maksimal 0,25 detik dari target.
- Mid: selisih terburuk lebih dari 0,25 detik dan maksimal 1,00 detik.
- Poor: ada aksi dengan selisih lebih dari 1,00 detik.

Ini sengaja ketat agar ketepatan waktu penting. Ubah toleransi di `config.py` untuk menyeimbangkan tingkat kesulitan.

## Harga jual dan profit

Harga jual dihitung dari `base_price × difficulty_multiplier × quality_multiplier`, kemudian dibulatkan ke integer terdekat. Harga market yang dibayar dicatat sebagai biaya ketika transaksi checkout berhasil. Profit bersih yang ditampilkan adalah total pendapatan penjualan dikurangi biaya belanja bahan yang tercatat.

## Pergantian hari

Penjualan mengurangi kuota harian satu per makanan yang dijual, bukan satu per transaksi. Tombol Akhiri Hari menaikkan nomor hari dan mengatur `daily_sales` kembali ke nol. Tidak ada penalti harian atau biaya operasional otomatis pada versi ini.

## Bangkrut dan kemenangan

Kondisi bangkrut aktif ketika uang pemain nol atau kurang serta pemain tidak memiliki bahan dan makanan yang masih dapat dipakai/dijual. Karena game berorientasi pada akumulasi keuntungan, belum ada angka target menang permanen. Pemain dapat terus meningkatkan profit selama belum bangkrut.
