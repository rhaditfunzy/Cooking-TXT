"""Compact the Cooking TXT sidebar brand block without changing gameplay/UI logic."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "src" / "core" / "game.py"

REPLACEMENTS = {
    'pygame.draw.line(self.screen, config.COLORS["mustard"], (20, 139), (192, 139), 2)':
        'pygame.draw.line(self.screen, config.COLORS["mustard"], (20, 113), (192, 113), 2)',
    'self.draw_text("COOKING", 25, 27, config.COLORS["surface"], self.font_display_small)':
        'self.draw_text("COOKING", 25, 17, config.COLORS["surface"], self.font_display_small)',
    'self.draw_text("TXT", 27, 69, config.COLORS["mustard"], self.font_medium)':
        'self.draw_text("TXT", 27, 49, config.COLORS["mustard"], self.font_medium)',
    'self.draw_text("RESTAURANT JOURNAL", 27, 111, config.COLORS["surface_light"], self.font_small)':
        'self.draw_text("RESTAURANT JOURNAL", 27, 81, config.COLORS["surface_light"], self.font_small)',
}


def main() -> int:
    if not TARGET.is_file():
        print("[ERROR] File src/core/game.py tidak ditemukan.")
        print("Pastikan script ini berada di folder utama Cooking-TXT.")
        return 1

    source = TARGET.read_text(encoding="utf-8")
    pending = {old: new for old, new in REPLACEMENTS.items() if old in source}

    if not pending:
        if all(new in source for new in REPLACEMENTS.values()):
            print("[INFO] Sidebar spacing sudah diperbaiki. Tidak ada perubahan.")
            return 0
        print("[ERROR] Susunan kode tidak cocok dengan versi yang didukung hotfix ini.")
        print("Tidak ada file yang diubah. Perbarui repository atau periksa game.py.")
        return 1

    missing = [old for old in REPLACEMENTS if old not in source and REPLACEMENTS[old] not in source]
    if missing:
        print("[ERROR] Sebagian baris tidak cocok dengan versi game.py ini.")
        print("Tidak ada file yang diubah agar patch tidak diterapkan setengah jalan.")
        return 1

    updated = source
    for old, new in REPLACEMENTS.items():
        updated = updated.replace(old, new, 1)

    try:
        compile(updated, str(TARGET), "exec")
    except SyntaxError as exc:
        print(f"[ERROR] Hasil patch gagal pemeriksaan sintaks: {exc}")
        print("Tidak ada file yang diubah.")
        return 1

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_name(f"game.py.before-sidebar-spacing-{stamp}.bak")
    backup.write_text(source, encoding="utf-8")
    TARGET.write_text(updated, encoding="utf-8", newline="\n")

    print("[OK] Sidebar brand spacing berhasil dirapikan.")
    print("     COOKING: y=17 | TXT: y=49 | RESTAURANT JOURNAL: y=81")
    print("     Garis pemisah: y=113")
    print(f"[BACKUP] {backup.name}")
    print("Tidak ada sistem gameplay, Market, fullscreen, atau header saldo yang diubah.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
