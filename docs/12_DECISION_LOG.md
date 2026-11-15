# 12 — Decision Log

Catatan ini menjelaskan keputusan teknis dan asumsi yang digunakan pada build pertama. Keputusan dapat direvisi, tetapi perubahan harus ikut memperbarui kode, test, dan dokumen terkait.

## DEC-001 — Data resep dan bahan memakai JSON terpisah

**Masalah:** resep/bahan perlu mudah ditambah tanpa mengubah Python.

**Keputusan:** satu file JSON untuk setiap bahan dan resep.

**Alasan:** konten dapat diubah secara mandiri, mudah dibaca, dan tidak memerlukan edit kode untuk penambahan normal.

**Konsekuensi:** dibutuhkan loader dan validasi; typo ID atau JSON invalid bisa membuat konten dilewati/gagal dimuat.

## DEC-002 — Logic gameplay dipisahkan ke systems

**Masalah:** jika logic market, cooking, dan ekonomi berada di satu file UI, perubahan akan sulit dirawat dan diuji.

**Keputusan:** buat `MarketSystem`, `CookingSystem`, `InventorySystem`, `EconomySystem`, dan `DaySystem`.

**Alasan:** tanggung jawab jelas dan sebagian besar logic bisa dites tanpa Pygame.

**Konsekuensi:** `Game` perlu mengoordinasikan beberapa objek sistem.

## DEC-003 — Timer bahan dihitung relatif terhadap aksi sebelumnya

**Masalah:** perlu menentukan apakah keterlambatan satu tahap menggeser tahapan berikutnya.

**Keputusan:** interval tahap berikutnya dimulai dari waktu aksi aktual pemain.

**Alasan:** satu keterlambatan tidak membuat semua tahap berikutnya otomatis terlewat, tetapi tetap tercatat sebagai pengurang kualitas.

**Konsekuensi:** jadwal aktual dapat bergeser dari total durasi resep jika pemain terlambat.

## DEC-004 — Kualitas memakai deviasi terburuk

**Masalah:** perlu rumus untuk menggabungkan beberapa input timing.

**Keputusan:** gunakan nilai deviasi terbesar dari semua bahan dan pengambilan makanan.

**Alasan:** semua tahap penting; satu kesalahan besar tetap terasa pada hasil akhir.

**Konsekuensi:** satu input buruk bisa menurunkan kualitas seluruh makanan. Toleransi berada di `config.py`.

## DEC-005 — Nilai awal harga dan modal ditambahkan

**Masalah:** dokumen konsep belum menentukan angka harga bahan, harga dasar resep, dan modal awal.

**Keputusan:** modal Rp250, harga market dan `base_price` diisi dengan angka awal untuk prototipe.

**Alasan:** game perlu dapat dimainkan dan diuji dari awal.

**Konsekuensi:** ekonomi masih perlu playtesting dan balancing; semua nilai mudah diubah di JSON/config.

## DEC-006 — Hari berakhir secara manual

**Masalah:** dokumen menetapkan limit lima makanan per hari tetapi belum menjelaskan durasi satu hari.

**Keputusan:** pemain menekan tombol Akhiri Hari.

**Alasan:** sederhana dan tidak memaksa pemain menunggu timer hari.

**Konsekuensi:** tidak ada simulasi jam, biaya harian, atau kejadian harian.

## DEC-007 — Save menyimpan progres ekonomi, bukan sesi aktif

**Masalah:** perlu menentukan ruang lingkup save awal.

**Keputusan:** simpan saldo, hari, stok, inventori makanan, pendapatan, biaya, dan hitungan penjualan. Tidak simpan cart atau cooking session.

**Alasan:** menjaga format save sederhana untuk versi pertama.

**Konsekuensi:** keluar di tengah cooking setelah bahan dikonsumsi berarti bahan tidak dikembalikan dan sesi tidak dapat dilanjutkan. Pertimbangkan menyimpan snapshot sesi pada iterasi berikutnya.

## DEC-008 — Profit bersih didefinisikan sebagai revenue dikurangi total pembelian bahan

**Masalah:** belum ada biaya per unit yang dialokasikan ke masing-masing makanan.

**Keputusan:** total expenses bertambah saat checkout; net profit = revenue - expenses.

**Alasan:** mudah dipahami untuk prototipe ekonomi.

**Konsekuensi:** ini bukan perhitungan laba per produk/COGS; biaya bahan yang masih menjadi stok tetap sudah masuk biaya.
