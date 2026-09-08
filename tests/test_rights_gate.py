#!/usr/bin/env python3
"""Fail-closed production rights gates.

Research candidates are allowed to be incomplete, blocked, or under review. Production
manifests are not. If a production game has a candidate record, that record must carry an
explicit production-approved state. The generated ScummVM provenance must also match the
production manifest exactly so stale materialized games cannot survive a rights withdrawal.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APPROVED_CANDIDATE_STATUSES = {
    "APPROVED",
    "APPROVED_OPEN_LICENSE",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_games() -> list[dict]:
    build = load_json(ROOT / "runtime" / "scummvm-build.json")
    games = build.get("games")
    if games is None:
        games = [build["game"]]
    return games


def provenance_games() -> list[dict]:
    provenance = load_json(ROOT / "runtime" / "scummvm" / "PROVENANCE.json")
    games = provenance.get("games")
    if games is None:
        games = [provenance["game"]]
    return games


class ProductionRightsGateTests(unittest.TestCase):
    def test_scummvm_manifest_rejects_nonapproved_candidates(self):
        for game in manifest_games():
            candidate_path = ROOT / "research" / "candidates" / f"{game['id']}.json"
            if not candidate_path.exists():
                continue

            candidate = load_json(candidate_path)
            with self.subTest(game=game["id"]):
                self.assertEqual(
                    candidate.get("id"),
                    game["id"],
                    f"Candidate identity mismatch in {candidate_path}",
                )
                self.assertIn(
                    candidate.get("status"),
                    APPROVED_CANDIDATE_STATUSES,
                    (
                        f"Production game {game['id']} is backed by candidate state "
                        f"{candidate.get('status')!r}; only explicit production-approved "
                        "candidate states may enter runtime/scummvm-build.json"
                    ),
                )

                decision_record = candidate.get("decision_record")
                if decision_record:
                    self.assertTrue(
                        (ROOT / decision_record).is_file(),
                        f"Approved candidate {game['id']} points at missing decision record {decision_record}",
                    )

    def test_generated_scummvm_games_exactly_match_manifest(self):
        expected = {game["id"] for game in manifest_games()}
        materialized = {game["id"] for game in provenance_games()}
        self.assertEqual(
            materialized,
            expected,
            (
                "Materialized ScummVM provenance differs from the production manifest. "
                "This can leave withdrawn or unreviewed game data publicly reachable."
            ),
        )

    def test_materialized_candidates_are_still_approved(self):
        for game in provenance_games():
            candidate_path = ROOT / "research" / "candidates" / f"{game['id']}.json"
            if not candidate_path.exists():
                continue

            candidate = load_json(candidate_path)
            with self.subTest(game=game["id"]):
                self.assertIn(
                    candidate.get("status"),
                    APPROVED_CANDIDATE_STATUSES,
                    (
                        f"Materialized game {game['id']} is backed by candidate state "
                        f"{candidate.get('status')!r}; generated runtime must be purged when "
                        "a candidate leaves an approved state"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
