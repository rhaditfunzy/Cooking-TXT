"""Pemuatan gambar opsional; placeholder disediakan oleh UI jika file kosong."""
from pathlib import Path
import pygame


class AssetLoader:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.cache: dict[str, pygame.Surface] = {}

    def image(self, relative_path: str, size: tuple[int, int] | None = None):
        if not relative_path:
            return None
        path = self.root / relative_path
        key = f"{path}:{size}"
        if key in self.cache:
            return self.cache[key]
        if not path.exists():
            return None
        try:
            surface = pygame.image.load(str(path)).convert_alpha()
            if size:
                surface = pygame.transform.smoothscale(surface, size)
            self.cache[key] = surface
            return surface
        except (pygame.error, OSError):
            return None
