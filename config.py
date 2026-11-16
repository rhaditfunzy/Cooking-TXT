"""Konfigurasi utama Cooking TXT.

Nilai di sini adalah default proyek. Ubah bagian ini untuk menyesuaikan ukuran
jendela, modal awal, batas penjualan, dan aturan harga.
"""

GAME_TITLE = "Cooking TXT"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60

STARTING_MONEY = 250
DAILY_SELL_LIMIT = 5
STARTING_DAY = 1
COUNTDOWN_SECONDS = 3.0

# Selisih waktu maksimum dari target untuk setiap aksi memasak.
GOOD_TIMING_TOLERANCE = 0.25
MID_TIMING_TOLERANCE = 1.00

# Pengali harga jual. Harga dasar resep dikalikan difficulty dan quality.
DIFFICULTY_MULTIPLIERS = {
    "easy": 1.00,
    "normal": 1.25,
    "hard": 1.60,
}
QUALITY_MULTIPLIERS = {
    "poor": 0.70,
    "mid": 0.90,
    "good": 1.15,
}

DATA_DIR = "data"
ASSET_DIR = "assets"
SAVE_PATH = "saves/player_save.json"

# Cooking TXT — Cozy Rustic palette.
# Warna utama mengikuti style guide; warna kertas/garis merupakan turunan netral.
COLORS = {
    "background": (243, 235, 220),       # parchment warm
    "surface": (255, 249, 238),          # warm paper
    "surface_light": (247, 237, 221),    # secondary paper
    "paper_alt": (238, 225, 204),
    "paper_line": (236, 225, 208),
    "border": (216, 197, 166),
    "border_dark": (126, 93, 70),
    "text": (87, 59, 48),                # #573B30 roasted brown
    "muted": (126, 103, 86),
    "accent": (188, 96, 64),             # #BC6040 terracotta
    "accent_dark": (151, 71, 49),
    "mustard": (221, 152, 77),           # #DD984D warm mustard
    "green": (141, 162, 143),            # #8DA28F sage
    "sage": (141, 162, 143),
    "red": (188, 96, 64),
    "blue": (56, 116, 170),              # #3874AA blue
    "teal": (82, 121, 120),              # #527978 muted teal
    "nav": (82, 121, 120),
    "nav_dark": (58, 91, 91),
    "white": (255, 252, 245),
}
