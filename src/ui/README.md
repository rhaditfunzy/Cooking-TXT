# UI modules

Pada build 0.1.0, layout Pygame dan event dispatch masih berada di `src/core/game.py` agar entry point awal tetap sederhana. Folder ini disiapkan untuk memindahkan komponen seperti navigation bar, cards, market screen, dan inventory screen ketika UI berkembang. Logic gameplay tetap berada di `src/systems/`, bukan di folder UI.
