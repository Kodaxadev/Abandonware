#!/usr/bin/env python3
"""Verify that a materialized js-dos bundle matches its audited manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import zipfile

REQUIRED_GENERATED = {
    ".jsdos/dosbox.conf",
    ".jsdos/jsdos.json",
    ".jsdos/provenance.json",
}
FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def fail(message: str) -> None:
    raise RuntimeError(message)


def verify(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bundle_path = Path(manifest["output"])
    if not bundle_path.is_file():
        fail(f"Missing materialized bundle: {bundle_path}")

    with zipfile.ZipFile(bundle_path, "r") as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)):
            fail("Bundle contains duplicate ZIP paths")

        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                fail(f"Unsafe archive path: {name}")

        missing = REQUIRED_GENERATED.difference(names)
        if missing:
            fail(f"Bundle is missing required js-dos metadata: {sorted(missing)}")

        for name in REQUIRED_GENERATED:
            if bundle.getinfo(name).date_time != FIXED_ZIP_DATE:
                fail(f"Generated entry has non-deterministic timestamp: {name}")

        jsdos_meta = json.loads(bundle.read(".jsdos/jsdos.json"))
        if jsdos_meta.get("version") != 1:
            fail("Unsupported .jsdos/jsdos.json version")

        provenance = json.loads(bundle.read(".jsdos/provenance.json"))
        source = manifest["source"]
        checks = {
            "game_id": manifest["id"],
            "title": manifest["title"],
            "version": manifest.get("version"),
            "upstream_url": source["url"],
            "upstream_page": source.get("page"),
            "upstream_size": int(source["size"]),
            "upstream_sha1": source["sha1"].casefold(),
            "copying_policy": source.get("copying_policy"),
            "rights_record": manifest.get("rights_record"),
        }
        for field, expected in checks.items():
            actual = provenance.get(field)
            if field == "upstream_sha1" and isinstance(actual, str):
                actual = actual.casefold()
            if actual != expected:
                fail(
                    f"Provenance mismatch for {field}: expected {expected!r}, got {actual!r}"
                )

        sha256 = provenance.get("upstream_sha256", "")
        if not isinstance(sha256, str) or len(sha256) != 64:
            fail("Provenance is missing a valid SHA-256 source fingerprint")

        launch_target = provenance.get("launch_target")
        if not isinstance(launch_target, str) or launch_target not in names:
            fail(f"Recorded launch target is absent from bundle: {launch_target!r}")

        expected_basename = manifest["launch"]["basename"].casefold()
        if PurePosixPath(launch_target).name.casefold() != expected_basename:
            fail("Recorded launch target does not match manifest basename")

        config = bundle.read(".jsdos/dosbox.conf").decode("utf-8")
        if "mount c ." not in config.casefold():
            fail("DOSBox configuration does not mount the bundled filesystem")
        if expected_basename not in config.casefold():
            fail("DOSBox configuration does not invoke the manifest launch target")

    print(f"Verified {bundle_path} against {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    verify(args.manifest)


if __name__ == "__main__":
    main()
