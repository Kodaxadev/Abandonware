#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "materialize_scummvm_games.py"
spec = importlib.util.spec_from_file_location("materialize_scummvm_games", MODULE_PATH)
materializer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(materializer)


class WorkingDirectory:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.previous: str | None = None

    def __enter__(self) -> None:
        self.previous = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self.previous is not None
        os.chdir(self.previous)


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


class ScummVMOpenLicenseEvidenceTests(unittest.TestCase):
    def create_fixture(self, root: Path) -> dict:
        rights = root / "docs" / "rights" / "open-game.md"
        rights.parent.mkdir(parents=True)
        rights.write_text("audited open-license rights record\n", encoding="utf-8")

        source_root = root / "runtime" / "sources" / "open-game"
        legal_root = source_root / "legal"
        legal_root.mkdir(parents=True)

        archive = source_root / "open-game-source.tar.gz"
        archive.write_bytes(b"immutable corresponding source bytes")
        archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()

        notice = legal_root / "COPYING"
        notice.write_text("open license and attribution\n", encoding="utf-8")
        notice_hash = hashlib.sha256(notice.read_bytes()).hexdigest()

        provenance = {
            "id": "open-game",
            "commit": "a" * 40,
            "tree": "b" * 40,
            "archive_file": archive.name,
            "archive_sha256": archive_hash,
            "preserved_notices": [
                {
                    "materialized_path": "legal/COPYING",
                    "sha256": notice_hash,
                }
            ],
        }
        source_record = source_root / "PROVENANCE.json"
        source_record.write_text(json.dumps(provenance), encoding="utf-8")

        return {
            "id": "open-game",
            "rights_basis": "open_license",
            "rights_record": rights.relative_to(root).as_posix(),
            "license_identifiers": ["LGPL-3.0", "CC-BY-3.0"],
            "corresponding_source_record": source_record.relative_to(root).as_posix(),
            "external_license_files": [notice.relative_to(root).as_posix()],
            "_archive": archive,
            "_source_record": source_record,
        }

    def test_open_license_can_use_external_source_evidence_without_package_notice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            game = self.create_fixture(root)
            with WorkingDirectory(root):
                policy, evidence = materializer.validate_rights_policy(game, notices=[])

            self.assertEqual(policy, "external_open_license_record")
            assert evidence is not None
            self.assertEqual(evidence["source_commit"], "a" * 40)
            self.assertEqual(evidence["license_identifiers"], ["LGPL-3.0", "CC-BY-3.0"])

    def test_open_license_rejects_unpreserved_external_license_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            game = self.create_fixture(root)
            extra = root / "runtime" / "sources" / "open-game" / "legal" / "UNTRACKED"
            extra.write_text("not in provenance\n", encoding="utf-8")
            game["external_license_files"] = [extra.relative_to(root).as_posix()]

            with WorkingDirectory(root):
                with self.assertRaisesRegex(RuntimeError, "not a preserved corresponding-source notice"):
                    materializer.validate_rights_policy(game, notices=[])

    def test_open_license_rejects_tampered_corresponding_source_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            game = self.create_fixture(root)
            game["_archive"].write_bytes(b"tampered after provenance was written")

            with WorkingDirectory(root):
                with self.assertRaisesRegex(RuntimeError, "archive hash mismatch"):
                    materializer.validate_rights_policy(game, notices=[])

    def test_freeware_still_requires_package_notice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rights = root / "rights.md"
            rights.write_text("freeware rights\n", encoding="utf-8")
            game = {
                "id": "freeware-game",
                "rights_basis": "freeware_redistribution",
                "rights_record": rights.name,
            }

            with WorkingDirectory(root):
                with self.assertRaisesRegex(RuntimeError, "contains no preserved"):
                    materializer.validate_rights_policy(game, notices=[])


if __name__ == "__main__":
    unittest.main()
