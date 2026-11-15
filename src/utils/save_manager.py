"""Penyimpanan progres dengan penulisan atomik."""
import json
from pathlib import Path
from src.entities.player import Player


class SaveManager:
    def __init__(self, save_path: str | Path):
        self.path = Path(save_path)

    def save(self, player: Player) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = {"version": 1, "player": player.to_dict()}
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        temp_path.replace(self.path)

    def load(self) -> Player | None:
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if not isinstance(payload, dict) or "player" not in payload:
                raise ValueError("Save file format is invalid")
            return Player.from_dict(payload["player"])
        except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError):
            # Jangan menimpa file rusak otomatis; mulai sesi baru, pengguna masih
            # dapat memeriksa file save secara manual.
            return None
