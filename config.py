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

COLORS = {
    "background": (23, 26, 33),
    "surface": (33, 38, 48),
    "surface_light": (43, 49, 62),
    "border": (67, 76, 93),
    "text": (240, 243, 248),
    "muted": (164, 174, 190),
    "accent": (242, 166, 74),
    "accent_dark": (194, 119, 39),
    "green": (92, 190, 125),
    "red": (226, 94, 94),
    "blue": (93, 158, 218),
    "white": (255, 255, 255),
}
