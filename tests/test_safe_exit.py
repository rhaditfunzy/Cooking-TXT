"""Regression tests for v0.3.1c safe-exit behavior."""
import unittest

from src.systems.exit_system import ExitSystem
from src.systems.cooking_system import CookingSystem


class EscapeRoutingTests(unittest.TestCase):
    def setUp(self):
        self.exit_system = ExitSystem()

    def test_escape_on_non_cooking_screen_requests_exit_confirmation(self):
        action = self.exit_system.escape_action(
            is_cooking=False, cooking_phase="idle", fullscreen=False,
            pending_result=False,
        )
        self.assertEqual(action, "request_exit")

    def test_escape_in_fullscreen_keeps_existing_fullscreen_shortcut(self):
        action = self.exit_system.escape_action(
            is_cooking=False, cooking_phase="idle", fullscreen=True,
            pending_result=False,
        )
        self.assertEqual(action, "leave_fullscreen")

    def test_escape_during_cooking_requests_cancel_confirmation(self):
        action = self.exit_system.escape_action(
            is_cooking=True, cooking_phase="ingredient_timing", fullscreen=False,
            pending_result=False,
        )
        self.assertEqual(action, "confirm_cooking_cancel")

    def test_escape_from_idle_cooking_returns_to_recipe_book(self):
        action = self.exit_system.escape_action(
            is_cooking=True, cooking_phase="idle", fullscreen=False,
            pending_result=False,
        )
        self.assertEqual(action, "back_to_recipes")

    def test_escape_with_unsaved_food_requests_exit_warning(self):
        action = self.exit_system.escape_action(
            is_cooking=True, cooking_phase="finished", fullscreen=False,
            pending_result=True,
        )
        self.assertEqual(action, "request_exit")

    def test_escape_while_dialog_open_cancels_dialog(self):
        self.exit_system.request_exit()
        action = self.exit_system.escape_action(
            is_cooking=False, cooking_phase="idle", fullscreen=False,
            pending_result=False,
        )
        self.assertEqual(action, "cancel_dialog")


class ExitSaveTests(unittest.TestCase):
    def setUp(self):
        self.exit_system = ExitSystem()
        self.exit_system.request_exit()

    def test_successful_save_allows_exit_and_prevents_duplicate_final_save(self):
        self.assertTrue(self.exit_system.confirm_exit(lambda: True))
        self.assertIsNone(self.exit_system.dialog)
        self.assertTrue(self.exit_system.final_save_attempted)
        self.assertFalse(self.exit_system.skip_final_save)

    def test_failed_save_keeps_exit_dialog_open_for_retry(self):
        self.assertFalse(self.exit_system.confirm_exit(lambda: False))
        self.assertEqual(self.exit_system.dialog, ExitSystem.EXIT_SAVE_FAILED)
        self.assertFalse(self.exit_system.final_save_attempted)
        self.assertFalse(self.exit_system.skip_final_save)

    def test_retry_after_failed_save_can_succeed(self):
        self.assertFalse(self.exit_system.confirm_exit(lambda: False))
        self.assertTrue(self.exit_system.confirm_exit(lambda: True))
        self.assertIsNone(self.exit_system.dialog)
        self.assertTrue(self.exit_system.final_save_attempted)

    def test_unexpected_save_exception_keeps_game_open(self):
        def fail():
            raise OSError("disk unavailable")

        self.assertFalse(self.exit_system.confirm_exit(fail))
        self.assertEqual(self.exit_system.dialog, ExitSystem.EXIT_SAVE_FAILED)
        self.assertIsInstance(self.exit_system.last_error, OSError)

    def test_explicit_exit_without_saving_skips_finally_save(self):
        self.assertTrue(self.exit_system.exit_without_saving())
        self.assertIsNone(self.exit_system.dialog)
        self.assertTrue(self.exit_system.skip_final_save)
        self.assertFalse(self.exit_system.final_save_attempted)

    def test_cancel_dialog_does_not_exit_or_skip_saving(self):
        self.exit_system.cancel_dialog()
        self.assertIsNone(self.exit_system.dialog)
        self.assertFalse(self.exit_system.skip_final_save)
        self.assertFalse(self.exit_system.final_save_attempted)

    def test_exit_without_saving_is_not_valid_for_cooking_cancel_dialog(self):
        self.exit_system.cancel_dialog()
        self.exit_system.request_cooking_cancel()
        self.assertFalse(self.exit_system.exit_without_saving())
        self.assertEqual(self.exit_system.dialog, ExitSystem.COOKING_CANCEL_CONFIRM)


class CookingPauseTests(unittest.TestCase):
    def setUp(self):
        self.cooking = CookingSystem(countdown_seconds=3.0)
        self.recipe = {
            "id": "test_recipe",
            "name": "Test Recipe",
            "difficulty": "easy",
            "base_price": 100,
            "ingredients": [{"id": "rice", "quantity": 1, "timing": 5.0}],
            "cooking_time": 8.0,
        }

    def test_countdown_is_frozen_and_deadline_shifts_on_resume(self):
        self.cooking.start(self.recipe, 10.0)
        self.cooking.pause(11.0)
        self.cooking.update(40.0)
        self.assertEqual(self.cooking.phase, "countdown")
        self.assertEqual(self.cooking.countdown_end, 13.0)

        self.cooking.resume(40.0)
        self.assertEqual(self.cooking.countdown_end, 42.0)
        self.cooking.update(42.0)
        self.assertEqual(self.cooking.phase, "ingredient_timing")
        self.assertEqual(self.cooking.target_time, 47.0)

    def test_ingredient_timer_preserves_remaining_time_after_pause(self):
        self.cooking.start(self.recipe, 10.0)
        self.cooking.update(13.0)
        self.assertEqual(self.cooking.phase, "ingredient_timing")
        self.assertEqual(self.cooking.target_time, 18.0)

        self.cooking.pause(14.0)
        self.cooking.update(90.0)
        self.assertEqual(self.cooking.target_time, 18.0)
        self.cooking.resume(90.0)
        self.assertEqual(self.cooking.target_time, 94.0)
        self.assertEqual(self.cooking.seconds_until_target(90.0), 4.0)

    def test_final_cooking_timer_preserves_remaining_time_after_pause(self):
        self.cooking.start(self.recipe, 10.0)
        self.cooking.update(13.0)
        self.cooking.submit_action(18.0)
        self.assertEqual(self.cooking.phase, "final_cooking")
        self.assertEqual(self.cooking.target_time, 26.0)

        self.cooking.pause(20.0)
        self.cooking.update(90.0)
        self.cooking.resume(90.0)
        self.assertEqual(self.cooking.target_time, 96.0)
        self.assertEqual(self.cooking.seconds_until_target(90.0), 6.0)

    def test_paused_cooking_rejects_actions_until_resumed(self):
        self.cooking.start(self.recipe, 10.0)
        self.cooking.update(13.0)
        self.cooking.pause(14.0)
        self.assertIsNone(self.cooking.submit_action(18.0))
        self.assertEqual(self.cooking.step_index, 0)

    def test_reset_clears_pause_state(self):
        self.cooking.start(self.recipe, 10.0)
        self.cooking.pause(11.0)
        self.cooking.reset()
        self.assertIsNone(self.cooking.paused_at)
        self.assertEqual(self.cooking.phase, "idle")


if __name__ == "__main__":
    unittest.main()
