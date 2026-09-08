#!/usr/bin/env python3
"""Audit a creator-hosted GitHub release archive without executing downloaded content.

This is a non-publishing research lane. It resolves one exact Git tag, selects one named
release asset, downloads it over HTTPS, inventories archive members safely, fingerprints
one required game-data member, and preserves human-readable license/readme/attribution
notices. A successful identity match is not a rights approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
from urllib.parse import quote, urlparse
import urllib.request
import zipfile

USER_AGENT = "Kodaxa-Abandonware-GitHub-Release-Audit/1.0"
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_NOTICE_BYTES = 256 * 1024
NOTICE_TOKENS = (
    "license",
    "licence",
    "copying",
    "copyright",
    "readme",
    "authors",
    "credits",
    "patents",
    "notice",
    "attribution",
    "third-party",
    "third_party",
)


def digest_bytes(raw: bytes, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(raw)
    return hasher.hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(value: str) -> PurePosixPath:
    normalized = PurePosixPath(value.replace("\\", "/"))
    if not normalized.parts or normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"Unsafe archive member path: {value!r}")
    return normalized


def notice_name(value: str) -> bool:
    name = value.rsplit("/", 1)[-1].casefold()
    return any(token in name for token in NOTICE_TOKENS)


def decode_notice(data: bytes) -> str | None:
    data = data[:MAX_NOTICE_BYTES]
    if b"\x00" in data:
        return None
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def request_json(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "api.github.com":
        raise RuntimeError(f"GitHub API URL must use https://api.github.com: {url}")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, destination: Path, expected_size: int | None = None) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }:
        raise RuntimeError(f"Unexpected GitHub release download host: {parsed.hostname!r}")

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_ARCHIVE_BYTES:
            raise RuntimeError(f"Release archive exceeds {MAX_ARCHIVE_BYTES} bytes")

        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_ARCHIVE_BYTES:
                raise RuntimeError(f"Release archive exceeds {MAX_ARCHIVE_BYTES} bytes")
            output.write(chunk)

    if expected_size is not None and destination.stat().st_size != expected_size:
        raise RuntimeError(
            f"Release asset size mismatch: expected {expected_size}, got {destination.stat().st_size}"
        )


def resolve_tag_commit(repository_full_name: str, tag: str) -> dict:
    encoded_tag = quote(tag, safe="")
    record = request_json(
        f"https://api.github.com/repos/{repository_full_name}/git/ref/tags/{encoded_tag}"
    )
    obj = record.get("object", {})
    object_sha = obj.get("sha")
    object_type = obj.get("type")
    if not object_sha or not object_type:
        raise RuntimeError(f"GitHub tag ref is incomplete for {repository_full_name}@{tag}")

    if object_type == "commit":
        return {
            "ref": record.get("ref"),
            "tag_object": None,
            "commit": object_sha,
        }

    if object_type != "tag":
        raise RuntimeError(f"Unsupported Git tag object type: {object_type!r}")

    tag_record = request_json(
        f"https://api.github.com/repos/{repository_full_name}/git/tags/{object_sha}"
    )
    target = tag_record.get("object", {})
    if target.get("type") != "commit" or not target.get("sha"):
        raise RuntimeError("Annotated Git tag does not resolve directly to a commit")
    return {
        "ref": record.get("ref"),
        "tag_object": object_sha,
        "commit": target["sha"],
    }


def fingerprint_match(matches: list[tuple[str, bytes]], required_suffix: str) -> dict:
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one archive member ending in {required_suffix!r}; "
            f"found {[name for name, _ in matches]}"
        )
    name, raw = matches[0]
    return {
        "path": name,
        "size": len(raw),
        "md5": hashlib.md5(raw, usedforsecurity=False).hexdigest(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def inspect_zip(path: Path, required_suffix: str) -> tuple[list[dict], dict, list[dict]]:
    members: list[dict] = []
    notices: list[dict] = []
    matches: list[tuple[str, bytes]] = []
    suffix = safe_path(required_suffix).as_posix().casefold()

    with zipfile.ZipFile(path, "r") as archive:
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
            lower = member_name.casefold()
            if lower.endswith(suffix):
                matches.append((member_name, archive.read(info)))
            if notice_name(member_name):
                raw = archive.read(info)
                notices.append({
                    "path": member_name,
                    "size": info.file_size,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "text": decode_notice(raw),
                })

    return members, fingerprint_match(matches, required_suffix), notices


def inspect_tar(path: Path, required_suffix: str) -> tuple[list[dict], dict, list[dict]]:
    members: list[dict] = []
    notices: list[dict] = []
    matches: list[tuple[str, bytes]] = []
    suffix = safe_path(required_suffix).as_posix().casefold()

    with tarfile.open(path, "r:*") as archive:
        for info in archive.getmembers():
            member = safe_path(info.name)
            member_name = member.as_posix()
            if info.issym() or info.islnk():
                raise RuntimeError(f"Release archive contains link member: {member_name}")
            members.append({"path": member_name, "size": info.size, "directory": info.isdir()})
            if not info.isfile():
                continue
            handle = archive.extractfile(info)
            if handle is None:
                raise RuntimeError(f"Could not read tar member: {member_name}")
            raw = handle.read()
            lower = member_name.casefold()
            if lower.endswith(suffix):
                matches.append((member_name, raw))
            if notice_name(member_name):
                notices.append({
                    "path": member_name,
                    "size": info.size,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "text": decode_notice(raw),
                })

    return members, fingerprint_match(matches, required_suffix), notices


def inspect_archive(path: Path, filename: str, required_suffix: str):
    lower = filename.casefold()
    if lower.endswith(".zip"):
        return inspect_zip(path, required_suffix)
    if lower.endswith(".tar.gz") or lower.endswith(".tgz") or lower.endswith(".tar"):
        return inspect_tar(path, required_suffix)
    raise RuntimeError(f"Unsupported GitHub release archive type: {filename}")


def audit(manifest_path: Path, output_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repository = manifest["repository_full_name"]
    tag = manifest["release_tag"]
    expected_filename = manifest["expected_filename"]
    required_suffix = manifest["required_member_suffix"]
    expected_payload = manifest["expected_payload"]

    if repository.count("/") != 1 or any(part in {"", ".", ".."} for part in repository.split("/")):
        raise RuntimeError(f"Invalid repository_full_name: {repository!r}")

    tag_identity = resolve_tag_commit(repository, tag)
    expected_tag_commit = manifest.get("expected_tag_commit")
    if expected_tag_commit and tag_identity["commit"].casefold() != expected_tag_commit.casefold():
        raise RuntimeError(
            f"Tag commit mismatch for {repository}@{tag}: expected {expected_tag_commit}, "
            f"got {tag_identity['commit']}"
        )

    release = request_json(
        f"https://api.github.com/repos/{repository}/releases/tags/{quote(tag, safe='')}"
    )
    if release.get("tag_name") != tag:
        raise RuntimeError(f"Release tag mismatch: expected {tag}, got {release.get('tag_name')!r}")

    assets = release.get("assets", [])
    matches = [asset for asset in assets if asset.get("name") == expected_filename]
    if len(matches) != 1:
        raise RuntimeError(
            f"Could not uniquely select GitHub release asset {expected_filename!r}; "
            f"available names: {[asset.get('name') for asset in assets]}"
        )
    asset = matches[0]
    asset_url = asset.get("browser_download_url")
    if not asset_url:
        raise RuntimeError("GitHub release asset has no browser_download_url")
    asset_size = int(asset.get("size", 0))
    if asset_size <= 0 or asset_size > MAX_ARCHIVE_BYTES:
        raise RuntimeError(f"Unexpected GitHub release asset size: {asset_size}")

    with tempfile.TemporaryDirectory(prefix="abandonware-github-release-") as temp_dir:
        archive_path = Path(temp_dir) / expected_filename
        download(asset_url, archive_path, asset_size)
        members, payload, notices = inspect_archive(archive_path, expected_filename, required_suffix)
        archive_hash = sha256(archive_path)
        archive_size = archive_path.stat().st_size

    exact_match = (
        payload["md5"].casefold() == str(expected_payload["md5"]).casefold()
        and payload["size"] == int(expected_payload["size"])
    )

    record = {
        "schema": 1,
        "id": manifest["id"],
        "title": manifest.get("title"),
        "repository_full_name": repository,
        "release_tag": tag,
        "release_id": release.get("id"),
        "release_page": release.get("html_url"),
        "published_at": release.get("published_at"),
        "tag_identity": tag_identity,
        "asset": {
            "name": expected_filename,
            "id": asset.get("id"),
            "size": archive_size,
            "sha256": archive_hash,
            "download_url": asset_url,
        },
        "required_payload": payload,
        "expected_payload": expected_payload,
        "payload_matches_expected_identity": exact_match,
        "member_count": len(members),
        "members": members,
        "notices": notices,
        "decision": "IDENTITY_MATCH_REQUIRES_RIGHTS_REVIEW" if exact_match else "IDENTITY_MISMATCH",
        "warning": (
            "This is a non-publishing identity audit. A matching author-hosted release payload "
            "does not itself authorize redistribution; production still requires the candidate's "
            "rights decision and all third-party exceptions to pass."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "id": record["id"],
        "repository": repository,
        "tag": tag,
        "tag_commit": tag_identity["commit"],
        "asset": expected_filename,
        "asset_size": archive_size,
        "asset_sha256": archive_hash,
        "payload": payload,
        "payload_matches_expected_identity": exact_match,
        "notice_paths": [notice["path"] for notice in notices],
        "decision": record["decision"],
    }, indent=2))

    if not exact_match:
        raise RuntimeError(
            f"GitHub author release payload does not match expected identity for {manifest['id']}"
        )

    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.manifest, args.output)


if __name__ == "__main__":
    main()
