#!/usr/bin/env python3
"""Audit a free itch.io release archive without executing downloaded content.

The audit follows itch.io's public CSRF/signed-download flow, selects one exact author
upload by filename, downloads it, inventories archive members safely, fingerprints a
required payload member, and records notice files. It never extracts or executes binaries.
"""

from __future__ import annotations

import argparse
from http.cookiejar import CookieJar
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile
from urllib.parse import urlencode, urlparse
import urllib.request
import zipfile

USER_AGENT = "Kodaxa-Abandonware-Author-Release-Audit/1.0"
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_NOTICE_BYTES = 256 * 1024
NOTICE_TOKENS = ("license", "licence", "copying", "copyright", "readme")


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


def parse_page(page_html: str) -> dict:
    csrf = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)', page_html, re.I)
    if csrf is None:
        csrf = re.search(r'csrf_token["\']?\s+value=["\']([^"\']+)', page_html, re.I)

    upload_ids = re.findall(r'data-upload_id=["\'](\d+)', page_html, re.I)
    upload_infos: list[dict] = []
    for match in re.finditer(
        r'<a[^>]*data-upload_id=["\'](\d+)["\'][^>]*>[\s\S]*?'
        r'<strong[^>]*class=["\'][^"\']*\bname\b[^"\']*["\'][^>]*>([^<]+)</strong>',
        page_html,
        re.I,
    ):
        upload_infos.append({"id": match.group(1), "name": html.unescape(match.group(2)).strip()})

    return {
        "csrf": html.unescape(csrf.group(1)) if csrf else "",
        "upload_ids": list(dict.fromkeys(upload_ids)),
        "upload_infos": upload_infos,
    }


def request(opener: urllib.request.OpenerDirector, url: str, *, data: dict | None = None,
            referer: str | None = None) -> urllib.response.addinfourl:
    headers = {"User-Agent": USER_AGENT}
    body = None
    if data is not None:
        body = urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, data=body, headers=headers)
    return opener.open(req, timeout=120)


def read_text_response(response) -> str:
    content = response.read()
    return content.decode("utf-8", errors="replace")


def download(opener: urllib.request.OpenerDirector, url: str, destination: Path) -> None:
    with request(opener, url) as response, destination.open("wb") as output:
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_ARCHIVE_BYTES:
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


def decode_notice(data: bytes) -> str:
    data = data[:MAX_NOTICE_BYTES]
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def inspect_zip(path: Path, required_suffix: str) -> tuple[list[dict], dict, list[dict]]:
    members: list[dict] = []
    notices: list[dict] = []
    matches: list[tuple[str, bytes]] = []
    suffix = safe_path(required_suffix).as_posix().casefold()

    with zipfile.ZipFile(path, "r") as archive:
        for info in archive.infolist():
            member = safe_path(info.filename)
            member_name = member.as_posix()
            members.append({"path": member_name, "size": info.file_size, "directory": info.is_dir()})
            if info.is_dir():
                continue
            lower = member_name.casefold()
            if lower.endswith(suffix):
                matches.append((member_name, archive.read(info)))
            if any(token in member.name.casefold() for token in NOTICE_TOKENS):
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
            if any(token in member.name.casefold() for token in NOTICE_TOKENS):
                notices.append({
                    "path": member_name,
                    "size": info.size,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "text": decode_notice(raw),
                })

    return members, fingerprint_match(matches, required_suffix), notices


