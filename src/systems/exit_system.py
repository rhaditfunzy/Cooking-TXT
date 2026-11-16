"""Pure state manager for safe application exit and Escape-key behavior."""
from __future__ import annotations

from typing import Callable


class ExitSystem:
    """Coordinates exit dialogs without depending on Pygame or the UI layer."""

    EXIT_CONFIRM = "exit_confirm"
    EXIT_SAVE_FAILED = "exit_save_failed"
    COOKING_CANCEL_CONFIRM = "cooking_cancel_confirm"

    def __init__(self) -> None:
        self.dialog: str | None = None
        self.final_save_attempted = False
        self.skip_final_save = False
        self.last_error: Exception | None = None

    def escape_action(
        self,
        *,
        is_cooking: bool,
        cooking_phase: str,
        fullscreen: bool,
        pending_result: bool,
    ) -> str:
        """Return the context-sensitive action for an Escape key press."""
        if self.dialog is not None:
            return "cancel_dialog"
        if fullscreen:
            return "leave_fullscreen"
        if is_cooking:
            if pending_result:
                return "request_exit"
            if cooking_phase not in {"idle", "finished"}:
                return "confirm_cooking_cancel"
            return "back_to_recipes"
        return "request_exit"

    def request_exit(self) -> None:
        if self.dialog is None:
            self.last_error = None
            self.dialog = self.EXIT_CONFIRM

    def request_cooking_cancel(self) -> None:
        if self.dialog is None:
            self.dialog = self.COOKING_CANCEL_CONFIRM

    def cancel_dialog(self) -> None:
        self.dialog = None
        self.last_error = None

    def confirm_exit(self, save_callback: Callable[[], bool]) -> bool:
        """Save before exit; remain open and expose a retry state on failure."""
        if self.dialog not in {self.EXIT_CONFIRM, self.EXIT_SAVE_FAILED}:
            return False

        self.last_error = None
        try:
            saved = bool(save_callback())
        except Exception as exc:  # keep the UI open even for an unexpected save error
            self.last_error = exc
            saved = False

        if not saved:
            self.dialog = self.EXIT_SAVE_FAILED
            return False

        self.dialog = None
        self.final_save_attempted = True
        return True

    def exit_without_saving(self) -> bool:
        """Allow an explicit, warned exit without a final save."""
        if self.dialog not in {self.EXIT_CONFIRM, self.EXIT_SAVE_FAILED}:
            return False
        self.dialog = None
        self.skip_final_save = True
        return True
