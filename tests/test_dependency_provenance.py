#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DependencyProvenanceTests(unittest.TestCase):
    def test_jszip_3101_is_local_and_matches_provenance(self) -> None:
        manifest = json.loads((ROOT / "runtime/jszip-build.json").read_text(encoding="utf-8"))
        provenance = json.loads((ROOT / "runtime/jszip/PROVENANCE.json").read_text(encoding="utf-8"))
        artifact = ROOT / "runtime/jszip/jszip.min.js"
        source_record = ROOT / "runtime/jszip/SOURCE.md"
        license_file = ROOT / "runtime/jszip/legal/LICENSE.markdown"
        index = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertEqual(manifest["runtime"]["version"], "3.10.1")
        self.assertEqual(manifest["runtime"]["commit"], "0f2f1e4d0509514417db83fe5b86bde90e0ffe8d")
        self.assertEqual(provenance["runtime"], manifest["runtime"])
        self.assertTrue(artifact.is_file())
        self.assertTrue(source_record.is_file())
        self.assertTrue(license_file.is_file())

        actual_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        self.assertEqual(actual_sha, provenance["sha256"])
        self.assertIn("JSZip v3.10.1", artifact.read_text(encoding="utf-8"))
        self.assertIn('src="runtime/jszip/jszip.min.js"', index)
        self.assertNotIn("cdn.jsdelivr.net/npm/jszip", index)

    def test_functional_browser_runtimes_are_repository_local(self) -> None:
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        required = (
            'href="runtime/jsdos/js-dos.css"',
            'src="runtime/jszip/jszip.min.js"',
            'src="runtime/jsdos/js-dos.js"',
            'src="runtime/jsdos/bridge.js"',
        )
        for marker in required:
            self.assertIn(marker, index)

        forbidden = (
            "v8.js-dos.com/latest",
            "cdn.jsdelivr.net/npm/jszip",
        )
        for marker in forbidden:
            self.assertNotIn(marker, index)


if __name__ == "__main__":
    unittest.main()
