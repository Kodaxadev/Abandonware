#!/usr/bin/env python3
"""Audit a candidate game ZIP without publishing or materializing it.

The candidate lane is intentionally separate from hosted-game manifests. It verifies the
exact source artifact, rejects unsafe paths, inventories archive structure, and records
license/readme/copyright notices for human rights review. Passing this tool does NOT make
a game hostable or browser-ready.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import urllib.request
import zipfile

NOTICE_TOKENS = ("license", "licence", "readme", "copying", "copyright", "legal")
MAX_NOTICE_BYTES = 256 * 1024
MAX_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(name: str) -> PurePosixPath:
    normalized = PurePosixPath(name.replace("\\", "/"))
    if not normalized.parts or normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"Unsafe archive member path: {name!r}")
    return normalized


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Kodaxa-Abandonware-Candidate-Audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_ARCHIVE_BYTES:
            raise RuntimeError(f"Candidate archive exceeds {MAX_ARCHIVE_BYTES} bytes")
        with destination.open("wb") as output:
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise RuntimeError(f"Candidate archive exceeds {MAX_ARCHIVE_BYTES} bytes")
                output.write(chunk)


def decode_notice(data: bytes) -> str:
    data = data[:MAX_NOTICE_BYTES]
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def audit(manifest_path: Path, output_path: Path | None) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate_id = manifest["id"]
    source = manifest["source"]
    expected_sha = source["sha256"].casefold()

    if len(expected_sha) != 64:
        raise RuntimeError("Candidate SHA-256 must contain exactly 64 hexadecimal characters")
    if not source["url"].startswith("https://"):
        raise RuntimeError("Candidate source URL must use HTTPS")

    with tempfile.TemporaryDirectory(prefix="abandonware-candidate-") as temp_dir:
        archive_path = Path(temp_dir) / "candidate.zip"
        print(f"Downloading candidate {candidate_id}: {source['url']}")
        download(source["url"], archive_path)

        actual_sha = sha256(archive_path)
        if actual_sha.casefold() != expected_sha:
            raise RuntimeError(
                f"SHA-256 mismatch for {candidate_id}: expected {expected_sha}, got {actual_sha}"
            )

        members: list[dict] = []
        notices: list[dict] = []
        direct_root_files: list[str] = []
        top_level_names: set[str] = set()

        with zipfile.ZipFile(archive_path, "r") as archive:
            for info in archive.infolist():
                path = safe_path(info.filename)
                top_level_names.add(path.parts[0])
                members.append({
                    "path": path.as_posix(),
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                    "directory": info.is_dir(),
                })

                if not info.is_dir() and len(path.parts) == 1:
                    direct_root_files.append(path.name)

                if info.is_dir():
                    continue

                lower_name = path.name.casefold()
                if any(token in lower_name for token in NOTICE_TOKENS):
                    raw = archive.read(info)
                    notices.append({
                        "path": path.as_posix(),
                        "size": info.file_size,
                        "text": decode_notice(raw),
                    })

        audit_record = {
            "schema": 1,
            "candidate_id": candidate_id,
            "title": manifest.get("title"),
            "source_url": source["url"],
            "source_page": source.get("page"),
            "sha256": actual_sha,
            "archive_size": archive_path.stat().st_size,
            "member_count": len(members),
            "top_level_names": sorted(top_level_names),
            "direct_root_files": sorted(direct_root_files),
            "notices": notices,
            "members": members,
            "decision": "REQUIRES_HUMAN_RIGHTS_REVIEW",
            "warning": "A successful package audit is provenance evidence only; it does not authorize hosting.",
        }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(audit_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_id": audit_record["candidate_id"],
        "sha256": audit_record["sha256"],
        "archive_size": audit_record["archive_size"],
        "member_count": audit_record["member_count"],
        "top_level_names": audit_record["top_level_names"],
        "direct_root_files": audit_record["direct_root_files"],
        "notice_paths": [notice["path"] for notice in notices],
        "decision": audit_record["decision"],
    }, indent=2))

    for notice in notices:
        print(f"\n===== NOTICE: {notice['path']} ({notice['size']} bytes) =====")
        print(notice["text"][:MAX_NOTICE_BYTES])
        print(f"===== END NOTICE: {notice['path']} =====")

    if not notices:
        print("\nWARNING: no readme/license/copyright-style notice files were found in the package.")

    return audit_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit(args.manifest, args.output)


if __name__ == "__main__":
    main()
