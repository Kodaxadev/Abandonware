#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile

from tools.audit_github_release import inspect_archive, notice_name, safe_path


class GitHubReleaseAuditTests(unittest.TestCase):
    def test_zip_fingerprints_one_required_payload_and_notices(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "release.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("game/data.dcp", b"payload")
                archive.writestr("game/LICENSE", "redistribution evidence")
                archive.writestr("game/README.md", "release notes")

            members, payload, notices = inspect_archive(archive_path, archive_path.name, "data.dcp")

            self.assertEqual(payload["path"], "game/data.dcp")
            self.assertEqual(payload["size"], 7)
            self.assertEqual({notice["path"] for notice in notices}, {"game/LICENSE", "game/README.md"})
            self.assertEqual(len(members), 3)

    def test_tar_rejects_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "release.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                payload = Path(temp_dir) / "data.dcp"
                payload.write_bytes(b"payload")
                archive.add(payload, arcname="game/data.dcp")
                info = tarfile.TarInfo("game/link")
                info.type = tarfile.SYMTYPE
                info.linkname = "data.dcp"
                archive.addfile(info)

            with self.assertRaisesRegex(RuntimeError, "link member"):
                inspect_archive(archive_path, archive_path.name, "data.dcp")

    def test_duplicate_payload_suffix_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "release.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("one/data.dcp", b"one")
                archive.writestr("two/data.dcp", b"two")

            with self.assertRaisesRegex(RuntimeError, "Expected exactly one"):
                inspect_archive(archive_path, archive_path.name, "data.dcp")

    def test_paths_cannot_escape_archive(self):
        with self.assertRaisesRegex(RuntimeError, "Unsafe archive member path"):
            safe_path("../escape")

    def test_attribution_notice_names_are_preserved(self):
        for value in ("AUTHORS", "Credits.txt", "PATENTS.TXT", "ATTRIBUTION.md", "third-party.txt"):
            with self.subTest(value=value):
                self.assertTrue(notice_name(value))


if __name__ == "__main__":
    unittest.main()
