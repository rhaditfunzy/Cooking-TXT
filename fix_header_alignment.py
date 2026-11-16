"""Apply the Cooking TXT header text alignment hotfix.

Run this file from the Cooking-TXT project root:
    python fix_header_alignment.py

Only the day and cash labels in Game.header() are changed.
"""
from __future__ import annotations

from pathlib import Path
import sys

TARGET = Path("src/core/game.py")
OLD_BLOCK = '''        self.draw_text(f"HARI {self.player.day}", day_rect.x + 13, day_rect.y + 12,
                       config.COLORS["teal"], self.font_medium)
        pygame.draw.circle(self.screen, config.COLORS["mustard"], (money_rect.x + 22, money_rect.centery), 8)
        self.draw_text(self.money(self.player.money), money_rect.x + 40, money_rect.y + 10,
                       config.COLORS["text"], self.font_medium)
'''
NEW_BLOCK = '''        # Center the day label both horizontally and vertically in its badge.
        day_surface = self.font_medium.render(f"HARI {self.player.day}", True, config.COLORS["teal"])
        self.screen.blit(day_surface, day_surface.get_rect(center=day_rect.center))

        # Center the coin icon + balance as one visual group in the cash badge.
        coin_radius = 8
        coin_diameter = coin_radius * 2
        coin_gap = 9
        money_surface = self.font_medium.render(self.money(self.player.money), True, config.COLORS["text"])
        group_width = coin_diameter + coin_gap + money_surface.get_width()
        group_left = money_rect.centerx - group_width // 2

        pygame.draw.circle(
            self.screen,
            config.COLORS["mustard"],
            (group_left + coin_radius, money_rect.centery),
            coin_radius,
        )
        money_rect_text = money_surface.get_rect(
            midleft=(group_left + coin_diameter + coin_gap, money_rect.centery)
        )
        self.screen.blit(money_surface, money_rect_text)
'''


def main() -> int:
    if not TARGET.is_file():
        print(f"ERROR: Tidak menemukan {TARGET}. Jalankan script dari folder utama Cooking-TXT.")
        return 1

    source = TARGET.read_text(encoding="utf-8")
    if NEW_BLOCK in source:
        print("Header sudah menggunakan alignment fix; tidak ada perubahan yang diperlukan.")
        return 0
    if OLD_BLOCK not in source:
        print("ERROR: Blok header yang diharapkan tidak ditemukan.")
        print("Tidak ada file yang diubah. Pastikan game.py berasal dari versi repository yang sesuai.")
        return 2

    backup = TARGET.with_suffix(".py.before_header_alignment.bak")
    if not backup.exists():
        backup.write_text(source, encoding="utf-8")

    updated = source.replace(OLD_BLOCK, NEW_BLOCK, 1)
    compile(updated, str(TARGET), "exec")
    TARGET.write_text(updated, encoding="utf-8", newline="\n")

    print("Berhasil memperbaiki alignment HARI dan saldo koin di header.")
    print(f"Backup dibuat di: {backup}")
    print("Tidak ada perubahan pada fullscreen, Market, atau sistem gameplay.")
    print("Jalankan game dengan: python main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
