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
        # Font tema: letakkan Fraunces-SemiBold.ttf dan NunitoSans-Regular.ttf
        # di assets/fonts/. Pygame default hanya dipakai sebagai fallback jika aset belum ada.
        self.font_display = self.load_font("Fraunces-SemiBold.ttf", 36)
        self.font_display_small = self.load_font("Fraunces-SemiBold.ttf", 27)
        self.font = self.load_font("NunitoSans-Regular.ttf", 18)
        self.font_small = self.load_font("NunitoSans-Regular.ttf", 15)
        self.font_medium = self.load_font("NunitoSans-Bold.ttf", 22)
        self.font_large = self.load_font("Fraunces-SemiBold.ttf", 46)

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
    def load_font(self, filename: str, size: int):
        """Load a project font from assets/fonts; use Pygame's bundled fallback if absent."""
        path = ROOT / config.ASSET_DIR / "fonts" / filename
        if path.exists():
            try:
                return pygame.font.Font(str(path), size)
            except pygame.error:
                pass
        if not getattr(self, "_font_fallback_warned", False):
            print(
                "[UI] Font tema belum lengkap. Tambahkan Fraunces-SemiBold.ttf, "
                "NunitoSans-Regular.ttf, dan NunitoSans-Bold.ttf ke assets/fonts/."
            )
            self._font_fallback_warned = True
        return pygame.font.Font(None, size)

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


    def panel(self, rect: pygame.Rect, fill=None, border=None, radius=12):
        """Panel kertas hangat dengan garis tepi tipis, tanpa shadow berat."""
        fill = config.COLORS["surface"] if fill is None else fill
        border = config.COLORS["border"] if border is None else border
        pygame.draw.rect(self.screen, fill, rect, border_radius=radius)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=radius)
        if rect.width > 34 and rect.height > 14:
            pygame.draw.line(
                self.screen, config.COLORS["mustard"],
                (rect.x + 13, rect.y + 5), (rect.right - 13, rect.y + 5), 2
            )

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
        """Tombol bergaya label kayu/kertas; action ID tetap sama dengan versi lama."""
        if enabled:
            self.buttons[button_id] = rect
        else:
            self.buttons.pop(button_id, None)
        fill = config.COLORS["accent"] if color is None else color
        if not enabled:
            fill = config.COLORS["surface_light"]
        elif pygame.Rect(rect).collidepoint(pygame.mouse.get_pos()):
            fill = tuple(min(255, channel + 12) for channel in fill)
        pygame.draw.rect(self.screen, fill, rect, border_radius=9)
        pygame.draw.rect(self.screen, config.COLORS["border_dark"], rect, 1, border_radius=9)
        text_color = config.COLORS["surface"] if enabled else config.COLORS["muted"]
        text_surface = (font or self.font_small).render(label, True, text_color)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))


    def nav_button(self, key: str, label: str, y: int, active: bool):
        rect = pygame.Rect(16, y, 180, 43)
        self.buttons[f"nav_{key}"] = rect
        fill = config.COLORS["accent"] if active else config.COLORS["nav"]
        pygame.draw.rect(self.screen, fill, rect, border_radius=9)
        if active:
            pygame.draw.rect(self.screen, config.COLORS["mustard"],
                             pygame.Rect(rect.x, rect.y + 7, 4, rect.height - 14), border_radius=2)
        marker_color = config.COLORS["mustard"] if active else config.COLORS["sage"]
        pygame.draw.circle(self.screen, marker_color, (rect.x + 23, rect.centery), 4)
        surface = self.font_medium.render(label, True, config.COLORS["surface"])
        self.screen.blit(surface, surface.get_rect(midleft=(rect.x + 42, rect.centery)))


    def header(self):
        """Sidebar navigasi + top bar dengan identitas rustic Cooking TXT."""
        # Sidebar teal seperti papan menu restoran.
        pygame.draw.rect(self.screen, config.COLORS["nav_dark"], (0, 0, 212, config.WINDOW_HEIGHT))
        pygame.draw.rect(self.screen, config.COLORS["nav"], (0, 0, 212, 145))
        pygame.draw.line(self.screen, config.COLORS["mustard"], (20, 139), (192, 139), 2)
        self.draw_text("COOKING", 25, 27, config.COLORS["surface"], self.font_display_small)
        self.draw_text("TXT", 27, 69, config.COLORS["mustard"], self.font_medium)
        self.draw_text("RESTAURANT JOURNAL", 27, 111, config.COLORS["surface_light"], self.font_small)

        nav_items = [
            ("home", "Beranda"), ("market", "Market"), ("recipes", "Buku Resep"),
            ("inventory", "Inventori"), ("profile", "Profil Bisnis"),
        ]
        for index, (key, label) in enumerate(nav_items):
            self.nav_button(key, label, 170 + index * 54, self.screen_name == key)

        pygame.draw.line(self.screen, config.COLORS["sage"], (22, 475), (190, 475), 1)
        self.draw_text("DAPUR KECIL,", 25, 505, config.COLORS["surface_light"], self.font_small)
        self.draw_text("MIMPI BESAR.", 25, 528, config.COLORS["mustard"], self.font_medium)
        self.draw_text("COOK  •  SELL  •  GROW", 25, 744, config.COLORS["surface_light"], self.font_small)

        # Top bar parchment.
        pygame.draw.rect(self.screen, config.COLORS["surface"], (212, 0, config.WINDOW_WIDTH - 212, 88))
        pygame.draw.line(self.screen, config.COLORS["border"], (212, 87), (config.WINDOW_WIDTH, 87), 1)
        self.draw_text("Cooking TXT", 242, 17, config.COLORS["text"], self.font_display_small)
        self.draw_text("RESTAURANT MANAGEMENT", 245, 54, config.COLORS["muted"], self.font_small)

        day_rect = pygame.Rect(875, 22, 116, 42)
        money_rect = pygame.Rect(1004, 22, 248, 42)
        pygame.draw.rect(self.screen, config.COLORS["paper_alt"], day_rect, border_radius=8)
        pygame.draw.rect(self.screen, config.COLORS["border"], day_rect, 1, border_radius=8)
        pygame.draw.rect(self.screen, config.COLORS["paper_alt"], money_rect, border_radius=8)
        pygame.draw.rect(self.screen, config.COLORS["border"], money_rect, 1, border_radius=8)
        self.draw_text(f"HARI {self.player.day}", day_rect.x + 13, day_rect.y + 12,
                       config.COLORS["teal"], self.font_medium)
        pygame.draw.circle(self.screen, config.COLORS["mustard"], (money_rect.x + 22, money_rect.centery), 8)
        self.draw_text(self.money(self.player.money), money_rect.x + 40, money_rect.y + 10,
                       config.COLORS["text"], self.font_medium)
        self.draw_text(f"Terjual {self.player.daily_sales}/{self.player.daily_sell_limit}",
                       1090, 65, config.COLORS["muted"], self.font_small)

    @staticmethod
    def money(value: int) -> str:
        return f"Rp {value:,}".replace(",", ".")


    def page_title(self, title: str, subtitle: str):
        self.draw_text(title, 242, 108, config.COLORS["text"], self.font_display)
        self.draw_text(subtitle, 245, 153, config.COLORS["muted"], self.font_small)
        pygame.draw.line(self.screen, config.COLORS["border"], (242, 181), (1255, 181), 1)


    def draw_message(self):
        if self.message:
            rect = pygame.Rect(235, 757, 1020, 28)
            color = config.COLORS["paper_alt"]
            pygame.draw.rect(self.screen, color, rect, border_radius=7)
            pygame.draw.rect(self.screen, config.COLORS["border"], rect, 1, border_radius=7)
            dot_color = self.message_color
            pygame.draw.circle(self.screen, dot_color, (rect.x + 15, rect.centery), 4)
            self.draw_text(self.message, rect.x + 29, rect.y + 6,
                           self.message_color, self.font_small)


    def draw_home(self):
        self.page_title("Beranda", "Ringkasan restoran dan langkah untuk memulai operasional hari ini.")
        metrics = [
            ("Saldo kas", self.money(self.player.money), config.COLORS["teal"]),
            ("Keuntungan bersih", self.money(self.player.net_profit), config.COLORS["accent"]),
            ("Makanan terjual", str(self.player.total_items_sold), config.COLORS["blue"]),
            ("Stok masakan", str(len(self.player.food_inventory)), config.COLORS["sage"]),
        ]
        for index, (label, value, color) in enumerate(metrics):
            x = 242 + index * 254
            rect = pygame.Rect(x, 202, 242, 104)
            self.panel(rect)
            pygame.draw.rect(self.screen, color, pygame.Rect(x + 15, 222, 4, 54), border_radius=2)
            self.draw_text(label, x + 30, 218, config.COLORS["muted"], self.font_small)
            self.draw_text(value, x + 30, 248, config.COLORS["text"], self.font_medium)

        left = pygame.Rect(242, 328, 625, 405)
        right = pygame.Rect(885, 328, 370, 405)
        self.panel(left)
        self.panel(right)
        self.draw_text("Ritme hari ini", left.x + 22, left.y + 22,
                       config.COLORS["text"], self.font_display_small)
        self.draw_text("Empat langkah sederhana untuk menjaga restoran tetap berjalan.",
                       left.x + 24, left.y + 61, config.COLORS["muted"], self.font_small)
        steps = [
            ("01", "Belanja bahan", "Pilih stok yang dibutuhkan di Market."),
            ("02", "Pilih resep", "Periksa bahan dan tingkat kesulitan."),
            ("03", "Masak dengan teliti", "Ikuti timing untuk hasil terbaik."),
            ("04", "Jual hasil masakan", "Maksimalkan kuota penjualan harian."),
        ]
        for i, (number, title, detail) in enumerate(steps):
            y = left.y + 118 + i * 61
            pygame.draw.circle(self.screen, config.COLORS["mustard"], (left.x + 39, y + 13), 16)
            num = self.font_small.render(number, True, config.COLORS["text"])
            self.screen.blit(num, num.get_rect(center=(left.x + 39, y + 13)))
            self.draw_text(title, left.x + 68, y - 2, config.COLORS["text"], self.font_medium)
            self.draw_text(detail, left.x + 68, y + 25, config.COLORS["muted"], self.font_small)
        self.button("home_market", "Belanja bahan", pygame.Rect(left.x + 24, left.bottom - 55, 155, 37))
        self.button("home_recipes", "Buka buku resep", pygame.Rect(left.x + 191, left.bottom - 55, 175, 37),
                    color=config.COLORS["blue"])

        self.draw_text("Catatan operasional", right.x + 22, right.y + 22,
                       config.COLORS["text"], self.font_display_small)
        rows = [
            ("Hari berjalan", f"Hari {self.player.day}"),
            ("Penjualan hari ini", f"{self.player.daily_sales}/{self.player.daily_sell_limit}"),
            ("Pendapatan", self.money(self.player.total_revenue)),
            ("Belanja bahan", self.money(self.player.total_expenses)),
        ]
        for i, (label, value) in enumerate(rows):
            y = right.y + 86 + i * 49
            self.draw_text(label, right.x + 22, y, config.COLORS["muted"], self.font_small)
            val = self.font_medium.render(value, True, config.COLORS["text"])
            self.screen.blit(val, val.get_rect(topright=(right.right - 22, y - 2)))
        bar_rect = pygame.Rect(right.x + 22, right.y + 300, right.width - 44, 12)
        pygame.draw.rect(self.screen, config.COLORS["paper_alt"], bar_rect, border_radius=6)
        ratio = min(1.0, self.player.daily_sales / max(1, self.player.daily_sell_limit))
        pygame.draw.rect(self.screen, config.COLORS["sage"],
                         pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * ratio), bar_rect.height),
                         border_radius=6)
        self.draw_text("Kuota penjualan harian", right.x + 22, right.y + 275,
                       config.COLORS["muted"], self.font_small)
        self.button("end_day", "Akhiri Hari", pygame.Rect(right.x + 22, right.bottom - 55, 150, 37),
                    color=config.COLORS["teal"])
        if EconomySystem.is_bankrupt(self.player):
            self.draw_text("TOKO BANGKRUT", right.x + 190, right.bottom - 50,
                           config.COLORS["accent"], self.font_medium)


    def draw_market(self):
        self.page_title("Market", "Belanja bahan segar untuk menyiapkan menu restoran.")
        left = pygame.Rect(242, 202, 642, 535)
        right = pygame.Rect(902, 202, 353, 535)
        self.panel(left)
        self.panel(right)
        self.draw_text("Bahan tersedia", left.x + 18, left.y + 18,
                       config.COLORS["text"], self.font_display_small)
        self.draw_text(f"{len(self.ingredients)} jenis bahan", left.x + 20, left.y + 54,
                       config.COLORS["muted"], self.font_small)
        item_list = list(self.ingredients.values())
        visible_items = item_list[self.market_scroll:self.market_scroll + 12]
        for index, ingredient in enumerate(visible_items):
            col, row = index // 6, index % 6
            x = left.x + 13 + col * 310
            y = left.y + 91 + row * 72
            card = pygame.Rect(x, y, 296, 64)
            self.panel(card, fill=config.COLORS["paper_alt"], radius=8)
            self.draw_optional_image(ingredient.image, pygame.Rect(x + 8, y + 11, 42, 42), ingredient.name)
            self.draw_text(ingredient.name, x + 57, y + 8, config.COLORS["text"], self.font_small)
            self.draw_text(self.money(ingredient.market_price), x + 57, y + 34,
                           config.COLORS["muted"], self.font_small)
            qty = self.market_quantities[ingredient.id]
            self.button(f"market_minus_{ingredient.id}", "−", pygame.Rect(x + 164, y + 19, 22, 26), color=config.COLORS["teal"])
            qsurf = self.font_small.render(str(qty), True, config.COLORS["text"])
            self.screen.blit(qsurf, qsurf.get_rect(center=(x + 199, y + 32)))
            self.button(f"market_plus_{ingredient.id}", "+", pygame.Rect(x + 212, y + 19, 22, 26), color=config.COLORS["teal"])
            self.button(f"market_add_{ingredient.id}", "Add", pygame.Rect(x + 240, y + 19, 48, 26),
                        color=config.COLORS["accent"])
        if len(item_list) > 12:
            self.button("market_scroll_up", "▲", pygame.Rect(left.right - 75, left.y + 18, 27, 26),
                        enabled=self.market_scroll > 0, color=config.COLORS["teal"])
            self.button("market_scroll_down", "▼", pygame.Rect(left.right - 43, left.y + 18, 27, 26),
                        enabled=self.market_scroll + 12 < len(item_list), color=config.COLORS["teal"])

        self.draw_text("Keranjang belanja", right.x + 19, right.y + 18,
                       config.COLORS["text"], self.font_display_small)
        cart_items = list(self.market.cart.items())
        visible_cart = cart_items[self.cart_scroll:self.cart_scroll + 9]
        if not cart_items:
            self.draw_text("Keranjang masih kosong.", right.x + 20, right.y + 92,
                           config.COLORS["muted"], self.font_small)
            self.draw_text("Tambahkan bahan dari katalog di sebelah kiri.", right.x + 20, right.y + 119,
                           config.COLORS["muted"], self.font_small)
        else:
            for index, (ingredient_id, quantity) in enumerate(visible_cart):
                ingredient = self.ingredients[ingredient_id]
                y = right.y + 83 + index * 37
                self.draw_text(ingredient.name, right.x + 20, y, config.COLORS["text"], self.font_small)
                self.draw_text(f"×{quantity}", right.x + 205, y,
                               config.COLORS["muted"], self.font_small)
                price = self.font_small.render(self.money(ingredient.market_price * quantity), True,
                                               config.COLORS["text"])
                self.screen.blit(price, price.get_rect(topright=(right.right - 53, y)))
                self.button(f"cart_remove_{ingredient_id}", "−1",
                            pygame.Rect(right.right - 43, y - 4, 32, 25), color=config.COLORS["teal"])
        if len(cart_items) > 9:
            self.button("cart_scroll_up", "▲", pygame.Rect(right.right - 78, right.y + 17, 27, 26),
                        enabled=self.cart_scroll > 0, color=config.COLORS["teal"])
            self.button("cart_scroll_down", "▼", pygame.Rect(right.right - 45, right.y + 17, 27, 26),
                        enabled=self.cart_scroll + 9 < len(cart_items), color=config.COLORS["teal"])
        pygame.draw.line(self.screen, config.COLORS["border"],
                         (right.x + 18, right.y + 430), (right.right - 18, right.y + 430), 1)
        self.draw_text("Total belanja", right.x + 20, right.y + 447,
                       config.COLORS["muted"], self.font_small)
        self.draw_text(self.money(self.market.cart_total()), right.x + 20, right.y + 472,
                       config.COLORS["text"], self.font_display_small)
        self.button("cart_buy", "Beli bahan", pygame.Rect(right.x + 18, right.bottom - 51, 150, 34),
                    enabled=bool(self.market.cart), color=config.COLORS["accent"])
        self.button("cart_clear", "Kosongkan", pygame.Rect(right.x + 179, right.bottom - 51, 155, 34),
                    enabled=bool(self.market.cart), color=config.COLORS["teal"])

    def _ingredient_summary(self, recipe: dict) -> str:
        parts = []
        for step in recipe["ingredients"]:
            ingredient = self.ingredients[step["id"]]
            quantity = int(step.get("quantity", 1))
            parts.append(f"{ingredient.name} x{quantity} ({step['timing']}s)")
        return "  •  ".join(parts)


    def draw_recipes(self):
        self.page_title("Buku Resep", "Pilih hidangan, periksa bahan, lalu mulai memasak.")
        recipes = self.recipe_system.all()
        visible_recipes = recipes[self.recipe_scroll:self.recipe_scroll + 6]
        for index, recipe in enumerate(visible_recipes):
            col, row = index % 2, index // 2
            x = 242 + col * 509
            y = 202 + row * 174
            rect = pygame.Rect(x, y, 495, 160)
            self.panel(rect)
            img_rect = pygame.Rect(x + 15, y + 43, 82, 82)
            self.draw_optional_image(recipe.get("image", ""), img_rect, recipe["name"])
            self.draw_text(recipe["name"], x + 112, y + 14,
                           config.COLORS["text"], self.font_display_small)
            difficulty = recipe["difficulty"].upper()
            difficulty_color = {
                "easy": config.COLORS["sage"],
                "normal": config.COLORS["mustard"],
                "hard": config.COLORS["accent"],
            }.get(recipe["difficulty"], config.COLORS["teal"])
            badge = pygame.Rect(x + 112, y + 51, max(70, self.font_small.size(difficulty)[0] + 20), 23)
            pygame.draw.rect(self.screen, difficulty_color, badge, border_radius=7)
            label = self.font_small.render(difficulty, True, config.COLORS["surface"])
            self.screen.blit(label, label.get_rect(center=badge.center))
            self.draw_text(f"Matang {recipe['cooking_time']} detik  ·  Dasar {self.money(int(recipe['base_price']))}",
                           x + 112, y + 82, config.COLORS["muted"], self.font_small)
            self.wrap_text(self._ingredient_summary(recipe), x + 112, y + 108, 250,
                           config.COLORS["muted"], self.font_small, line_height=17, max_lines=2)
            enough, missing = self.inventory.has_ingredients(recipe)
            self.button(f"recipe_cook_{recipe['id']}", "Masak",
                        pygame.Rect(x + 380, y + 108, 98, 34), enabled=enough,
                        color=config.COLORS["accent"])
            if not enough:
                self.draw_text("Bahan kurang", x + 380, y + 88,
                               config.COLORS["accent_dark"], self.font_small)
        if len(recipes) > 6:
            self.button("recipe_scroll_up", "▲", pygame.Rect(1186, 151, 28, 26),
                        enabled=self.recipe_scroll > 0, color=config.COLORS["teal"])
            self.button("recipe_scroll_down", "▼", pygame.Rect(1219, 151, 28, 26),
                        enabled=self.recipe_scroll + 6 < len(recipes), color=config.COLORS["teal"])
        if not recipes:
            self.panel(pygame.Rect(242, 202, 1013, 210))
            self.draw_text("Belum ada resep valid.", 270, 245, config.COLORS["text"], self.font_display_small)
            self.draw_text("Periksa data/recipes dan pastikan ID bahan tersedia.", 270, 292,
                           config.COLORS["muted"], self.font_small)
        if self.recipe_system.errors:
            self.draw_text(f"Peringatan: {len(self.recipe_system.errors)} file resep dilewati.",
                           245, 721, config.COLORS["accent_dark"], self.font_small)


    def draw_cooking(self):
        recipe = self.recipe_system.get(self.selected_recipe_id or "")
        self.page_title("Cooking Station", "Jaga ritme memasak: masukkan bahan dan angkat hidangan pada waktu yang tepat.")
        if not recipe:
            self.panel(pygame.Rect(242, 202, 1013, 250))
            self.draw_text("Resep tidak ditemukan.", 270, 245, config.COLORS["text"], self.font_display_small)
            self.button("cooking_back", "Kembali ke resep", pygame.Rect(270, 315, 190, 40), color=config.COLORS["teal"])
            return

        left = pygame.Rect(242, 202, 385, 535)
        right = pygame.Rect(645, 202, 610, 535)
        self.panel(left)
        self.panel(right)
        self.draw_optional_image(recipe.get("image", ""), pygame.Rect(left.x + 20, left.y + 58, 94, 94), recipe["name"])
        self.draw_text(recipe["name"], left.x + 130, left.y + 62,
                       config.COLORS["text"], self.font_display_small)
        self.draw_text(f"{recipe['difficulty'].upper()}  ·  {recipe['cooking_time']} detik akhir",
                       left.x + 132, left.y + 105, config.COLORS["muted"], self.font_small)
        self.draw_text("Urutan bahan", left.x + 22, left.y + 180,
                       config.COLORS["text"], self.font_medium)
        for index, step in enumerate(recipe["ingredients"]):
            ingredient = self.ingredients[step["id"]]
            done = self.cooking.step_index > index or self.cooking.phase in {"final_cooking", "finished"}
            current = self.cooking.phase == "ingredient_timing" and self.cooking.step_index == index
            y = left.y + 224 + index * 48
            fill = config.COLORS["paper_alt"] if current else config.COLORS["surface"]
            row_rect = pygame.Rect(left.x + 16, y, left.width - 32, 40)
            pygame.draw.rect(self.screen, fill, row_rect, border_radius=8)
            pygame.draw.rect(self.screen, config.COLORS["border"], row_rect, 1, border_radius=8)
            marker = config.COLORS["sage"] if done else (config.COLORS["accent"] if current else config.COLORS["border_dark"])
            pygame.draw.circle(self.screen, marker, (row_rect.x + 19, row_rect.centery), 7)
            self.draw_text(f"{ingredient.name} ×{step.get('quantity', 1)}",
                           row_rect.x + 36, row_rect.y + 10, config.COLORS["text"], self.font_small)
            t = self.font_small.render(f"+{step['timing']}s", True, config.COLORS["muted"])
            self.screen.blit(t, t.get_rect(topright=(row_rect.right - 12, row_rect.y + 11)))
        self.draw_text(f"Waktu memasak akhir: {recipe['cooking_time']} detik",
                       left.x + 20, left.bottom - 65, config.COLORS["muted"], self.font_small)
        self.button("cooking_back", "Kembali", pygame.Rect(left.x + 20, left.bottom - 48, 115, 32),
                    color=config.COLORS["teal"])

        phase_label = {
            "idle": "SIAP MEMASAK", "countdown": "BERSIAP", "ingredient_timing": "MASUKKAN BAHAN",
            "final_cooking": "PROSES MEMASAK", "finished": "HIDANGAN SELESAI",
        }.get(self.cooking.phase, self.cooking.phase.upper())
        self.draw_text("Area memasak", right.x + 24, right.y + 22,
                       config.COLORS["text"], self.font_display_small)
        phase_rect = pygame.Rect(right.right - 205, right.y + 20, 178, 28)
        pygame.draw.rect(self.screen, config.COLORS["paper_alt"], phase_rect, border_radius=8)
        phase_surface = self.font_small.render(phase_label, True, config.COLORS["teal"])
        self.screen.blit(phase_surface, phase_surface.get_rect(center=phase_rect.center))
        pygame.draw.line(self.screen, config.COLORS["border"],
                         (right.x + 22, right.y + 66), (right.right - 22, right.y + 66), 1)

        if self.cooking.phase == "countdown":
            big = str(self.cooking.countdown_number(self._now))
            number = self.font_large.render(big, True, config.COLORS["accent"])
            self.screen.blit(number, number.get_rect(center=(right.centerx, right.y + 210)))
            self.draw_text("Tarik napas, siapkan bahan pertama.", right.x + 150, right.y + 272,
                           config.COLORS["muted"], self.font)
        elif self.cooking.phase in {"ingredient_timing", "final_cooking"}:
            remaining = self.cooking.seconds_until_target(self._now)
            timer_text = f"{remaining:05.2f}s" if remaining >= 0 else f"+{abs(remaining):04.2f}s"
            timer_color = config.COLORS["sage"] if remaining >= 0 else config.COLORS["accent"]
            timer = self.font_large.render(timer_text, True, timer_color)
            self.screen.blit(timer, timer.get_rect(center=(right.centerx, right.y + 200)))
            if self.cooking.phase == "ingredient_timing":
                expected = self.cooking.expected_ingredient()
                ingredient = self.ingredients[expected["id"]]
                instruction = f"Masukkan {ingredient.name} ×{expected.get('quantity', 1)}"
                action_label = "MASUKKAN BAHAN"
            else:
                instruction = "Saatnya mengangkat hidangan dari kompor."
                action_label = "AMBIL HIDANGAN"
            instruction_surface = self.font_medium.render(instruction, True, config.COLORS["text"])
            self.screen.blit(instruction_surface, instruction_surface.get_rect(center=(right.centerx, right.y + 275)))
            progress_rect = pygame.Rect(right.x + 95, right.y + 318, right.width - 190, 12)
            pygame.draw.rect(self.screen, config.COLORS["paper_alt"], progress_rect, border_radius=6)
            if self.cooking.phase == "ingredient_timing":
                ratio = min(1.0, self.cooking.step_index / max(1, len(recipe["ingredients"])))
            else:
                ratio = 0.92
            pygame.draw.rect(self.screen, config.COLORS["sage"],
                             pygame.Rect(progress_rect.x, progress_rect.y,
                                         int(progress_rect.width * ratio), progress_rect.height), border_radius=6)
            self.button("cooking_action", action_label,
                        pygame.Rect(right.x + 125, right.y + 365, right.width - 250, 54),
                        font=self.font_medium)
            if self.cooking.last_deviation is not None:
                deviation = f"Selisih aksi sebelumnya: {self.cooking.last_deviation:.2f} detik"
                label = self.font_small.render(deviation, True, config.COLORS["muted"])
                self.screen.blit(label, label.get_rect(center=(right.centerx, right.y + 450)))
        elif self.cooking.phase == "finished":
            food = self.cooking.finished_food
            if food:
                quality_color = {
                    "good": config.COLORS["sage"], "mid": config.COLORS["mustard"],
                    "poor": config.COLORS["accent"],
                }[food.quality]
                quality = self.font_large.render(food.quality.upper(), True, quality_color)
                self.screen.blit(quality, quality.get_rect(center=(right.centerx, right.y + 190)))
                price = EconomySystem.selling_price(food.base_price, food.difficulty, food.quality)
                price_label = self.font_medium.render(f"Perkiraan harga jual: {self.money(price)}",
                                                      True, config.COLORS["text"])
                self.screen.blit(price_label, price_label.get_rect(center=(right.centerx, right.y + 260)))
                self.draw_text("Hidangan sudah masuk ke Inventori.", right.x + 180, right.y + 300,
                               config.COLORS["muted"], self.font_small)
            self.button("cooking_inventory", "Buka Inventori",
                        pygame.Rect(right.x + 125, right.y + 365, 175, 42), color=config.COLORS["teal"])
            self.button("cooking_again", "Masak Lagi",
                        pygame.Rect(right.x + 315, right.y + 365, 155, 42), color=config.COLORS["accent"])
        else:
            enough, missing = self.inventory.has_ingredients(recipe)
            headline = "Bahan siap digunakan." if enough else "Periksa stok bahan sebelum mulai."
            text = self.font_medium.render(headline, True, config.COLORS["text"])
            self.screen.blit(text, text.get_rect(center=(right.centerx, right.y + 220)))
            self.draw_text("Kualitas hasil ditentukan oleh ketepatan setiap aksi.",
                           right.x + 125, right.y + 266, config.COLORS["muted"], self.font_small)
            self.button("cooking_start", "MULAI MEMASAK",
                        pygame.Rect(right.x + 145, right.y + 345, right.width - 290, 58),
                        enabled=enough, font=self.font_medium)
        self.draw_text(self.cooking.message, right.x + 24, right.bottom - 35,
                       config.COLORS["muted"], self.font_small)


    def draw_inventory(self):
        self.page_title("Inventori", "Kelola hasil masakan dan pantau bahan yang masih tersimpan.")
        food_panel = pygame.Rect(242, 202, 640, 535)
        stock_panel = pygame.Rect(900, 202, 355, 535)
        self.panel(food_panel)
        self.panel(stock_panel)
        self.draw_text(f"Makanan jadi · {len(self.player.food_inventory)}",
                       food_panel.x + 20, food_panel.y + 18, config.COLORS["text"], self.font_display_small)
        self.draw_text("Stok bahan mentah", stock_panel.x + 20, stock_panel.y + 18,
                       config.COLORS["text"], self.font_display_small)
        food_items = self.player.food_inventory
        visible = food_items[self.inventory_scroll:self.inventory_scroll + 7]
        if not visible:
            self.draw_text("Belum ada makanan.", food_panel.x + 24, food_panel.y + 100,
                           config.COLORS["text"], self.font_medium)
            self.draw_text("Masak resep terlebih dahulu untuk mengisi inventori.",
                           food_panel.x + 24, food_panel.y + 133, config.COLORS["muted"], self.font_small)
        for index, food in enumerate(visible):
            y = food_panel.y + 72 + index * 62
            row = pygame.Rect(food_panel.x + 14, y, food_panel.width - 28, 54)
            self.panel(row, fill=config.COLORS["paper_alt"], radius=8)
            self.draw_optional_image(food.image, pygame.Rect(row.x + 7, row.y + 6, 42, 42), food.name)
            self.draw_text(food.name, row.x + 59, row.y + 7, config.COLORS["text"], self.font_medium)
            quality_color = {
                "good": config.COLORS["sage"], "mid": config.COLORS["mustard"],
                "poor": config.COLORS["accent"],
            }.get(food.quality, config.COLORS["muted"])
            self.draw_text(f"{food.quality.upper()}  ·  {food.difficulty.upper()}",
                           row.x + 60, row.y + 32, quality_color, self.font_small)
            price = EconomySystem.selling_price(food.base_price, food.difficulty, food.quality)
            p = self.font_small.render(self.money(price), True, config.COLORS["text"])
            self.screen.blit(p, p.get_rect(midright=(row.right - 112, row.centery)))
            self.button(f"sell_{food.instance_id}", "Jual",
                        pygame.Rect(row.right - 95, row.y + 11, 82, 32),
                        enabled=DaySystem.can_sell(self.player), color=config.COLORS["accent"])
        if len(food_items) > 7:
            self.button("inventory_up", "▲", pygame.Rect(food_panel.right - 76, food_panel.y + 18, 27, 26),
                        enabled=self.inventory_scroll > 0, color=config.COLORS["teal"])
            self.button("inventory_down", "▼", pygame.Rect(food_panel.right - 44, food_panel.y + 18, 27, 26),
                        enabled=self.inventory_scroll + 7 < len(food_items), color=config.COLORS["teal"])
        remaining = max(0, self.player.daily_sell_limit - self.player.daily_sales)
        self.draw_text(f"Kuota penjualan tersisa: {remaining} dari {self.player.daily_sell_limit}",
                       food_panel.x + 20, food_panel.bottom - 34, config.COLORS["muted"], self.font_small)

        stock_items = [(key, qty) for key, qty in self.player.ingredient_stock.items() if qty > 0]
        visible_stock = stock_items[self.stock_scroll:self.stock_scroll + 13]
        if not stock_items:
            self.draw_text("Belum ada stok bahan.", stock_panel.x + 20, stock_panel.y + 95,
                           config.COLORS["muted"], self.font_small)
        for index, (ingredient_id, quantity) in enumerate(visible_stock):
            ingredient = self.ingredients.get(ingredient_id)
            name = ingredient.name if ingredient else ingredient_id
            y = stock_panel.y + 78 + index * 32
            pygame.draw.circle(self.screen, config.COLORS["sage"], (stock_panel.x + 26, y + 9), 4)
            self.draw_text(name, stock_panel.x + 40, y, config.COLORS["text"], self.font_small)
            qty = self.font_medium.render(f"×{quantity}", True, config.COLORS["teal"])
            self.screen.blit(qty, qty.get_rect(topright=(stock_panel.right - 20, y - 4)))
        if len(stock_items) > 13:
            self.button("stock_scroll_up", "▲", pygame.Rect(stock_panel.right - 78, stock_panel.y + 18, 27, 26),
                        enabled=self.stock_scroll > 0, color=config.COLORS["teal"])
            self.button("stock_scroll_down", "▼", pygame.Rect(stock_panel.right - 45, stock_panel.y + 18, 27, 26),
                        enabled=self.stock_scroll + 13 < len(stock_items), color=config.COLORS["teal"])


    def draw_profile(self):
        self.page_title("Profil Bisnis", "Lihat perkembangan keuangan dan aturan operasional restoran.")
        left = pygame.Rect(242, 202, 485, 535)
        right = pygame.Rect(745, 202, 510, 535)
        self.panel(left)
        self.panel(right)
        self.draw_text("Ringkasan keuangan", left.x + 22, left.y + 22,
                       config.COLORS["text"], self.font_display_small)
        stats = [
            ("Saldo saat ini", self.money(self.player.money)),
            ("Total pendapatan", self.money(self.player.total_revenue)),
            ("Total biaya bahan", self.money(self.player.total_expenses)),
            ("Keuntungan bersih", self.money(self.player.net_profit)),
            ("Makanan terjual", str(self.player.total_items_sold)),
            ("Hari berjalan", str(self.player.day)),
        ]
        for idx, (label, value) in enumerate(stats):
            y = left.y + 86 + idx * 55
            self.draw_text(label, left.x + 23, y, config.COLORS["muted"], self.font_small)
            val = self.font_medium.render(value, True, config.COLORS["text"])
            self.screen.blit(val, val.get_rect(topright=(left.right - 22, y - 5)))
            if idx < len(stats) - 1:
                pygame.draw.line(self.screen, config.COLORS["border"],
                                 (left.x + 22, y + 31), (left.right - 22, y + 31), 1)
        self.draw_text("Aturan restoran", right.x + 22, right.y + 22,
                       config.COLORS["text"], self.font_display_small)
        rules = [
            "Maksimal lima makanan dapat dijual setiap hari.",
            "Harga jual mengikuti harga dasar, kesulitan, dan kualitas.",
            "Belanja bahan tercatat sebagai biaya; penjualan sebagai pendapatan.",
            "Akhiri hari untuk mengatur ulang kuota penjualan.",
            "Toko bangkrut jika uang dan seluruh stok bernilai nol.",
        ]
        for idx, line in enumerate(rules):
            y = right.y + 88 + idx * 64
            pygame.draw.circle(self.screen, config.COLORS["mustard"], (right.x + 29, y + 8), 5)
            self.wrap_text(line, right.x + 45, y, right.width - 72,
                           config.COLORS["muted"], self.font_small, line_height=20, max_lines=2)
        self.button("profile_end_day", "Akhiri Hari",
                    pygame.Rect(right.x + 22, right.bottom - 58, 150, 38), color=config.COLORS["teal"])
        self.button("profile_save", "Simpan Sekarang",
                    pygame.Rect(right.x + 185, right.bottom - 58, 180, 38), color=config.COLORS["accent"])

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
                if mouse_x < 885:
                    self.inventory_scroll = max(0, min(max(0, len(self.player.food_inventory) - 7), self.inventory_scroll - event.y))
                else:
                    stock_count = sum(1 for qty in self.player.ingredient_stock.values() if qty > 0)
                    self.stock_scroll = max(0, min(max(0, stock_count - 13), self.stock_scroll - event.y))
            elif self.screen_name == state.MARKET:
                if mouse_x < 890:
                    self.market_scroll = max(0, min(max(0, len(self.ingredients) - 12), self.market_scroll - event.y))
                else:
                    self.cart_scroll = max(0, min(max(0, len(self.market.cart) - 10), self.cart_scroll - event.y))
            elif self.screen_name == state.RECIPES:
                self.recipe_scroll = max(0, min(max(0, len(self.recipe_system.all()) - 6), self.recipe_scroll - event.y * 2))


    def draw(self):
        self.screen.fill(config.COLORS["background"])
        # Garis halus pada area kertas memberi tekstur tanpa mengganggu keterbacaan.
        for y in range(96, config.WINDOW_HEIGHT, 34):
            pygame.draw.line(self.screen, config.COLORS["paper_line"], (212, y),
                             (config.WINDOW_WIDTH, y), 1)
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
