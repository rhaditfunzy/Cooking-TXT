"""State machine memasak berbasis waktu nyata.

Urutan: countdown -> ingredient_timing (berulang) -> final_cooking -> finished.
Setiap waktu timing dihitung sejak aksi sebelumnya. Selisih dari target menentukan
kualitas akhir. Sistem ini tidak bergantung pada Pygame sehingga mudah dites.
"""
from __future__ import annotations
from uuid import uuid4
from typing import Any
from config import COUNTDOWN_SECONDS, GOOD_TIMING_TOLERANCE, MID_TIMING_TOLERANCE
from src.entities.food import Food


class CookingSystem:
    def __init__(self, good_tolerance: float = GOOD_TIMING_TOLERANCE,
                 mid_tolerance: float = MID_TIMING_TOLERANCE,
                 countdown_seconds: float = COUNTDOWN_SECONDS):
        self.good_tolerance = good_tolerance
        self.mid_tolerance = mid_tolerance
        self.countdown_seconds = countdown_seconds
        self.reset()

    def reset(self) -> None:
        self.recipe: dict[str, Any] | None = None
        self.phase = "idle"
        self.countdown_end = 0.0
        self.target_time = 0.0
        self.started_at = 0.0
        self.paused_at: float | None = None
        self.step_index = 0
        self.deviations: list[float] = []
        self.last_deviation: float | None = None
        self.finished_food: Food | None = None
        self.message = "Pilih resep untuk mulai memasak."

    def pause(self, now: float) -> None:
        # Freeze an active timer while a confirmation modal is shown.
        if self.paused_at is None and self.phase in {
            "countdown", "ingredient_timing", "final_cooking"
        }:
            self.paused_at = float(now)

    def resume(self, now: float) -> None:
        # Shift active deadlines by the paused duration, preserving remaining time.
        if self.paused_at is None:
            return
        duration = max(0.0, float(now) - self.paused_at)
        self.started_at += duration
        if self.phase == "countdown":
            self.countdown_end += duration
            self.target_time += duration
        elif self.phase in {"ingredient_timing", "final_cooking"}:
            self.target_time += duration
        self.paused_at = None

    def start(self, recipe: dict[str, Any], now: float) -> None:
        if self.phase not in {"idle", "finished"}:
            raise RuntimeError("Masih ada sesi memasak yang berjalan")
        self.recipe = recipe
        self.phase = "countdown"
        self.started_at = now
        self.paused_at = None
        self.countdown_end = now + self.countdown_seconds
        self.target_time = self.countdown_end
        self.step_index = 0
        self.deviations = []
        self.last_deviation = None
        self.finished_food = None
        self.message = "Bersiap!"

    def update(self, now: float) -> None:
        if self.paused_at is not None:
            return
        if self.phase == "countdown" and now >= self.countdown_end:
            self.phase = "ingredient_timing"
            first_interval = float(self.recipe["ingredients"][0]["timing"])
            self.target_time = self.countdown_end + first_interval
            self.message = "Masukkan bahan pertama sesuai timer."

    def expected_ingredient(self) -> dict[str, Any] | None:
        if self.phase != "ingredient_timing" or not self.recipe:
            return None
        return self.recipe["ingredients"][self.step_index]

    def seconds_until_target(self, now: float) -> float:
        if self.phase == "countdown":
            return self.countdown_end - now
        if self.phase in {"ingredient_timing", "final_cooking"}:
            return self.target_time - now
        return 0.0

    def submit_action(self, now: float) -> Food | None:
        """Masukkan bahan berikutnya atau ambil makanan saat timer selesai."""
        if self.paused_at is not None:
            return None
        if self.phase not in {"ingredient_timing", "final_cooking"} or not self.recipe:
            return None
        deviation = abs(now - self.target_time)
        self.last_deviation = deviation
        self.deviations.append(deviation)

        if self.phase == "ingredient_timing":
            self.step_index += 1
            if self.step_index < len(self.recipe["ingredients"]):
                next_interval = float(self.recipe["ingredients"][self.step_index]["timing"])
                self.target_time = now + next_interval
                self.message = "Bahan berhasil dimasukkan. Siapkan bahan berikutnya."
            else:
                self.phase = "final_cooking"
                self.target_time = now + float(self.recipe["cooking_time"])
                self.message = "Semua bahan masuk. Tunggu sampai makanan matang."
            return None

        quality = self._calculate_quality()
        self.finished_food = Food(
            instance_id=str(uuid4()),
            recipe_id=str(self.recipe["id"]),
            name=str(self.recipe["name"]),
            difficulty=str(self.recipe["difficulty"]),
            quality=quality,
            base_price=int(self.recipe["base_price"]),
            image=str(self.recipe.get("image", "")),
        )
        self.phase = "finished"
        self.message = f"Masakan selesai dengan kualitas {quality.upper()}!"
        return self.finished_food

    def _calculate_quality(self) -> str:
        worst_deviation = max(self.deviations, default=0.0)
        if worst_deviation <= self.good_tolerance:
            return "good"
        if worst_deviation <= self.mid_tolerance:
            return "mid"
        return "poor"

    def countdown_number(self, now: float) -> int:
        remaining = max(0.0, self.countdown_end - now)
        return max(1, int(remaining) + (1 if remaining % 1 else 0))
