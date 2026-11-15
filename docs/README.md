# Dokumentasi Cooking TXT

Dokumentasi ini menjelaskan versi kode yang disertakan dalam proyek. Jika ada perbedaan antara rencana dan implementasi, dokumentasi menjelaskan perilaku implementasi saat ini.

| Dokumen | Isi |
|---|---|
| [00 Project Overview](00_PROJECT_OVERVIEW.md) | Tujuan, fitur, dan status cakupan game |
| [01 Architecture](01_ARCHITECTURE.md) | Struktur folder dan komunikasi antarmodul |
| [02 Game Mechanics](02_GAME_MECHANICS.md) | Aturan permainan, ekonomi, hari, dan asumsi |
| [03 Cooking System](03_COOKING_SYSTEM.md) | State machine, timer, penilaian kualitas |
| [04 Market System](04_MARKET_SYSTEM.md) | Keranjang dan transaksi |
| [05 Inventory & Selling](05_INVENTORY_SELLING.md) | Stok bahan, hasil masakan, penjualan |
| [06 Economy System](06_ECONOMY_SYSTEM.md) | Harga jual, pendapatan, biaya, bangkrut |
| [07 API Reference](07_API_REFERENCE.md) | Class, fungsi, parameter, return, efek samping |
| [08 JSON Data Guide](08_JSON_DATA_GUIDE.md) | Cara menambah bahan dan resep |
| [09 UI/UX Guide](09_UI_UX_GUIDE.md) | Navigasi dan kontrol layar |
| [10 Save System](10_SAVE_SYSTEM.md) | Struktur dan aturan save |
| [11 Development Guide](11_DEVELOPMENT_GUIDE.md) | Menjalankan, menguji, dan mengembangkan |
| [12 Decision Log](12_DECISION_LOG.md) | Alasan keputusan teknis dan asumsi |
| [Changelog](CHANGELOG.md) | Riwayat versi |

## Prinsip dokumentasi

- API di sini berarti API internal Python, yaitu antarmuka antarclass dan modul, bukan layanan web.
- Setiap perubahan yang memengaruhi perilaku harus diikuti pembaruan dokumen terkait.
- Contoh kode harus mengikuti kode yang benar-benar ada.
- Nilai gameplay yang belum ditetapkan di dokumen konsep ditandai sebagai asumsi implementasi.
