"""Penyimpanan progres Cooking TXT dengan backup dan perlindungan data.

Fitur:
- Penulisan atomik melalui file sementara.
- Backup save valid sebelumnya ke ``<save>.bak`` sebelum diganti.
- Karantina save rusak dengan timestamp, tanpa menghapus file aslinya.
- Proteksi tulis jika file rusak tidak dapat diamankan atau tidak dapat dibaca.
- Error penyimpanan dilaporkan melalui SaveError agar UI dapat memberi tahu pemain.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from src.entities.player import Player


class SaveError(RuntimeError):
    """Kegagalan saat menyimpan progres pemain."""


class SaveProtectionError(SaveError):
    """Penulisan diblokir untuk mencegah save lama tertimpa."""


class _CorruptSaveError(ValueError):
    """Isi save tidak valid atau tidak kompatibel."""


class _SaveReadError(OSError):
    """Save tidak dapat dibaca karena masalah filesystem/akses."""


class SaveManager:
    """Mengelola load/save pemain dengan fail-safe untuk data yang ada."""

    SAVE_VERSION = 1

    def __init__(self, save_path: str | Path):
        self.path = Path(save_path)
        self.backup_path = self.path.with_name(self.path.name + ".bak")

        # Informasi ini dipakai Game untuk memberi pemberitahuan yang sesuai.
        self.last_load_status = "not_loaded"
        self.last_error: str | None = None
        self.quarantined_path: Path | None = None
        self.write_protected = False
        self.write_protection_reason: str | None = None
        self.last_save_status = "not_saved"

    def _read_player_file(self, path: Path) -> Player:
        """Baca serta validasi satu file save tanpa mengubah file tersebut."""
        try:
            with path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise _CorruptSaveError(f"JSON tidak valid: {exc}") from exc
        except OSError as exc:
            raise _SaveReadError(f"File tidak dapat dibaca: {exc}") from exc

        if not isinstance(payload, dict):
            raise _CorruptSaveError("Struktur save harus berupa object JSON.")

        version = payload.get("version", self.SAVE_VERSION)
        if version != self.SAVE_VERSION:
            raise _CorruptSaveError(
                f"Versi save {version!r} tidak didukung (diharapkan {self.SAVE_VERSION})."
            )

        player_data = payload.get("player")
        if not isinstance(player_data, dict):
            raise _CorruptSaveError("Data pemain tidak ditemukan atau tidak valid.")

        try:
            player = Player.from_dict(player_data)
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
            raise _CorruptSaveError(f"Data pemain rusak: {exc}") from exc

        if not isinstance(player, Player):
            raise _CorruptSaveError("Data save tidak menghasilkan Player yang valid.")
        return player

    def _quarantine_corrupt_save(self) -> Path:
        """Pindahkan save rusak ke nama baru yang unik; jangan pernah menghapusnya."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        candidate = self.path.with_name(
            f"{self.path.stem}.corrupt-{timestamp}{self.path.suffix}"
        )
        suffix = 1
        while candidate.exists():
            candidate = self.path.with_name(
                f"{self.path.stem}.corrupt-{timestamp}-{suffix}{self.path.suffix}"
            )
            suffix += 1

        # os.replace hanya memindahkan file di filesystem yang sama. Jika gagal,
        # file sumber tetap dipertahankan dan pemanggil akan memblokir penulisan.
        os.replace(self.path, candidate)
        self.quarantined_path = candidate
        return candidate

    def load(self) -> Player | None:
        """Muat save; karantina file rusak dan lindungi file jika tidak aman."""
        self.last_load_status = "not_loaded"
        self.last_error = None
        self.quarantined_path = None
        self.write_protected = False
        self.write_protection_reason = None

        if not self.path.exists():
            self.last_load_status = "missing"
            return None

        try:
            player = self._read_player_file(self.path)
        except _CorruptSaveError as exc:
            self.last_error = str(exc)
            try:
                self._quarantine_corrupt_save()
            except OSError as backup_exc:
                self.last_load_status = "corrupt_backup_failed"
                self.write_protected = True
                self.write_protection_reason = (
                    "Save rusak tidak berhasil diamankan. File lama dipertahankan "
                    "dan penyimpanan baru diblokir agar data tidak tertimpa. "
                    f"Detail: {backup_exc}"
                )
            else:
                self.last_load_status = "corrupt_backed_up"
            return None
        except _SaveReadError as exc:
            self.last_load_status = "read_error"
            self.last_error = str(exc)
            self.write_protected = True
            self.write_protection_reason = (
                "Save tidak dapat dibaca. Penulisan diblokir agar file lama "
                f"tidak tertimpa. Detail: {exc}"
            )
            return None

        self.last_load_status = "loaded"
        return player

    def _create_backup(self) -> None:
        """Buat/replace .bak dari save valid sebelumnya secara aman."""
        fd, temporary_name = tempfile.mkstemp(
            prefix=self.backup_path.name + ".",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        os.close(fd)
        temporary_backup = Path(temporary_name)
        try:
            shutil.copy2(self.path, temporary_backup)
            os.replace(temporary_backup, self.backup_path)
        except OSError as exc:
            raise SaveError(
                "Backup save sebelumnya gagal dibuat; save utama tidak diubah. "
                f"Detail: {exc}"
            ) from exc
        finally:
            try:
                temporary_backup.unlink(missing_ok=True)
            except OSError:
                pass

    def _write_temporary_save(self, payload: dict[str, Any]) -> Path:
        """Tulis JSON ke file sementara pada folder yang sama dengan save utama."""
        fd, temporary_name = tempfile.mkstemp(
            prefix=self.path.name + ".",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            return temporary_path
        except Exception:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    def save(self, player: Player) -> None:
        """Simpan pemain; jangan menimpa data yang belum berhasil diamankan."""
        if self.write_protected:
            self.last_save_status = "blocked"
            raise SaveProtectionError(
                self.write_protection_reason
                or "Penyimpanan diblokir untuk melindungi save sebelumnya."
            )

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.last_save_status = "failed"
            raise SaveError(f"Folder save tidak dapat dibuat: {exc}") from exc

        temporary_path: Path | None = None
        try:
            payload = {
                "version": self.SAVE_VERSION,
                "player": player.to_dict(),
            }
            # Validasi serialisasi sebelum menyentuh save yang sudah ada.
            json.dumps(payload, ensure_ascii=False)
            temporary_path = self._write_temporary_save(payload)

            if self.path.exists():
                try:
                    self._read_player_file(self.path)
                except _CorruptSaveError as exc:
                    self.last_error = str(exc)
                    try:
                        self._quarantine_corrupt_save()
                    except OSError as backup_exc:
                        self.write_protected = True
                        self.write_protection_reason = (
                            "Save yang ada ternyata rusak dan tidak dapat diamankan. "
                            "Penulisan diblokir agar file tersebut tidak tertimpa. "
                            f"Detail: {backup_exc}"
                        )
                        raise SaveProtectionError(self.write_protection_reason) from backup_exc
                except _SaveReadError as exc:
                    self.write_protected = True
                    self.write_protection_reason = (
                        "Save lama tidak dapat diverifikasi; penulisan diblokir "
                        f"untuk melindungi data. Detail: {exc}"
                    )
                    raise SaveProtectionError(self.write_protection_reason) from exc
                else:
                    # Backup dibuat hanya setelah save lama terbukti valid.
                    self._create_backup()

            os.replace(temporary_path, self.path)
            temporary_path = None
            self.last_save_status = "saved"
            self.last_error = None
        except SaveError:
            self.last_save_status = "failed"
            raise
        except (OSError, TypeError, ValueError) as exc:
            self.last_save_status = "failed"
            raise SaveError(f"Progres gagal disimpan: {exc}") from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
