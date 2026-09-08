#!/usr/bin/env python3
"""Audit an author-controlled ZIP release without publishing or executing it.

Pinned mode verifies an exact size plus SHA-256/SHA-512 before using the artifact as identity
evidence. Discovery mode exists only to fingerprint a fixed creator URL when no independent
digest survives; its output is explicitly non-final and must be copied back into the manifest
and re-run in pinned mode before the artifact can support production.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import urlparse
import urllib.request
import zipfile

USER_AGENT = "Kodaxa-Abandonware-Direct-Release-Audit/1.1"
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


def download(
    url: str,
    destination: Path,
    allowed_host: str,
    *,
    expected_size: int | None,
    max_size: int,
) -> int:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != allowed_host:
        raise RuntimeError(f"Direct release URL must use HTTPS on {allowed_host}: {url}")
    if max_size <= 0 or max_size > MAX_ARCHIVE_BYTES:
        raise RuntimeError(f"Invalid max_size: {max_size}")

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response, destination.open("wb") as output:
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size:
                raise RuntimeError(f"Archive exceeds manifest max_size of {max_size} bytes")
            output.write(chunk)

    actual_size = destination.stat().st_size
    if expected_size is not None and actual_size != expected_size:
        raise RuntimeError(
            f"Direct release size mismatch: expected {expected_size}, got {actual_size}"
        )
    return actual_size


def audit(manifest_path: Path, output_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = manifest["source"]
    url = source["url"]
    allowed_host = source["allowed_host"]
    discovery_mode = bool(source.get("discovery_mode", False))
    expected_size = int(source["size"]) if source.get("size") is not None else None
    max_size = int(source.get("max_size", expected_size or MAX_ARCHIVE_BYTES))
    expected_sha512 = str(source.get("sha512", "")).casefold()
    expected_sha256 = str(source.get("sha256", "")).casefold()
    has_digest_pin = bool(expected_sha512 or expected_sha256)

    if not has_digest_pin and not discovery_mode:
        raise RuntimeError(
            "Direct release manifest must pin SHA-512/SHA-256 or explicitly use discovery_mode"
        )
    if discovery_mode and has_digest_pin:
        raise RuntimeError("discovery_mode must be disabled once a digest is pinned")
    if not discovery_mode and expected_size is None:
        raise RuntimeError("Pinned direct release manifests must include exact size")

    required = manifest.get("required_payload")
    required_name = None
    expected_payload_md5 = None
    expected_payload_size = None
    if required is not None:
        required_name = safe_path(required["filename"]).as_posix().casefold()
        expected_payload_md5 = str(required["md5"]).casefold()
        expected_payload_size = int(required["size"])

    with tempfile.TemporaryDirectory(prefix="abandonware-direct-release-") as temp_dir:
        archive_path = Path(temp_dir) / "release.zip"
        actual_size = download(
            url,
            archive_path,
            allowed_host,
            expected_size=expected_size,
            max_size=max_size,
        )
        actual_sha512 = digest(archive_path, "sha512")
        actual_sha256 = digest(archive_path, "sha256")
        if expected_sha512 and actual_sha512 != expected_sha512:
            raise RuntimeError(f"SHA-512 mismatch: expected {expected_sha512}, got {actual_sha512}")
        if expected_sha256 and actual_sha256 != expected_sha256:
            raise RuntimeError(f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}")

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
                if required_name and member_name.casefold().endswith(required_name):
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

    payload = None
    if required is not None:
        if len(payload_matches) != 1:
            raise RuntimeError(
                f"Expected exactly one payload ending in {required['filename']!r}; "
                f"found {[item['path'] for item in payload_matches]}"
            )
        payload = payload_matches[0]
        if payload["size"] != expected_payload_size or payload["md5"].casefold() != expected_payload_md5:
            raise RuntimeError(f"Detector payload mismatch for {manifest['id']}: {payload}")

    decision = (
        "HASH_DISCOVERY_REQUIRES_PINNED_RERUN"
        if discovery_mode
        else "IDENTITY_MATCH_REQUIRES_RIGHTS_REVIEW"
    )
    record = {
        "schema": 2,
        "id": manifest["id"],
        "title": manifest.get("title"),
        "source_page": source.get("page"),
        "source_url": url,
        "discovery_mode": discovery_mode,
        "archive_size": actual_size,
        "archive_sha256": actual_sha256,
        "archive_sha512": actual_sha512,
        "required_payload": payload,
        "member_count": len(members),
        "members": members,
        "notices": notices,
        "decision": decision,
        "warning": (
            "Discovery-mode hashes are observations, not immutable pins; copy the observed size/hash "
            "back into the manifest and re-run with discovery_mode disabled. This non-publishing "
            "audit never substitutes for an independent rights decision."
            if discovery_mode
            else "This non-publishing audit establishes artifact identity only. Production still "
            "requires an independent rights decision covering the complete game data."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "id": record["id"],
        "source_url": url,
        "discovery_mode": discovery_mode,
        "archive_size": actual_size,
        "archive_sha256": actual_sha256,
        "archive_sha512": actual_sha512,
        "payload": payload,
        "notice_paths": [notice["path"] for notice in notices],
        "decision": decision,
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
