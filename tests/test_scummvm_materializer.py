#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "materialize_scummvm_games.py"
spec = importlib.util.spec_from_file_location("materialize_scummvm_games", MODULE_PATH)
materializer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(materializer)


class ScummVMTargetValidationTests(unittest.TestCase):
    def test_parent_directory_with_only_nested_payload_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_root = Path(temp_dir)
            nested = data_root / "sfinx-en-v1.1" / "sfinx-en-v1.1"
            nested.mkdir(parents=True)
            (nested / "vol.cat").write_bytes(b"catalog")
            (nested / "vol.dat").write_bytes(b"data")

            game = {
                "id": "sfinx",
                "data_directory": "sfinx-en-v1.1",
                "relative_game_path": ".",
                "required_files": ["vol.cat", "vol.dat"],
            }

            with self.assertRaisesRegex(RuntimeError, "no direct payload files"):
                materializer.validate_game_target(data_root, game)

    def test_nested_payload_passes_when_relative_path_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_root = Path(temp_dir)
            nested = data_root / "sfinx-en-v1.1" / "sfinx-en-v1.1"
            nested.mkdir(parents=True)
            (nested / "vol.cat").write_bytes(b"catalog")
            (nested / "vol.dat").write_bytes(b"data")
            (nested / "license.txt").write_text("redistribution notice", encoding="utf-8")

            game = {
                "id": "sfinx",
                "data_directory": "sfinx-en-v1.1",
                "relative_game_path": "sfinx-en-v1.1",
                "required_files": ["vol.cat", "vol.dat"],
            }

            target, direct_files = materializer.validate_game_target(data_root, game)
            self.assertEqual(target, nested)
            self.assertEqual(direct_files, ["license.txt", "vol.cat", "vol.dat"])

    def test_required_detection_file_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_root = Path(temp_dir)
            target = data_root / "soltys-en-v1.0"
            target.mkdir(parents=True)
            (target / "vol.cat").write_bytes(b"catalog")

            game = {
                "id": "soltys",
                "data_directory": "soltys-en-v1.0",
                "relative_game_path": ".",
                "required_files": ["vol.cat", "vol.dat"],
            }

            with self.assertRaisesRegex(RuntimeError, "Required ScummVM detection file is missing"):
                materializer.validate_game_target(data_root, game)

    def test_relative_paths_cannot_escape_game_directory(self) -> None:
        game = {
            "id": "escape",
            "data_directory": "game",
            "relative_game_path": "../outside",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(RuntimeError, "Unsafe ZIP/member-relative path"):
                materializer.game_target_path(Path(temp_dir), game)


if __name__ == "__main__":
    unittest.main()
