#!/usr/bin/env python3
"""Audit an exact author-controlled ZIP release without publishing it.

This lane is for direct creator/developer download URLs that are not GitHub Releases. The
manifest must pin an expected size plus at least one strong external digest (SHA-512 or
SHA-256). The audit downloads the exact HTTPS URL, verifies those pins, safely inventories
the ZIP, validates one required detector payload, preserves notice-style files, and emits a
SHA-256 suitable for later production manifests. Nothing from the archive is executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from urllib.parse import urlparse
import urllib.request
import zipfile

USER_AGENT = "Kodaxa-Abandonware-Direct-Release-Audit/1.0"
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_NOTICE_BYTES = 256 * 1024
NOTICE_TOKENS = (
    "license", "licence", "copying", "copyright", "readme", "authors",
    "credits", "notice", "attribution", "third-party", "third_party",
)


def safe_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value.replace("\\", "/"))
    if not path.parts or path.is_absolute() or ".." in path.parts:
        raise RuntimeError(f"Unsafe archive member path: {value!r}")
    return path


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def notice_name(value: str) -> bool:
    name = value.rsplit("/", 1)[-1].casefold()
    return any(token in name for token in NOTICE_TOKENS)


def decode_notice(raw: bytes) -> str | None:
    raw = raw[:MAX_NOTICE_BYTES]
    if b"\x00" in raw:
        return None
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def download(url: str, destination: Path, allowed_host: str, expected_size: int) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != allowed_host:
        raise RuntimeError(
            f"Direct release URL must use HTTPS on {allowed_host}: {url}"
        )
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as output:
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_ARCHIVE_BYTES:
                raise RuntimeError(f"Archive exceeds {MAX_ARCHIVE_BYTES} bytes")
            output.write(chunk)
    actual_size = destination.stat().st_size
    if actual_size != expected_size:
        raise RuntimeError(
            f"Direct release size mismatch: expected {expected_size}, got {actual_size}"
        )


def audit(manifest_path: Path, output_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = manifest["source"]
    url = source["url"]
    expected_size = int(source["size"])
    allowed_host = source["allowed_host"]
    expected_sha512 = str(source.get("sha512", "")).casefold()
    expected_sha256 = str(source.get("sha256", "")).casefold()
    if not expected_sha512 and not expected_sha256:
        raise RuntimeError("Direct release manifest must pin SHA-512 or SHA-256")

    required = manifest["required_payload"]
    required_name = safe_path(required["filename"]).as_posix().casefold()
    expected_payload_md5 = str(required["md5"]).casefold()
    expected_payload_size = int(required["size"])

    with tempfile.TemporaryDirectory(prefix="abandonware-direct-release-") as temp_dir:
        archive_path = Path(temp_dir) / "release.zip"
        download(url, archive_path, allowed_host, expected_size)
        actual_sha512 = digest(archive_path, "sha512")
        actual_sha256 = digest(archive_path, "sha256")
        if expected_sha512 and actual_sha512 != expected_sha512:
            raise RuntimeError(
                f"SHA-512 mismatch: expected {expected_sha512}, got {actual_sha512}"
            )
        if expected_sha256 and actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
            )

        members: list[dict] = []
        notices: list[dict] = []
        payload_matches: list[dict] = []
        with zipfile.ZipFile(archive_path, "r") as archive:
            for info in archive.infolist():
                member = safe_path(info.filename)
                member_name = member.as_posix()
                members.append({
                    "path": member_name,
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                    "directory": info.is_dir(),
                })
                if info.is_dir():
                    continue
                raw: bytes | None = None
                if member_name.casefold().endswith(required_name):
                    raw = archive.read(info)
                    payload_matches.append({
                        "path": member_name,
                        "size": len(raw),
                        "md5": hashlib.md5(raw, usedforsecurity=False).hexdigest(),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    })
                if notice_name(member_name):
                    if raw is None:
                        raw = archive.read(info)
                    notices.append({
                        "path": member_name,
                        "size": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "text": decode_notice(raw),
                    })

    if len(payload_matches) != 1:
        raise RuntimeError(
            f"Expected exactly one payload ending in {required['filename']!r}; "
            f"found {[item['path'] for item in payload_matches]}"
        )
    payload = payload_matches[0]
    if payload["size"] != expected_payload_size or payload["md5"].casefold() != expected_payload_md5:
        raise RuntimeError(
            f"Detector payload mismatch for {manifest['id']}: {payload}"
        )

    record = {
        "schema": 1,
        "id": manifest["id"],
        "title": manifest.get("title"),
        "source_page": source.get("page"),
        "source_url": url,
        "archive_size": expected_size,
        "archive_sha256": actual_sha256,
        "archive_sha512": actual_sha512,
        "required_payload": payload,
        "member_count": len(members),
        "members": members,
        "notices": notices,
        "decision": "IDENTITY_MATCH_REQUIRES_RIGHTS_REVIEW",
        "warning": (
            "This non-publishing audit establishes artifact identity only. Production still "
            "requires an independent rights decision that covers the complete game data."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "id": record["id"],
        "source_url": url,
        "archive_size": expected_size,
        "archive_sha256": actual_sha256,
        "archive_sha512": actual_sha512,
        "payload": payload,
        "notice_paths": [notice["path"] for notice in notices],
        "decision": record["decision"],
    }, indent=2))
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.manifest, args.output)


if __name__ == "__main__":
    main()
