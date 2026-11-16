"""Regression tests for v0.3.1a save protection."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.entities.player import Player
from src.utils.save_manager import (
    SaveError,
    SaveManager,
    SaveProtectionError,
)


class SaveProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.save_path = Path(self.temp_dir.name) / "player_save.json"
        self.manager = SaveManager(self.save_path)

    def test_missing_save_can_be_created(self):
        self.assertIsNone(self.manager.load())
        self.assertEqual(self.manager.last_load_status, "missing")
        self.assertFalse(self.manager.write_protected)

        self.manager.save(Player(money=250))
        self.assertTrue(self.save_path.exists())
        self.assertEqual(self.manager.load().money, 250)

    def test_corrupt_json_is_quarantined_without_data_loss(self):
        corrupt_bytes = b'{"version": 1, "player": '
        self.save_path.write_bytes(corrupt_bytes)

        loaded = self.manager.load()

        self.assertIsNone(loaded)
        self.assertEqual(self.manager.last_load_status, "corrupt_backed_up")
        self.assertFalse(self.manager.write_protected)
        self.assertFalse(self.save_path.exists())
        self.assertIsNotNone(self.manager.quarantined_path)
        self.assertTrue(self.manager.quarantined_path.exists())
        self.assertEqual(self.manager.quarantined_path.read_bytes(), corrupt_bytes)

    def test_invalid_player_payload_is_quarantined(self):
        self.save_path.write_text(
            json.dumps({"version": 1, "player": []}), encoding="utf-8"
        )

        self.assertIsNone(self.manager.load())
        self.assertEqual(self.manager.last_load_status, "corrupt_backed_up")
        self.assertTrue(self.manager.quarantined_path.exists())

    def test_unsupported_save_version_is_quarantined(self):
        self.save_path.write_text(
            json.dumps({"version": 999, "player": {}}), encoding="utf-8"
        )

        self.assertIsNone(self.manager.load())
        self.assertEqual(self.manager.last_load_status, "corrupt_backed_up")
        self.assertTrue(self.manager.quarantined_path.exists())

    def test_failed_quarantine_blocks_future_writes(self):
        original = b"not valid json"
        self.save_path.write_bytes(original)

        with mock.patch.object(
            self.manager,
            "_quarantine_corrupt_save",
            side_effect=OSError("permission denied"),
        ):
            self.assertIsNone(self.manager.load())

        self.assertEqual(self.manager.last_load_status, "corrupt_backup_failed")
        self.assertTrue(self.manager.write_protected)
        self.assertEqual(self.save_path.read_bytes(), original)

        with self.assertRaises(SaveProtectionError):
            self.manager.save(Player(money=999))

        self.assertEqual(self.save_path.read_bytes(), original)

    def test_valid_previous_save_is_backed_up_before_replacement(self):
        self.manager.save(Player(money=100))
        self.assertFalse(self.manager.backup_path.exists())

        self.manager.save(Player(money=200))

        backup_payload = json.loads(self.manager.backup_path.read_text(encoding="utf-8"))
        current_payload = json.loads(self.save_path.read_text(encoding="utf-8"))
        self.assertEqual(backup_payload["player"]["money"], 100)
        self.assertEqual(current_payload["player"]["money"], 200)

    def test_backup_failure_preserves_previous_save(self):
        self.manager.save(Player(money=100))
        original = self.save_path.read_bytes()

        with mock.patch(
            "src.utils.save_manager.shutil.copy2",
            side_effect=OSError("disk unavailable"),
        ):
            with self.assertRaises(SaveError):
                self.manager.save(Player(money=200))

        self.assertEqual(self.save_path.read_bytes(), original)
        self.assertEqual(self.manager.last_save_status, "failed")

    def test_corrupt_file_found_during_save_is_quarantined(self):
        original = b"{broken"
        self.save_path.write_bytes(original)

        self.manager.save(Player(money=300))

        self.assertTrue(self.save_path.exists())
        self.assertTrue(self.manager.quarantined_path.exists())
        self.assertEqual(self.manager.quarantined_path.read_bytes(), original)
        current = json.loads(self.save_path.read_text(encoding="utf-8"))
        self.assertEqual(current["player"]["money"], 300)

    def test_corrupt_save_backup_name_is_unique(self):
        self.save_path.write_text("bad", encoding="utf-8")
        first_manager = SaveManager(self.save_path)
        first_manager.load()

        self.save_path.write_text("also bad", encoding="utf-8")
        second_manager = SaveManager(self.save_path)
        second_manager.load()

        self.assertNotEqual(
            first_manager.quarantined_path,
            second_manager.quarantined_path,
        )
        self.assertTrue(first_manager.quarantined_path.exists())
        self.assertTrue(second_manager.quarantined_path.exists())


if __name__ == "__main__":
    unittest.main()
