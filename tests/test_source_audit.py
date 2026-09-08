#!/usr/bin/env python3
import unittest

from tools.audit_source_repo import decode_notice, notice_name, safe_git_path, validate_path_list


class SourceAuditEvidenceTests(unittest.TestCase):
    def test_authorship_and_attribution_notice_names_are_discovered(self):
        for path in (
            "AUTHORS",
            "docs/CREDITS.md",
            "legal/PATENTS.txt",
            "NOTICE",
            "ATTRIBUTION.md",
            "third-party-licenses.txt",
        ):
            with self.subTest(path=path):
                self.assertTrue(notice_name(path))

    def test_unrelated_source_filename_is_not_implicitly_legal_evidence(self):
        self.assertFalse(notice_name("rooms/room06/room06.slu"))
        self.assertFalse(notice_name("music/track.ogg"))

    def test_explicit_evidence_path_list_rejects_duplicates(self):
        manifest = {
            "rights_evidence_paths": [
                "rooms/room06/room06.slu",
                "rooms/room06/room06.slu",
            ]
        }
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            validate_path_list(manifest, "rights_evidence_paths")

    def test_explicit_evidence_path_list_rejects_traversal(self):
        manifest = {"rights_evidence_paths": ["../outside.txt"]}
        with self.assertRaisesRegex(RuntimeError, "Unsafe Git tree path"):
            validate_path_list(manifest, "rights_evidence_paths")

    def test_safe_git_path_normalizes_windows_separators(self):
        self.assertEqual(
            safe_git_path(r"rooms\room06\room06.slu"),
            "rooms/room06/room06.slu",
        )

    def test_text_evidence_decoder_rejects_binary_blob(self):
        self.assertIsNone(decode_notice(b"license\x00binary"))


if __name__ == "__main__":
    unittest.main()
