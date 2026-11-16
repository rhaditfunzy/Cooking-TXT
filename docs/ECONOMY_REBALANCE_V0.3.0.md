# Cooking TXT — Economy Rebalance v0.3.0

## Tujuan

Membuat kualitas `poor` dapat menghasilkan kerugian per hidangan, sementara `mid` tetap memberi laba kecil dan `good` memberikan imbalan lebih besar. Harga Market bahan dan pengali kesulitan/kualitas sengaja dipertahankan agar perubahan terfokus pada harga dasar resep.

## Rumus yang dipakai

```text
selling_price = round(base_price × difficulty_multiplier × quality_multiplier)
```

Pengali tetap:

| Kesulitan | Pengali |
|---|---:|
| easy | 1.00 |
| normal | 1.25 |
| hard | 1.60 |

| Kualitas | Pengali |
|---|---:|
| poor | 0.70 |
| mid | 0.90 |
| good | 1.15 |

## Harga bahan Market (tidak diubah)

| Bahan | Harga/unit |
|---|---:|
| Beef | 35 |
| Chicken Leg | 18 |
| Salmon Fillet | 45 |
| Shrimp | 25 |
| Lemon | 5 |
| Lettuce | 5 |
| Potato | 7 |
| Rice | 4 |
| Dough | 6 |
| Egg | 6 |
| Milk | 5 |

## Harga resep dan hasil simulasi

Modal dihitung dari `market_price × quantity` untuk setiap bahan. Semua resep bawaan saat ini memakai satu unit tiap bahan.

| Resep | Modal bahan | Base price lama | Base price baru | Poor: jual (laba/rugi) | Mid: jual (laba/rugi) | Good: jual (laba/rugi) |
|---|---:|---:|---:|---:|---:|---:|
| Egg Fried Rice | 10 | 45 | 13 | 9 (-1) | 12 (+2) | 15 (+5) |
| Lemon Chicken | 30 | 72 | 38 | 27 (-3) | 34 (+4) | 44 (+14) |
| Shrimp Salad | 35 | 65 | 44 | 31 (-4) | 40 (+5) | 51 (+16) |
| Beef Fried Rice | 50 | 100 | 50 | 44 (-6) | 56 (+6) | 72 (+22) |
| Salmon Pie | 67 | 150 | 52 | 58 (-9) | 75 (+8) | 96 (+29) |
| Creamy Lemon Shrimp Rice | 39 | 110 | 39 | 34 (-5) | 44 (+5) | 56 (+17) |

`Laba/rugi` di tabel adalah harga jual dikurangi modal bahan resep, sebelum biaya lain. Pembulatan menggunakan fungsi `round()` Python seperti implementasi game.

## Alasan kalibrasi

Harga efektif sebelum pengali kualitas ditargetkan sekitar 1.25 kali modal bahan. Dengan demikian:

- Poor: sekitar 0.875 kali modal → rugi sekitar 12.5% sebelum efek pembulatan.
- Mid: sekitar 1.125 kali modal → laba sekitar 12.5%.
- Good: sekitar 1.4375 kali modal → laba sekitar 43.75%.

Harga `base_price` tiap resep disesuaikan dengan pengali kesulitannya agar hasil akhirnya berada di rentang margin yang serupa.

## Dampak ke permainan

- Keenam resep bawaan mengalami rugi ketika kualitas Poor.
- Keenam resep masih menghasilkan laba ketika kualitas Mid dan Good.
- Good tetap memberi insentif yang terasa, tetapi tidak lagi menghasilkan markup berlipat-lipat seperti sebelumnya.
- Harga bahan Market, modal awal, batas penjualan harian, dan rumus kebangkrutan tidak berubah.

## Catatan save lama

`Food` yang sudah berada di `saves/player_save.json` menyimpan `base_price` pada saat makanan dibuat. Setelah harga resep diperbarui, makanan lama di inventori masih membawa harga lama. Jalankan `python migrate_economy_save.py` satu kali setelah memasang patch untuk menyelaraskan harga makanan yang belum terjual. Script membuat backup save bertimestamp sebelum menulis perubahan. Jika tidak ada save, script aman dan tidak melakukan apa pun.

## Ruang lingkup akuntansi

Game saat ini mencatat biaya saat bahan dibeli (`total_expenses`) dan pendapatan saat makanan terjual (`total_revenue`). `net_profit` adalah pendapatan kas kumulatif dikurangi seluruh belanja bahan, bukan COGS per batch. Perhitungan modal pada tabel ini dipakai untuk kalibrasi per resep, bukan mengubah cara dashboard menghitung arus kas.

## Pengujian

Jalankan:

```bash
python -m unittest discover -s tests -v
```

Test tambahan `tests/test_economy_balance.py` memeriksa modal resep aktual dari JSON dan memastikan Poor rugi sementara Mid/Good tetap untung.
