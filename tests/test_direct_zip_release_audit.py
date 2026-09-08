#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.audit_direct_zip_release import decode_notice, notice_name, safe_path


class DirectZipReleaseAuditTests(unittest.TestCase):
    def test_safe_path_rejects_escape(self):
        with self.assertRaisesRegex(RuntimeError, "Unsafe archive member path"):
            safe_path("../escape")

    def test_safe_path_normalizes_windows_separator(self):
        self.assertEqual(safe_path(r"game\INIT.DFW").as_posix(), "game/INIT.DFW")

    def test_notice_names_include_attribution_files(self):
        for name in ("LICENSE", "README.txt", "AUTHORS", "credits.md", "ATTRIBUTION"):
            with self.subTest(name=name):
                self.assertTrue(notice_name(name))

    def test_binary_notice_is_not_decoded_as_text(self):
        self.assertIsNone(decode_notice(b"notice\x00binary"))


if __name__ == "__main__":
    unittest.main()
