"""Aplikasi Pygame dan penghubung seluruh sistem Cooking TXT."""
from __future__ import annotations
import sys
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from src.core import state
from src.entities.player import Player
from src.systems.recipe_system import RecipeSystem
from src.systems.market_system import MarketSystem
from src.systems.inventory_system import InventorySystem
from src.systems.cooking_system import CookingSystem
from src.systems.economy_system import EconomySystem
from src.systems.day_system import DaySystem
from src.utils.json_loader import load_ingredients
from src.utils.save_manager import SaveManager
from src.utils.asset_loader import AssetLoader


class Game:
    """Mengelola loop utama, navigasi layar, input, dan rendering."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.GAME_TITLE)
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("segoeui", 18)
        self.font_small = pygame.font.SysFont("segoeui", 14)
        self.font_medium = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_large = pygame.font.SysFont("segoeui", 34, bold=True)

        self.ingredients = load_ingredients(ROOT / config.DATA_DIR / "ingredients")
        self.recipe_system = RecipeSystem(
            ROOT / config.DATA_DIR / "recipes", set(self.ingredients.keys())
        )
        self.save_manager = SaveManager(ROOT / config.SAVE_PATH)
        self.player = self.save_manager.load() or Player()
        self.market = MarketSystem(self.ingredients)
        self.inventory = InventorySystem(self.player)
        self.cooking = CookingSystem()
        self.assets = AssetLoader(ROOT)

        self.screen_name = state.HOME
        self.selected_recipe_id: str | None = None
        self.market_quantities = {key: 1 for key in self.ingredients}
        self.inventory_scroll = 0
        self.stock_scroll = 0
        self.market_scroll = 0
        self.cart_scroll = 0
        self.recipe_scroll = 0
        self.message = "Selamat datang! Mulailah dengan membeli bahan di Market."
        self.message_color = config.COLORS["muted"]
        self.buttons: dict[str, pygame.Rect] = {}
        self._now = 0.0
        self._last_cooked_food_id: str | None = None

    # ---------- Drawing primitives ----------
    def draw_text(self, text: str, x: int, y: int, color=None, font=None):
        font = font or self.font
        color = color or config.COLORS["text"]
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))
        return surface.get_rect(topleft=(x, y))

    def wrap_text(self, text: str, x: int, y: int, width: int, color=None,
                  font=None, line_height: int = 23, max_lines: int = 4):
        font = font or self.font_small
        color = color or config.COLORS["muted"]
        words = str(text).split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        for index, line in enumerate(lines[:max_lines]):
            self.draw_text(line, x, y + index * line_height, color, font)
        if len(lines) > max_lines:
            self.draw_text("…", x + width - 12, y + (max_lines - 1) * line_height, color, font)

    def panel(self, rect: pygame.Rect, fill=None, border=None, radius=14):
        pygame.draw.rect(self.screen, fill or config.COLORS["surface"], rect, border_radius=radius)
        pygame.draw.rect(self.screen, border or config.COLORS["border"], rect, 1, border_radius=radius)

    def draw_optional_image(self, relative_path: str, rect: pygame.Rect, fallback_label: str = ""):
        """Menggambar gambar jika tersedia; jika tidak, tampilkan placeholder."""
        image = self.assets.image(relative_path, rect.size)
        if image:
            self.screen.blit(image, rect.topleft)
        else:
            pygame.draw.rect(self.screen, config.COLORS["surface"], rect, border_radius=7)
            pygame.draw.rect(self.screen, config.COLORS["border"], rect, 1, border_radius=7)
            if fallback_label:
                label = self.font_small.render(fallback_label[:2].upper(), True, config.COLORS["muted"])
                self.screen.blit(label, label.get_rect(center=rect.center))

    def button(self, button_id: str, label: str, rect: pygame.Rect,
               enabled: bool = True, color=None, font=None):
        if enabled:
            self.buttons[button_id] = rect
        else:
            self.buttons.pop(button_id, None)
        fill = color or config.COLORS["accent"]
        if not enabled:
            fill = config.COLORS["surface_light"]
        elif pygame.Rect(rect).collidepoint(pygame.mouse.get_pos()):
            fill = tuple(min(255, c + 18) for c in fill)
        pygame.draw.rect(self.screen, fill, rect, border_radius=9)
        pygame.draw.rect(self.screen, config.COLORS["border"], rect, 1, border_radius=9)
        font = font or self.font_small
        text_surface = font.render(label, True, config.COLORS["background"] if enabled else config.COLORS["muted"])
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def nav_button(self, key: str, label: str, x: int, active: bool):
        rect = pygame.Rect(x, 27, 112, 38)
        self.buttons[f"nav_{key}"] = rect
        fill = config.COLORS["accent"] if active else config.COLORS["surface_light"]
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        text_color = config.COLORS["background"] if active else config.COLORS["text"]
        surface = self.font_small.render(label, True, text_color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))

    def header(self):
        pygame.draw.rect(self.screen, (19, 22, 29), (0, 0, config.WINDOW_WIDTH, 94))
        self.draw_text("COOKING TXT", 30, 13, config.COLORS["accent"], self.font_medium)
        self.draw_text(f"Hari {self.player.day}", 30, 52, config.COLORS["muted"], self.font_small)
        nav_items = [
            ("home", "Home"), ("market", "Market"), ("recipes", "Recipes"),
            ("inventory", "Inventory"), ("profile", "Profile"),
        ]
        start_x = 260
        for index, (key, label) in enumerate(nav_items):
            self.nav_button(key, label, start_x + index * 118, self.screen_name == key)
        self.draw_text(self.money(self.player.money), 1015, 23, config.COLORS["green"], self.font_medium)
        self.draw_text(f"Terjual hari ini: {self.player.daily_sales}/{self.player.daily_sell_limit}",
                       1015, 54, config.COLORS["muted"], self.font_small)

    @staticmethod
    def money(value: int) -> str:
        return f"Rp {value:,}".replace(",", ".")

    def page_title(self, title: str, subtitle: str):
        self.draw_text(title, 30, 116, config.COLORS["text"], self.font_large)
        self.draw_text(subtitle, 32, 158, config.COLORS["muted"], self.font_small)

    def draw_message(self):
        if self.message:
            rect = pygame.Rect(30, 752, 1220, 30)
            pygame.draw.rect(self.screen, (28, 32, 41), rect, border_radius=7)
            self.draw_text(self.message, 42, 757, self.message_color, self.font_small)

    # ---------- Screens ----------
    def draw_home(self):
        self.page_title("Dashboard", "Kelola toko, belanja bahan, masak, lalu jual hasil masakanmu.")
        cards = [
            (30, "Saldo", self.money(self.player.money), config.COLORS["green"]),
            (340, "Keuntungan bersih", self.money(self.player.net_profit), config.COLORS["accent"]),
            (650, "Total terjual", str(self.player.total_items_sold), config.COLORS["blue"]),
            (960, "Stok makanan", str(len(self.player.food_inventory)), config.COLORS["text"]),
        ]
        for x, title, value, color in cards:
            rect = pygame.Rect(x, 205, 285, 112)
            self.panel(rect)
            self.draw_text(title, x + 18, 221, config.COLORS["muted"], self.font_small)
            self.draw_text(value, x + 18, 255, color, self.font_medium)

        self.panel(pygame.Rect(30, 340, 770, 365))
        self.draw_text("Mulai berjualan", 54, 362, config.COLORS["text"], self.font_medium)
        steps = [
            "1. Buka Market dan beli bahan yang dibutuhkan.",
            "2. Buka Recipes, pilih masakan, lalu mulai memasak.",
            "3. Ikuti timer untuk memasukkan bahan dan mengambil masakan.",
            "4. Buka Inventory untuk menjual hasil masakan.",
        ]
        for idx, line in enumerate(steps):
            self.draw_text(line, 56, 415 + idx * 47, config.COLORS["muted"], self.font)
        self.draw_text("Tips: kualitas Good didapat jika setiap aksi dekat dengan target timer.",
                       56, 622, config.COLORS["accent"], self.font_small)
        self.button("home_market", "Buka Market", pygame.Rect(56, 654, 145, 36))
        self.button("home_recipes", "Lihat Resep", pygame.Rect(214, 654, 145, 36), color=config.COLORS["blue"])

        self.panel(pygame.Rect(825, 340, 425, 365))
        self.draw_text("Ringkasan hari ini", 850, 362, config.COLORS["text"], self.font_medium)
        self.draw_text(f"Hari: {self.player.day}", 850, 420, config.COLORS["muted"])
        self.draw_text(f"Penjualan: {self.player.daily_sales}/{self.player.daily_sell_limit}",
                       850, 461, config.COLORS["muted"])
        self.draw_text(f"Pendapatan: {self.money(self.player.total_revenue)}", 850, 502,
                       config.COLORS["muted"])
        self.draw_text(f"Belanja bahan: {self.money(self.player.total_expenses)}", 850, 543,
                       config.COLORS["muted"])
        self.button("end_day", "Akhiri Hari", pygame.Rect(850, 622, 170, 42), color=config.COLORS["blue"])
        if EconomySystem.is_bankrupt(self.player):
            self.draw_text("TOKO BANGKRUT", 850, 580, config.COLORS["red"], self.font_medium)

    def draw_market(self):
        self.page_title("Market", "Pilih jumlah bahan, tambahkan ke keranjang, lalu lakukan pembelian.")
        left = pygame.Rect(30, 195, 790, 535)
        right = pygame.Rect(840, 195, 410, 535)
        self.panel(left)
        self.panel(right)
        self.draw_text("Bahan tersedia", 52, 211, config.COLORS["text"], self.font_medium)
        self.draw_text("Keranjang", 862, 211, config.COLORS["text"], self.font_medium)

        item_list = list(self.ingredients.values())
        visible_items = item_list[self.market_scroll:self.market_scroll + 12]
        for index, ingredient in enumerate(visible_items):
            col = index // 6
            row = index % 6
            x = 50 + col * 385
            y = 252 + row * 75
            self.panel(pygame.Rect(x, y, 360, 64), fill=config.COLORS["surface_light"], radius=9)
            self.draw_optional_image(ingredient.image, pygame.Rect(x + 8, y + 12, 40, 40), ingredient.name)
            self.draw_text(ingredient.name, x + 58, y + 8, config.COLORS["text"], self.font_small)
            self.draw_text(self.money(ingredient.market_price), x + 58, y + 34, config.COLORS["muted"], self.font_small)
            qty = self.market_quantities[ingredient.id]
            self.button(f"market_minus_{ingredient.id}", "-", pygame.Rect(x + 190, y + 18, 28, 28), color=config.COLORS["blue"])
            self.draw_text(str(qty), x + 229, y + 22, config.COLORS["text"], self.font_small)
            self.button(f"market_plus_{ingredient.id}", "+", pygame.Rect(x + 250, y + 18, 28, 28), color=config.COLORS["blue"])
            self.button(f"market_add_{ingredient.id}", "Tambah", pygame.Rect(x + 286, y + 18, 65, 28))
        if len(item_list) > 12:
            self.button("market_scroll_up", "▲", pygame.Rect(738, 207, 30, 28), enabled=self.market_scroll > 0, color=config.COLORS["blue"])
            self.button("market_scroll_down", "▼", pygame.Rect(774, 207, 30, 28),
                        enabled=self.market_scroll + 12 < len(item_list), color=config.COLORS["blue"])

        cart_y = 253
        cart_items = list(self.market.cart.items())
        visible_cart = cart_items[self.cart_scroll:self.cart_scroll + 10]
        if not cart_items:
            self.draw_text("Keranjang masih kosong.", 864, cart_y, config.COLORS["muted"], self.font_small)
        else:
            for ingredient_id, quantity in visible_cart:
                ingredient = self.ingredients[ingredient_id]
                self.draw_text(f"{ingredient.name} x{quantity}", 864, cart_y, config.COLORS["text"], self.font_small)
                self.draw_text(self.money(ingredient.market_price * quantity), 1085, cart_y,
                               config.COLORS["muted"], self.font_small)
                self.button(f"cart_remove_{ingredient_id}", "−1", pygame.Rect(1190, cart_y - 3, 42, 25), color=config.COLORS["blue"])
                cart_y += 30
        if len(cart_items) > 10:
            self.button("cart_scroll_up", "▲", pygame.Rect(1178, 207, 30, 28), enabled=self.cart_scroll > 0, color=config.COLORS["blue"])
            self.button("cart_scroll_down", "▼", pygame.Rect(1213, 207, 30, 28),
                        enabled=self.cart_scroll + 10 < len(cart_items), color=config.COLORS["blue"])
        total_y = 603
        self.draw_text("Total belanja", 864, total_y, config.COLORS["muted"], self.font_small)
        self.draw_text(self.money(self.market.cart_total()), 864, total_y + 27,
                       config.COLORS["accent"], self.font_medium)
        self.button("cart_buy", "Buy", pygame.Rect(864, 670, 150, 40), enabled=bool(self.market.cart))
        self.button("cart_clear", "Clear", pygame.Rect(1025, 670, 150, 40),
                    enabled=bool(self.market.cart), color=config.COLORS["blue"])

    def _ingredient_summary(self, recipe: dict) -> str:
        parts = []
        for step in recipe["ingredients"]:
            ingredient = self.ingredients[step["id"]]
            quantity = int(step.get("quantity", 1))
            parts.append(f"{ingredient.name} x{quantity} ({step['timing']}s)")
        return "  •  ".join(parts)

    def draw_recipes(self):
        self.page_title("Recipe Book", "Pilih resep untuk melihat kebutuhan bahan dan memulai proses memasak.")
        recipes = self.recipe_system.all()
        visible_recipes = recipes[self.recipe_scroll:self.recipe_scroll + 6]
        for index, recipe in enumerate(visible_recipes):
            col, row = index % 2, index // 2
            x = 30 + col * 615
            y = 195 + row * 170
            rect = pygame.Rect(x, y, 590, 150)
            self.panel(rect)
            difficulty_color = {"easy": config.COLORS["green"], "normal": config.COLORS["accent"], "hard": config.COLORS["red"]}.get(recipe["difficulty"], config.COLORS["text"])
            self.draw_text(recipe["name"], x + 18, y + 13, config.COLORS["text"], self.font_medium)
            self.draw_text(recipe["difficulty"].upper(), x + 18, y + 45, difficulty_color, self.font_small)
            self.draw_text(f"Matang: {recipe['cooking_time']} detik  |  Harga dasar: {self.money(int(recipe['base_price']))}",
                           x + 18, y + 72, config.COLORS["muted"], self.font_small)
            self.draw_optional_image(recipe.get("image", ""), pygame.Rect(x + 18, y + 96, 44, 44), recipe["name"])
            self.wrap_text(self._ingredient_summary(recipe), x + 74, y + 98, 350,
                           config.COLORS["muted"], self.font_small, line_height=18, max_lines=2)
            enough, missing = self.inventory.has_ingredients(recipe)
            label = "Cook" if enough else "Bahan kurang"
            self.button(f"recipe_cook_{recipe['id']}", label,
                        pygame.Rect(x + 450, y + 94, 120, 38), enabled=enough)
        if len(recipes) > 6:
            self.button("recipe_scroll_up", "▲", pygame.Rect(1178, 158, 30, 28), enabled=self.recipe_scroll > 0, color=config.COLORS["blue"])
            self.button("recipe_scroll_down", "▼", pygame.Rect(1213, 158, 30, 28),
                        enabled=self.recipe_scroll + 6 < len(recipes), color=config.COLORS["blue"])
        if not recipes:
            self.draw_text("Belum ada resep valid. Periksa folder data/recipes.", 45, 220, config.COLORS["red"])
        if self.recipe_system.errors:
            self.draw_text(f"Peringatan: {len(self.recipe_system.errors)} file resep dilewati.",
                           45, 710, config.COLORS["red"], self.font_small)

    def draw_cooking(self):
        recipe = self.recipe_system.get(self.selected_recipe_id or "")
        self.page_title("Cooking Station", "Tekan tombol aksi saat timer mencapai target. Selisih waktu memengaruhi kualitas.")
        if not recipe:
            self.draw_text("Resep tidak ditemukan. Kembali ke Recipe Book.", 40, 220, config.COLORS["red"])
            self.button("cooking_back", "Kembali ke Resep", pygame.Rect(40, 280, 180, 42))
            return
        self.panel(pygame.Rect(30, 195, 520, 520))
        self.panel(pygame.Rect(570, 195, 680, 520))
        self.draw_text(recipe["name"], 55, 220, config.COLORS["text"], self.font_medium)
        self.draw_text(f"Kesulitan: {recipe['difficulty'].upper()}", 55, 260, config.COLORS["muted"], self.font_small)
        self.draw_text("Urutan bahan", 55, 315, config.COLORS["accent"], self.font_medium)
        for index, step in enumerate(recipe["ingredients"]):
            ingredient = self.ingredients[step["id"]]
            prefix = "✓" if self.cooking.step_index > index or self.cooking.phase in {"final_cooking", "finished"} else f"{index + 1}."
            self.draw_text(f"{prefix} {ingredient.name} x{step.get('quantity', 1)}", 60, 360 + index * 42,
                           config.COLORS["text"], self.font)
            self.draw_text(f"Target +{step['timing']}s", 330, 364 + index * 42,
                           config.COLORS["muted"], self.font_small)
        self.draw_text(f"Waktu memasak akhir: {recipe['cooking_time']} detik", 55, 600,
                       config.COLORS["muted"], self.font_small)

        phase_label = {
            "idle": "SIAP MEMASAK", "countdown": "BERSIAP", "ingredient_timing": "MASUKKAN BAHAN",
            "final_cooking": "PROSES MEMASAK", "finished": "SELESAI",
        }.get(self.cooking.phase, self.cooking.phase.upper())
        self.draw_text(phase_label, 610, 228, config.COLORS["accent"], self.font_medium)
        if self.cooking.phase == "countdown":
            big = str(self.cooking.countdown_number(self._now))
            self.draw_text(big, 830, 300, config.COLORS["accent"], self.font_large)
            self.draw_text("Countdown dimulai. Siapkan bahan pertama!", 650, 380, config.COLORS["muted"], self.font)
        elif self.cooking.phase in {"ingredient_timing", "final_cooking"}:
            remaining = self.cooking.seconds_until_target(self._now)
            if remaining >= 0:
                timer_text = f"{remaining:05.2f}s"
                timer_color = config.COLORS["green"]
            else:
                timer_text = f"+{abs(remaining):04.2f}s"
                timer_color = config.COLORS["red"]
            self.draw_text(timer_text, 740, 300, timer_color, self.font_large)
            if self.cooking.phase == "ingredient_timing":
                expected = self.cooking.expected_ingredient()
                ingredient = self.ingredients[expected["id"]]
                self.draw_text(f"Aksi berikutnya: masukkan {ingredient.name}", 650, 380,
                               config.COLORS["text"], self.font)
                action_label = "MASUKKAN BAHAN"
            else:
                self.draw_text("Waktunya mengambil makanan dari kompor.", 650, 380,
                               config.COLORS["text"], self.font)
                action_label = "AMBIL MAKANAN"
            self.button("cooking_action", action_label, pygame.Rect(730, 450, 360, 66), font=self.font_medium)
            if self.cooking.last_deviation is not None:
                self.draw_text(f"Selisih aksi sebelumnya: {self.cooking.last_deviation:.2f} detik",
                               700, 550, config.COLORS["muted"], self.font_small)
        elif self.cooking.phase == "finished":
            food = self.cooking.finished_food
            if food:
                quality_color = {"good": config.COLORS["green"], "mid": config.COLORS["accent"], "poor": config.COLORS["red"]}[food.quality]
                self.draw_text(food.quality.upper(), 830, 305, quality_color, self.font_large)
                price = EconomySystem.selling_price(food.base_price, food.difficulty, food.quality)
                self.draw_text(f"Perkiraan harga jual: {self.money(price)}", 700, 385,
                               config.COLORS["text"], self.font)
                self.draw_text("Masakan sudah masuk ke Inventory.", 700, 425,
                               config.COLORS["muted"], self.font_small)
            self.button("cooking_inventory", "Buka Inventory", pygame.Rect(680, 500, 180, 42))
            self.button("cooking_again", "Masak Lagi", pygame.Rect(880, 500, 180, 42), color=config.COLORS["blue"])
        else:
            enough, missing = self.inventory.has_ingredients(recipe)
            self.draw_text("Bahan yang dibutuhkan tersedia." if enough else "Bahan belum cukup.",
                           650, 310, config.COLORS["muted"], self.font)
            self.button("cooking_start", "START COOKING", pygame.Rect(730, 420, 360, 62), enabled=enough,
                        font=self.font_medium)
        self.draw_text(self.cooking.message, 610, 650, config.COLORS["muted"], self.font_small)
        self.button("cooking_back", "Kembali", pygame.Rect(55, 660, 130, 36), color=config.COLORS["blue"])

    def draw_inventory(self):
        self.page_title("Inventory", "Jual makanan yang sudah selesai dimasak. Penjualan dibatasi 5 makanan per hari.")
        self.panel(pygame.Rect(30, 195, 780, 535))
        self.panel(pygame.Rect(830, 195, 420, 535))
        self.draw_text(f"Makanan ({len(self.player.food_inventory)})", 52, 212, config.COLORS["text"], self.font_medium)
        self.draw_text("Stok bahan", 852, 212, config.COLORS["text"], self.font_medium)
        food_items = self.player.food_inventory
        start = self.inventory_scroll
        visible = food_items[start:start + 7]
        if not visible:
            self.draw_text("Belum ada makanan. Masak resep untuk mengisi inventori.", 55, 270,
                           config.COLORS["muted"], self.font_small)
        for index, food in enumerate(visible):
            y = 258 + index * 62
            self.panel(pygame.Rect(50, y, 740, 52), fill=config.COLORS["surface_light"], radius=8)
            self.draw_text(food.name, 64, y + 6, config.COLORS["text"], self.font_small)
            qcolor = {"good": config.COLORS["green"], "mid": config.COLORS["accent"], "poor": config.COLORS["red"]}[food.quality]
            self.draw_text(f"{food.quality.upper()} · {food.difficulty}", 64, y + 29, qcolor, self.font_small)
            price = EconomySystem.selling_price(food.base_price, food.difficulty, food.quality)
            self.draw_text(self.money(price), 500, y + 17, config.COLORS["muted"], self.font_small)
            self.button(f"sell_{food.instance_id}", "Sell", pygame.Rect(680, y + 10, 90, 32),
                        enabled=DaySystem.can_sell(self.player))
        if len(food_items) > 7:
            self.button("inventory_up", "▲", pygame.Rect(735, 208, 28, 28), enabled=start > 0, color=config.COLORS["blue"])
            self.button("inventory_down", "▼", pygame.Rect(770, 208, 28, 28),
                        enabled=start + 7 < len(food_items), color=config.COLORS["blue"])
        self.draw_text(f"Sisa kuota penjualan: {max(0, self.player.daily_sell_limit - self.player.daily_sales)}",
                       55, 710, config.COLORS["muted"], self.font_small)
        stock_items = [(key, qty) for key, qty in self.player.ingredient_stock.items() if qty > 0]
        visible_stock = stock_items[self.stock_scroll:self.stock_scroll + 13]
        if not stock_items:
            self.draw_text("Tidak ada bahan tersimpan.", 854, 260, config.COLORS["muted"], self.font_small)
        for index, (ingredient_id, quantity) in enumerate(visible_stock):
            ingredient = self.ingredients.get(ingredient_id)
            name = ingredient.name if ingredient else ingredient_id
            self.draw_text(f"{name}", 855, 258 + index * 32, config.COLORS["text"], self.font_small)
            self.draw_text(f"x{quantity}", 1185, 258 + index * 32, config.COLORS["accent"], self.font_small)
        if len(stock_items) > 13:
            self.button("stock_scroll_up", "▲", pygame.Rect(1178, 207, 30, 28), enabled=self.stock_scroll > 0, color=config.COLORS["blue"])
            self.button("stock_scroll_down", "▼", pygame.Rect(1213, 207, 30, 28),
                        enabled=self.stock_scroll + 13 < len(stock_items), color=config.COLORS["blue"])

    def draw_profile(self):
        self.page_title("Profile & Business", "Statistik keuangan toko dan progres permainan.")
        self.panel(pygame.Rect(30, 195, 590, 515))
        self.panel(pygame.Rect(650, 195, 600, 515))
        stats = [
            ("Saldo saat ini", self.money(self.player.money)),
            ("Total pendapatan", self.money(self.player.total_revenue)),
            ("Total biaya bahan", self.money(self.player.total_expenses)),
            ("Keuntungan bersih", self.money(self.player.net_profit)),
            ("Total makanan terjual", str(self.player.total_items_sold)),
            ("Hari berjalan", str(self.player.day)),
        ]
        for idx, (label, value) in enumerate(stats):
            y = 235 + idx * 62
            self.draw_text(label, 58, y, config.COLORS["muted"], self.font)
            self.draw_text(value, 340, y, config.COLORS["text"], self.font_medium)
        self.draw_text("Aturan bisnis", 680, 222, config.COLORS["text"], self.font_medium)
        rules = [
            "• Maksimal 5 makanan dijual setiap hari.",
            "• Harga jual = harga dasar × pengali kesulitan × pengali kualitas.",
            "• Belanja bahan tercatat sebagai biaya; penjualan tercatat sebagai pendapatan.",
            "• Akhiri hari untuk mengembalikan kuota penjualan menjadi 5.",
            "• Toko bangkrut jika saldo nol dan tidak ada stok bahan/makanan.",
        ]
        for idx, line in enumerate(rules):
            self.wrap_text(line, 680, 280 + idx * 65, 520, config.COLORS["muted"], self.font_small, 20, 3)
        self.button("profile_end_day", "Akhiri Hari", pygame.Rect(680, 610, 170, 42), color=config.COLORS["blue"])
        self.button("profile_save", "Simpan Sekarang", pygame.Rect(870, 610, 170, 42))

    # ---------- Input and actions ----------
    def current_time(self) -> float:
        return pygame.time.get_ticks() / 1000.0

    def set_message(self, message: str, is_error: bool = False):
        self.message = message
        self.message_color = config.COLORS["red"] if is_error else config.COLORS["muted"]

    def save_game(self):
        self.save_manager.save(self.player)

    def open_screen(self, screen_name: str):
        self.screen_name = screen_name
        if screen_name == state.INVENTORY:
            self.inventory_scroll = 0

    def start_selected_recipe(self):
        recipe = self.recipe_system.get(self.selected_recipe_id or "")
        if not recipe:
            self.set_message("Resep tidak ditemukan.", True)
            return
        enough, missing = self.inventory.has_ingredients(recipe)
        if not enough:
            self.set_message("Bahan tidak cukup: " + "; ".join(missing), True)
            return
        try:
            self.inventory.consume_recipe_ingredients(recipe)
            self.cooking.start(recipe, self.current_time())
            self.save_game()
            self.set_message(f"Memulai {recipe['name']}. Ikuti countdown!", False)
        except (ValueError, RuntimeError) as exc:
            self.set_message(str(exc), True)

    def sell_food(self, instance_id: str):
        food = self.inventory.find_food(instance_id)
        if not food:
            self.set_message("Makanan tidak ditemukan.", True)
            return
        if not DaySystem.can_sell(self.player):
            self.set_message("Kuota penjualan hari ini sudah habis. Akhiri hari untuk lanjut.", True)
            return
        price = EconomySystem.selling_price(food.base_price, food.difficulty, food.quality)
        DaySystem.register_sale(self.player)
        self.player.food_inventory.remove(food)
        self.player.money += price
        self.player.total_revenue += price
        self.save_game()
        self.set_message(f"{food.name} terjual seharga {self.money(price)}.")

    def handle_action(self, action: str):
        if action.startswith("nav_"):
            if self.screen_name == state.COOKING and self.cooking.phase not in {"idle", "finished"}:
                self.set_message("Selesaikan sesi memasak sebelum berpindah layar.", True)
                return
            self.open_screen(action[4:])
            return
        if action == "home_market":
            self.open_screen(state.MARKET)
        elif action == "home_recipes":
            self.open_screen(state.RECIPES)
        elif action == "end_day" or action == "profile_end_day":
            if self.cooking.phase not in {"idle", "finished"}:
                self.set_message("Selesaikan sesi memasak sebelum mengakhiri hari.", True)
            else:
                DaySystem.end_day(self.player)
                self.save_game()
                self.set_message(f"Hari baru dimulai. Sekarang Hari {self.player.day}.")
        elif action == "profile_save":
            self.save_game()
            self.set_message("Progres berhasil disimpan.")
        elif action == "cart_buy":
            success, message, _ = self.market.checkout(self.player)
            self.save_game() if success else None
            self.set_message(message, not success)
        elif action == "cart_clear":
            self.market.clear_cart()
            self.cart_scroll = 0
            self.set_message("Keranjang dikosongkan.")
        elif action == "market_scroll_up":
            self.market_scroll = max(0, self.market_scroll - 12)
        elif action == "market_scroll_down":
            self.market_scroll = min(max(0, len(self.ingredients) - 12), self.market_scroll + 12)
        elif action == "cart_scroll_up":
            self.cart_scroll = max(0, self.cart_scroll - 10)
        elif action == "cart_scroll_down":
            self.cart_scroll = min(max(0, len(self.market.cart) - 10), self.cart_scroll + 10)
        elif action == "recipe_scroll_up":
            self.recipe_scroll = max(0, self.recipe_scroll - 6)
        elif action == "recipe_scroll_down":
            self.recipe_scroll = min(max(0, len(self.recipe_system.all()) - 6), self.recipe_scroll + 6)
        elif action == "stock_scroll_up":
            self.stock_scroll = max(0, self.stock_scroll - 13)
        elif action == "stock_scroll_down":
            stock_count = sum(1 for qty in self.player.ingredient_stock.values() if qty > 0)
            self.stock_scroll = min(max(0, stock_count - 13), self.stock_scroll + 13)
        elif action.startswith("market_plus_"):
            key = action[len("market_plus_"):]
            self.market_quantities[key] += 1
        elif action.startswith("market_minus_"):
            key = action[len("market_minus_"):]
            self.market_quantities[key] = max(1, self.market_quantities[key] - 1)
        elif action.startswith("market_add_"):
            key = action[len("market_add_"):]
            self.market.add_to_cart(key, self.market_quantities[key])
            self.set_message(f"{self.ingredients[key].name} ditambahkan ke keranjang.")
        elif action.startswith("cart_remove_"):
            key = action[len("cart_remove_"):]
            self.market.change_cart_quantity(key, -1)
        elif action.startswith("recipe_cook_"):
            self.selected_recipe_id = action[len("recipe_cook_"):]
            self.cooking.reset()
            self.open_screen(state.COOKING)
        elif action == "cooking_start":
            self.start_selected_recipe()
        elif action == "cooking_action":
            food = self.cooking.submit_action(self.current_time())
            if food:
                self.inventory.add_food(food)
                self.save_game()
                self.set_message(f"{food.name} selesai: {food.quality.upper()}.")
            else:
                self.set_message(self.cooking.message)
        elif action == "cooking_back":
            if self.cooking.phase in {"idle", "finished"}:
                self.open_screen(state.RECIPES)
            else:
                self.set_message("Selesaikan sesi memasak sebelum kembali ke Recipe Book.", True)
        elif action == "cooking_inventory":
            self.open_screen(state.INVENTORY)
        elif action == "cooking_again":
            self.cooking.reset()
            self.open_screen(state.COOKING)
        elif action == "inventory_up":
            self.inventory_scroll = max(0, self.inventory_scroll - 1)
        elif action == "inventory_down":
            self.inventory_scroll = min(max(0, len(self.player.food_inventory) - 7), self.inventory_scroll + 1)
        elif action.startswith("sell_"):
            self.sell_food(action[len("sell_"):])

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.screen_name == state.COOKING:
                if self.cooking.phase in {"idle", "finished"}:
                    self.open_screen(state.RECIPES)
                else:
                    self.set_message("Selesaikan sesi memasak sebelum kembali.", True)
            else:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for action, rect in reversed(list(self.buttons.items())):
                if rect.collidepoint(event.pos):
                    self.handle_action(action)
                    break
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, _ = pygame.mouse.get_pos()
            if self.screen_name == state.INVENTORY:
                if mouse_x < 810:
                    self.inventory_scroll = max(0, min(max(0, len(self.player.food_inventory) - 7), self.inventory_scroll - event.y))
                else:
                    stock_count = sum(1 for qty in self.player.ingredient_stock.values() if qty > 0)
                    self.stock_scroll = max(0, min(max(0, stock_count - 13), self.stock_scroll - event.y))
            elif self.screen_name == state.MARKET:
                if mouse_x < 820:
                    self.market_scroll = max(0, min(max(0, len(self.ingredients) - 12), self.market_scroll - event.y))
                else:
                    self.cart_scroll = max(0, min(max(0, len(self.market.cart) - 10), self.cart_scroll - event.y))
            elif self.screen_name == state.RECIPES:
                self.recipe_scroll = max(0, min(max(0, len(self.recipe_system.all()) - 6), self.recipe_scroll - event.y * 2))

    def draw(self):
        self.screen.fill(config.COLORS["background"])
        self.buttons.clear()
        self.header()
        if self.screen_name == state.HOME:
            self.draw_home()
        elif self.screen_name == state.MARKET:
            self.draw_market()
        elif self.screen_name == state.RECIPES:
            self.draw_recipes()
        elif self.screen_name == state.COOKING:
            self.draw_cooking()
        elif self.screen_name == state.INVENTORY:
            self.draw_inventory()
        elif self.screen_name == state.PROFILE:
            self.draw_profile()
        self.draw_message()
        pygame.display.flip()

    def run(self):
        while self.running:
            self._now = self.current_time()
            self.cooking.update(self._now)
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            self.clock.tick(config.FPS)
        self.save_game()
        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
