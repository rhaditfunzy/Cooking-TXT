# 10 — Save System

## Lokasi

`SaveManager` menulis progres ke `saves/player_save.json`.

## Isi save

```json
{
  "version": 1,
  "player": {
    "money": 250,
    "day": 1,
    "daily_sales": 0,
    "daily_sell_limit": 5,
    "ingredient_stock": {},
    "food_inventory": [],
    "total_revenue": 0,
    "total_expenses": 0,
    "total_items_sold": 0
  }
}
```

Angka di atas hanya contoh bentuk data, bukan selalu nilai save aktif.

## Kapan disimpan?

- Setelah pembelian berhasil.
- Setelah memasak selesai dan Food masuk ke Inventory.
- Setelah penjualan berhasil.
- Setelah pergantian hari.
- Saat aplikasi ditutup normal.
- Ketika pemain menekan **Simpan Sekarang** di Profile.

## Cara penulisan

Save ditulis ke file sementara dengan akhiran `.tmp`, kemudian dipindahkan menggantikan file utama. Tujuannya mengurangi risiko file utama berisi JSON setengah tertulis jika proses terhenti saat penulisan.

## Batasan

- Keranjang Market tidak disimpan.
- Sesi memasak aktif tidak disimpan untuk dilanjutkan.
- Jika aplikasi ditutup saat memasak aktif, bahan yang telah dikonsumsi sejak mulai sesi tidak dikembalikan pada versi ini.
- `version` disertakan untuk memudahkan migrasi format di masa depan, tetapi migrator lintas versi belum dibuat.
- Jika save rusak/tidak valid, game membuat Player baru. File rusak tidak otomatis dihapus atau ditimpa sampai save baru disimpan.

## Reset progres

Untuk memulai dari awal, tutup game dan hapus atau pindahkan `saves/player_save.json`. Saat game dibuka lagi, Player baru dibuat.
