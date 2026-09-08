#!/usr/bin/env python3
import unittest

from tools.materialize_direct_source_set import safe_relative, source_set_hash


class DirectSourceSetTests(unittest.TestCase):
    def test_source_set_hash_is_order_sensitive_and_deterministic(self):
        components = [
            {"name": "a.zip", "size": 1, "sha256": "a" * 64, "source_url": "https://example.com/a.zip"},
            {"name": "b.zip", "size": 2, "sha256": "b" * 64, "source_url": "https://example.com/b.zip"},
        ]
        first = source_set_hash(components)
        self.assertEqual(first, source_set_hash(components))
        self.assertNotEqual(first, source_set_hash(list(reversed(components))))

    def test_safe_relative_rejects_traversal(self):
        with self.assertRaisesRegex(RuntimeError, "Unsafe repository-relative path"):
            safe_relative("../outside")

    def test_safe_relative_normalizes_windows_separators(self):
        self.assertEqual(safe_relative(r"runtime\sources\game").as_posix(), "runtime/sources/game")


if __name__ == "__main__":
    unittest.main()