def fingerprint_match(matches: list[tuple[str, bytes]], required_suffix: str) -> dict:
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one archive member ending in {required_suffix!r}; found "
            f"{[name for name, _ in matches]}"
        )
    name, raw = matches[0]
    return {
        "path": name,
        "size": len(raw),
        "md5": hashlib.md5(raw, usedforsecurity=False).hexdigest(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def inspect_archive(path: Path, filename: str, required_suffix: str):
    lower = filename.casefold()
    if lower.endswith(".zip"):
        return inspect_zip(path, required_suffix)
    if lower.endswith(".tar.gz") or lower.endswith(".tgz") or lower.endswith(".tar"):
        return inspect_tar(path, required_suffix)
    raise RuntimeError(f"Unsupported author release archive type: {filename}")


def audit(manifest_path: Path, output_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    game_url = manifest["game_url"].rstrip("/")
    parsed = urlparse(game_url)
    expected_host = manifest["allowed_host"]
    if parsed.scheme != "https" or parsed.hostname != expected_host:
        raise RuntimeError(f"Author release URL must be HTTPS on {expected_host}")

    expected_filename = manifest["expected_filename"]
    required_suffix = manifest["required_member_suffix"]
    expected_payload = manifest["expected_payload"]

    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    with request(opener, game_url) as response:
        page = parse_page(read_text_response(response))
    if not page["csrf"]:
        raise RuntimeError("Could not extract itch.io CSRF token from author page")

    initial_body = {"csrf_token": page["csrf"]}
    if page["upload_ids"]:
        initial_body["upload_id"] = page["upload_ids"][0]
    with request(opener, f"{game_url}/download_url", data=initial_body, referer=game_url) as response:
        download_page_url = json.loads(read_text_response(response)).get("url")
    if not download_page_url:
        raise RuntimeError("itch.io did not return a signed download page URL")

    with request(opener, download_page_url) as response:
        download_page = parse_page(read_text_response(response))
    csrf = download_page["csrf"] or page["csrf"]
    infos = download_page["upload_infos"] or page["upload_infos"]
    matches = [item for item in infos if item["name"] == expected_filename]
    if len(matches) != 1:
        raise RuntimeError(
            f"Could not uniquely select author upload {expected_filename!r}; "
            f"available names: {[item['name'] for item in infos]}"
        )
    upload_id = matches[0]["id"]

    with request(
        opener,
        f"{game_url}/file/{upload_id}",
        data={"csrf_token": csrf},
        referer=download_page_url,
    ) as response:
        cdn = json.loads(read_text_response(response))
    cdn_url = cdn.get("url")
    if not cdn_url or urlparse(cdn_url).scheme != "https":
        raise RuntimeError("itch.io did not return a valid HTTPS release URL")

    with tempfile.TemporaryDirectory(prefix="abandonware-author-release-") as temp_dir:
        archive_path = Path(temp_dir) / expected_filename
        download(opener, cdn_url, archive_path)
        members, payload, notices = inspect_archive(archive_path, expected_filename, required_suffix)
        archive_hash = sha256(archive_path)
        archive_size = archive_path.stat().st_size

    exact_match = (
        payload["md5"].casefold() == expected_payload["md5"].casefold()
        and payload["size"] == int(expected_payload["size"])
    )

    record = {
        "schema": 1,
        "candidate_id": manifest["id"],
        "title": manifest["title"],
        "game_url": game_url,
        "release_label": manifest.get("release_label"),
        "upload_id": upload_id,
        "filename": expected_filename,
        "archive_size": archive_size,
        "archive_sha256": archive_hash,
        "member_count": len(members),
        "members": members,
        "payload": payload,
        "expected_payload": expected_payload,
        "notices": notices,
        "exact_payload_match": exact_match,
        "decision": "EXACT_BINARY_MATCH" if exact_match else "BINARY_MISMATCH",
        "warning": (
            "A binary identity match links the author-hosted release payload to the comparison "
            "hash. License scope and corresponding-source obligations remain separate checks."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_id": record["candidate_id"],
        "filename": record["filename"],
        "upload_id": record["upload_id"],
        "archive_size": record["archive_size"],
        "archive_sha256": record["archive_sha256"],
        "payload": record["payload"],
        "notice_paths": [notice["path"] for notice in notices],
        "decision": record["decision"],
    }, indent=2))

    for notice in notices:
        print(f"\n===== RELEASE NOTICE: {notice['path']} ({notice['size']} bytes) =====")
        print(notice["text"][:MAX_NOTICE_BYTES])
        print(f"===== END RELEASE NOTICE: {notice['path']} =====")

    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = audit(args.manifest, args.output)
    if record["decision"] != "EXACT_BINARY_MATCH":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
