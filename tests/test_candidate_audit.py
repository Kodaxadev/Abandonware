#!/usr/bin/env python3
import unittest

from tools.audit_candidate_zip import is_notice_name, scan_evidence


class CandidateAuditEvidenceTests(unittest.TestCase):
    def test_wrapped_redistribution_prohibition_is_detected(self):
        text = (
            "The End User may not rent, lease, sell, or otherwise\n"
            "distribute the Software. The End User may make one backup copy."
        )
        evidence = scan_evidence(text)
        self.assertIn("redistribution_prohibited", evidence)

    def test_wrapped_copying_prohibition_is_detected(self):
        text = (
            "This Software is protected by copyright law. Copying any part or the look and feel\n"
            "of this Software is strictly forbidden."
        )
        evidence = scan_evidence(text)
        self.assertIn("copying_prohibited", evidence)

    def test_backup_only_is_detected(self):
        evidence = scan_evidence("One copy may be made solely for backup or archival purposes.")
        self.assertIn("backup_only", evidence)

    def test_affirmative_distribution_permission_is_not_a_prohibition(self):
        evidence = scan_evidence(
            "Permission is granted to distribute unmodified copies of this game free of charge."
        )
        self.assertIn("distribute", evidence)
        self.assertNotIn("redistribution_prohibited", evidence)
        self.assertNotIn("copying_prohibited", evidence)

    def test_authorship_and_attribution_notice_names_are_preserved(self):
        for filename in (
            "AUTHORS.TXT",
            "Credits.html",
            "PATENTS.TXT",
            "NOTICE",
            "ATTRIBUTION.md",
            "third-party-licenses.txt",
        ):
            with self.subTest(filename=filename):
                self.assertTrue(is_notice_name(filename))

    def test_game_payload_is_not_misclassified_as_notice(self):
        self.assertFalse(is_notice_name("gamedata.slg"))
        self.assertFalse(is_notice_name("gameicon.icns"))


if __name__ == "__main__":
    unittest.main()
