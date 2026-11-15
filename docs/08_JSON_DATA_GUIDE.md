# 08 — JSON Data Guide

Semua file harus UTF-8 dan berakhiran `.json`. Nama file bebas, tetapi `id` harus unik di seluruh folder kategori yang sama. Setelah menambah/mengubah data, tutup lalu jalankan ulang game agar data dibaca kembali.

## Menambah bahan

Buat file baru di `data/ingredients/`, misalnya `tomato.json`:

```json
{
  "id": "tomato",
  "name": "Tomato",
  "category": "vegetable",
  "market_price": 8,
  "image": "assets/images/ingredients/tomato.png",
  "description": "Tomat segar."
}
```

Field wajib:

| Field | Tipe | Keterangan |
|---|---|---|
| `id` | string | ID unik, gunakan huruf kecil dan underscore |
| `name` | string | Nama yang tampil di UI |
| `category` | string | Kelompok bahan; bebas untuk sekarang |
| `market_price` | integer | Harga beli per unit, tidak boleh negatif |

Field opsional: `image`, `description`. Gambar tidak wajib tersedia agar data tetap valid.

## Menambah resep

Buat file baru di `data/recipes/`, misalnya `tomato_egg.json`:

```json
{
  "id": "tomato_egg",
  "name": "Tomato Egg",
  "difficulty": "easy",
  "ingredients": [
    { "id": "tomato", "quantity": 1, "timing": 2 },
    { "id": "egg", "quantity": 1, "timing": 8 }
  ],
  "cooking_time": 15,
  "base_price": 55,
  "image": "assets/images/recipes/tomato_egg.png",
  "description": "Telur dengan tomat."
}
```

Field resep:

| Field | Tipe | Keterangan |
|---|---|---|
| `id` | string | ID unik resep |
| `name` | string | Nama masakan |
| `difficulty` | string | `easy`, `normal`, atau `hard` |
| `ingredients` | array | 1–5 step bahan |
| `ingredients[].id` | string | Harus cocok dengan ID bahan |
| `ingredients[].quantity` | integer | Jumlah bahan yang dikonsumsi; default 1 jika dihilangkan |
| `ingredients[].timing` | angka | Interval detik dari aksi sebelumnya; boleh 0 |
| `cooking_time` | angka | Interval detik untuk mengambil makanan setelah bahan terakhir |
| `base_price` | integer | Harga dasar sebelum pengali difficulty/quality |
| `image` | string | Path relatif gambar resep; opsional |
| `description` | string | Deskripsi; opsional |

## Aturan penting

- Maksimal lima step bahan per resep, mengikuti batas konsep.
- Setiap step adalah satu jenis bahan. Jika resep butuh dua unit ingredient yang sama, set `quantity: 2` pada step tersebut.
- ID bahan harus sudah ada di `data/ingredients/`.
- Difficulty harus persis `easy`, `normal`, atau `hard`.
- `timing` adalah detik, bukan jumlah bahan.
- Jika dua bahan harus dimasukkan berurutan tanpa jeda, timing bahan berikutnya dapat diatur `0`.
- Hindari ID duplikat.

## Menambahkan gambar

Letakkan gambar di lokasi yang sesuai dan tulis path relatif dari root proyek, misalnya `assets/images/ingredients/tomato.png`. Gambar bersifat opsional di build UI awal; sistem `AssetLoader` sudah disediakan sebagai dasar integrasi artwork berikutnya. Format yang umum untuk Pygame: PNG atau JPG.

## Validasi saat startup

- Ingredient JSON yang invalid membuat loader bahan mengeluarkan `ValueError`.
- Recipe JSON yang invalid dilewati; nama file dan alasan kesalahan masuk ke `RecipeSystem.errors`.
- Resep yang mengacu pada bahan yang tidak ada dianggap invalid.
