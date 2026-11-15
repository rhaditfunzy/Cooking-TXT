# 06 — Economy System

## Sumber angka

- Harga beli bahan berasal dari `market_price` di masing-masing `data/ingredients/*.json`.
- Harga dasar makanan berasal dari `base_price` di masing-masing `data/recipes/*.json`.
- Pengali kesulitan dan kualitas berada di `config.py`.

## Rumus harga jual

```text
selling_price = round(base_price × difficulty_multiplier × quality_multiplier)
```

Default difficulty multiplier:

| Difficulty | Multiplier |
|---|---:|
| easy | 1.00 |
| normal | 1.25 |
| hard | 1.60 |

Default quality multiplier:

| Quality | Multiplier |
|---|---:|
| poor | 0.70 |
| mid | 0.90 |
| good | 1.15 |

Harga jual minimum adalah Rp1.

## Statistik uang

- `money`: saldo yang dapat dibelanjakan.
- `total_revenue`: akumulasi hasil penjualan.
- `total_expenses`: akumulasi pembelian bahan.
- `net_profit`: `total_revenue - total_expenses`.

Biaya bahan dicatat saat checkout. Tidak ada biaya lain (sewa, gaji, listrik, pajak, atau waste) pada versi ini. Karena biaya dihitung saat beli, `net_profit` adalah laba kas sederhana dari pendapatan dikurangi total belanja bahan, bukan laporan laba rugi per makanan yang terjual.

## Bankruptcy

`EconomySystem.is_bankrupt(player)` bernilai true saat `money <= 0`, `food_inventory` kosong, dan seluruh stok bahan nol atau tidak positif. Ini asumsi implementasi untuk membuat kondisi kalah dapat diuji. Jika ingin definisi lain (misalnya saldo negatif, hutang, atau jumlah hari rugi), ubah fungsi ini dan dokumen ini.
