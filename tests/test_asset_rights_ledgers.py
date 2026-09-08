#!/usr/bin/env python3
"""Validate machine-readable third-party asset rights ledgers.

A ledger is research evidence, but once a candidate links one it becomes part of the
production rights boundary. Counts, source identity, preserved credit evidence, and
blocking state must remain internally consistent. Production approval is impossible while
any linked ledger still contains a production-blocking asset.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APPROVED_CANDIDATE_STATUSES = {"APPROVED", "APPROVED_OPEN_LICENSE"}
CLEAR_STATES = {
    "CLEAR_WITH_ATTRIBUTION",
    "CLEAR_SHAREALIKE",
    "CLEAR_CC0",
    "CLEAR_CC0_DEVELOPER_RECORD",
}
BLOCKING_STATES = {
    "BLOCKING_NONCOMMERCIAL",
    "BLOCKING_SAMPLING_PLUS_WHOLE_SOUND",
    "UNRESOLVED_SOURCE_LICENSE",
    "PROVISIONAL_HISTORICAL_CC0",
    "UNRESOLVED_PERMISSION",
    "UNRESOLVED_REDISTRIBUTION_SCOPE",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def linked_candidates() -> list[tuple[Path, dict, Path, dict]]:
    records: list[tuple[Path, dict, Path, dict]] = []
    for candidate_path in sorted((ROOT / "research" / "candidates").glob("*.json")):
        candidate = load_json(candidate_path)
        ledger_value = candidate.get("asset_rights_ledger")
        if not ledger_value:
            continue
        ledger_path = ROOT / ledger_value
        if not ledger_path.is_file():
            raise AssertionError(
                f"Candidate {candidate.get('id')} points at missing asset ledger {ledger_value}"
            )
        records.append((candidate_path, candidate, ledger_path, load_json(ledger_path)))
    return records


class AssetRightsLedgerTests(unittest.TestCase):
    def test_linked_ledgers_are_internally_consistent(self):
        for candidate_path, candidate, ledger_path, ledger in linked_candidates():
            game_id = candidate["id"]
            with self.subTest(game=game_id):
                self.assertEqual(ledger.get("game_id"), game_id)
                self.assertIsInstance(ledger.get("assets"), list)
                self.assertTrue(ledger["assets"], f"Empty asset ledger: {ledger_path}")

                asset_ids = [asset.get("id") for asset in ledger["assets"]]
                self.assertTrue(all(asset_ids), f"Asset ledger contains an id-less record: {ledger_path}")
                self.assertEqual(
                    len(asset_ids),
                    len(set(asset_ids)),
                    f"Duplicate asset id in {ledger_path}",
                )

                blocking = [asset for asset in ledger["assets"] if asset.get("production_blocking") is True]
                clear = [asset for asset in ledger["assets"] if asset.get("production_blocking") is False]
                self.assertEqual(
                    len(blocking) + len(clear),
                    len(ledger["assets"]),
                    f"Every asset must declare boolean production_blocking in {ledger_path}",
                )

                summary = ledger.get("summary", {})
                self.assertEqual(summary.get("asset_records"), len(ledger["assets"]))
                self.assertEqual(summary.get("production_blocking_records"), len(blocking))
                self.assertEqual(summary.get("clear_records"), len(clear))

                known_restrictive = [
                    asset["id"]
                    for asset in ledger["assets"]
                    if str(asset.get("rights_state", "")).startswith("BLOCKING_")
                ]
                unresolved_or_provisional = [
                    asset["id"]
                    for asset in ledger["assets"]
                    if asset.get("rights_state") in {
                        "UNRESOLVED_SOURCE_LICENSE",
                        "PROVISIONAL_HISTORICAL_CC0",
                        "UNRESOLVED_PERMISSION",
                        "UNRESOLVED_REDISTRIBUTION_SCOPE",
                    }
                ]
                self.assertEqual(summary.get("known_restrictive_records"), len(known_restrictive))
                self.assertEqual(summary.get("unresolved_or_provisional_records"), len(unresolved_or_provisional))
                self.assertEqual(summary.get("known_restrictive_ids"), known_restrictive)
                self.assertEqual(summary.get("unresolved_or_provisional_ids"), unresolved_or_provisional)

                for asset in ledger["assets"]:
                    state = asset.get("rights_state")
                    self.assertIn(
                        state,
                        CLEAR_STATES | BLOCKING_STATES,
                        f"Unknown rights_state {state!r} for {asset.get('id')} in {ledger_path}",
                    )
                    if state in CLEAR_STATES:
                        self.assertFalse(
                            asset["production_blocking"],
                            f"Clear asset {asset['id']} is incorrectly blocking production",
                        )
                    else:
                        self.assertTrue(
                            asset["production_blocking"],
                            f"Unresolved/restrictive asset {asset['id']} must fail closed",
                        )

    def test_ledger_source_identity_matches_preserved_source(self):
        for _candidate_path, candidate, ledger_path, ledger in linked_candidates():
            game_id = candidate["id"]
            source_record_value = candidate.get("corresponding_source_record")
            with self.subTest(game=game_id):
                self.assertTrue(source_record_value, f"Ledger-backed candidate {game_id} has no source record")
                source_record = ROOT / source_record_value
                self.assertTrue(source_record.is_file(), f"Missing source provenance: {source_record}")
                source = load_json(source_record)
                identity = ledger.get("source_identity", {})
                self.assertEqual(identity.get("commit"), source.get("commit"))
                self.assertEqual(identity.get("tree"), source.get("tree"))
                self.assertEqual(identity.get("repository_url"), source.get("repository_url"))

                preserved_by_source_path = {
                    notice["source_path"]: notice for notice in source.get("preserved_notices", [])
                }
                for evidence in ledger.get("credits_evidence", []):
                    evidence_path = ROOT / evidence["path"]
                    self.assertTrue(evidence_path.is_file(), f"Missing ledger credit evidence: {evidence_path}")
                    self.assertEqual(sha256(evidence_path), evidence["sha256"])
                    source_notice = preserved_by_source_path.get(evidence.get("source_path"))
                    self.assertIsNotNone(
                        source_notice,
                        f"Ledger evidence is not preserved in source provenance: {evidence.get('source_path')}",
                    )
                    self.assertEqual(source_notice["sha256"], evidence["sha256"])

    def test_approved_candidates_cannot_keep_blocking_asset_ledgers(self):
        for _candidate_path, candidate, ledger_path, ledger in linked_candidates():
            if candidate.get("status") not in APPROVED_CANDIDATE_STATUSES:
                continue
            blocking = [asset["id"] for asset in ledger["assets"] if asset.get("production_blocking")]
            with self.subTest(game=candidate["id"]):
                self.assertFalse(
                    blocking,
                    (
                        f"Approved candidate {candidate['id']} still has production-blocking assets "
                        f"in {ledger_path}: {blocking}"
                    ),
                )
                self.assertNotIn(
                    str(ledger.get("status", "")),
                    {"HOLD", "HOLD_BLOCKING_ASSETS"},
                    f"Approved candidate {candidate['id']} still has a HOLD asset ledger",
                )


if __name__ == "__main__":
    unittest.main()
