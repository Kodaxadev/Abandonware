#!/usr/bin/env python3
"""Audit an external Git source repository without executing repository code.

This lane is for corresponding-source and license evidence only. It clones a bare
repository, resolves an optional exact revision, records commit/tree identity, inventories
files and gitlinks, preserves human-readable license/readme notices, records remote release
tags, fingerprints requested blobs, and creates a deterministic git-archive tarball. It
never checks out or runs files from the audited repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
from urllib.parse import urlparse

MAX_NOTICE_BYTES = 256 * 1024
NOTICE_TOKENS = ("license", "licence", "copying", "copyright", "readme")


def run_git(git_dir: Path, *args: str, text: bool = True) -> str | bytes:
    command = ["git", f"--git-dir={git_dir}", *args]
    result = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    return result.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_git_path(value: str) -> str:
    normalized = PurePosixPath(value.replace("\\", "/"))
    if not normalized.parts or normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"Unsafe Git tree path: {value!r}")
    return normalized.as_posix()


def clone_bare(url: str, destination: Path) -> None:
    subprocess.run(
        [
            "git",
            "-c", "protocol.file.allow=never",
            "clone",
            "--bare",
            "--filter=blob:none",
            "--no-tags",
            "--single-branch",
            url,
            str(destination),
        ],
        check=True,
    )


def fetch_revision(git_dir: Path, revision: str) -> str:
    """Fetch one requested remote revision and return its exact commit."""
    if revision == "HEAD":
        return str(run_git(git_dir, "rev-parse", "HEAD^{commit}")).strip()

    if not revision.startswith("refs/"):
        raise RuntimeError("Explicit source revision must be a full refs/... name")
    subprocess.run(
        [
            "git",
            "-c", "protocol.file.allow=never",
            f"--git-dir={git_dir}",
            "fetch",
            "--no-tags",
            "origin",
            revision,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return str(run_git(git_dir, "rev-parse", "FETCH_HEAD^{commit}")).strip()


def remote_tags(url: str) -> list[dict]:
    """Read remote tag refs without checking out or executing remote content."""
    result = subprocess.run(
        ["git", "-c", "protocol.file.allow=never", "ls-remote", "--tags", url],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    indexed: dict[str, dict] = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        object_sha, ref = line.split("\t", 1)
        prefix = "refs/tags/"
        if not ref.startswith(prefix):
            continue
        name = ref[len(prefix):]
        peeled = name.endswith("^{}")
        if peeled:
            name = name[:-3]
        record = indexed.setdefault(name, {"name": name})
        record["peeled_commit" if peeled else "object"] = object_sha
    records = []
    for name in sorted(indexed):
        record = indexed[name]
        record["resolved_commit"] = record.get("peeled_commit", record.get("object"))
        records.append(record)
    return records


def notice_name(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].casefold()
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


def fingerprint_blob(git_dir: Path, commit: str, value: str) -> dict:
    path = safe_git_path(value)
    try:
        raw = run_git(git_dir, "show", f"{commit}:{path}", text=False)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Requested fingerprint path is missing at {commit}: {path}") from error
    assert isinstance(raw, bytes)
    object_sha = str(run_git(git_dir, "rev-parse", f"{commit}:{path}")).strip()
    return {
        "path": path,
        "object": object_sha,
        "size": len(raw),
        "md5": hashlib.md5(raw, usedforsecurity=False).hexdigest(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def audit(manifest_path: Path, output_dir: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate_id = manifest["id"]
    repository_url = manifest["repository_url"]
    parsed = urlparse(repository_url)

    if parsed.scheme != "https":
        raise RuntimeError("Source repository URL must use HTTPS")
    if parsed.hostname != manifest["allowed_host"]:
        raise RuntimeError(
            f"Source host mismatch for {candidate_id}: expected {manifest['allowed_host']}, "
            f"got {parsed.hostname}"
        )

    requested_revision = manifest.get("revision", "HEAD")
    fingerprint_paths = manifest.get("fingerprint_paths", [])
    if not isinstance(fingerprint_paths, list):
        raise RuntimeError("fingerprint_paths must be a list")

    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="abandonware-source-audit-") as temp_dir:
        git_dir = Path(temp_dir) / "source.git"
        tags = remote_tags(repository_url)
        clone_bare(repository_url, git_dir)
        branch = str(run_git(git_dir, "symbolic-ref", "--short", "HEAD")).strip()
        commit = fetch_revision(git_dir, requested_revision)
        tree = str(run_git(git_dir, "rev-parse", f"{commit}^{{tree}}")).strip()
        commit_time = str(run_git(git_dir, "show", "-s", "--format=%cI", commit)).strip()
        resolved_tags = [tag["name"] for tag in tags if tag.get("resolved_commit") == commit]

        raw_tree = str(run_git(git_dir, "ls-tree", "-r", commit))
        files: list[dict] = []
        gitlinks: list[str] = []
        for line in raw_tree.splitlines():
            metadata, path = line.split("\t", 1)
            mode, object_type, object_sha = metadata.split(" ", 2)
            files.append({
                "path": path,
                "mode": mode,
                "type": object_type,
                "object": object_sha,
            })
            if mode == "160000" or object_type == "commit":
                gitlinks.append(path)

        notice_records: list[dict] = []
        for file_record in files:
            path = file_record["path"]
            if file_record["type"] != "blob" or not notice_name(path):
                continue
            raw = run_git(git_dir, "show", f"{commit}:{path}", text=False)
            assert isinstance(raw, bytes)
            decoded = decode_notice(raw)
            notice_records.append({
                "path": path,
                "object": file_record["object"],
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "text": decoded,
            })

        fingerprints = [fingerprint_blob(git_dir, commit, value) for value in fingerprint_paths]

        archive_path = output_dir / f"{candidate_id}-{commit}.tar.gz"
        subprocess.run(
            [
                "git",
                f"--git-dir={git_dir}",
                "archive",
                "--format=tar.gz",
                f"--prefix={candidate_id}-{commit}/",
                f"--output={archive_path}",
                commit,
            ],
            check=True,
        )

        record = {
            "schema": 3,
            "candidate_id": candidate_id,
            "title": manifest.get("title"),
            "repository_url": repository_url,
            "source_page": manifest.get("source_page"),
            "requested_revision": requested_revision,
            "resolved_branch": branch,
            "resolved_commit": commit,
            "resolved_tree": tree,
            "commit_time": commit_time,
            "remote_tags": tags,
            "tags_pointing_at_revision": resolved_tags,
            "file_count": len(files),
            "gitlinks": gitlinks,
            "files": files,
            "fingerprints": fingerprints,
            "notices": notice_records,
            "license_expectations": manifest.get("license_expectations", []),
            "archive_file": archive_path.name,
            "archive_sha256": sha256(archive_path),
            "decision": "REQUIRES_HUMAN_SOURCE_REVIEW",
            "warning": (
                "This audit records source identity, remote tag refs, requested blob hashes, and "
                "notice files only. It never executes repository code. A matching compiled blob "
                "can establish release identity, but license scope still requires human review."
            ),
        }

    report_path = output_dir / f"{candidate_id}.json"
    report_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_id": candidate_id,
        "requested_revision": record["requested_revision"],
        "branch": record["resolved_branch"],
        "commit": record["resolved_commit"],
        "commit_time": record["commit_time"],
        "tree": record["resolved_tree"],
        "remote_tags": record["remote_tags"],
        "tags_pointing_at_revision": record["tags_pointing_at_revision"],
        "file_count": record["file_count"],
        "gitlinks": record["gitlinks"],
        "fingerprints": record["fingerprints"],
        "notice_paths": [notice["path"] for notice in notice_records],
        "archive_file": record["archive_file"],
        "archive_sha256": record["archive_sha256"],
        "decision": record["decision"],
    }, indent=2))

    for notice in notice_records:
        print(f"\n===== SOURCE NOTICE: {notice['path']} ({notice['size']} bytes) =====")
        if notice["text"] is None:
            print("[binary/non-text notice omitted]")
        else:
            print(notice["text"][:MAX_NOTICE_BYTES])
        print(f"===== END SOURCE NOTICE: {notice['path']} =====")

    if not notice_records:
        print("\nWARNING: no license/readme/copyright-style source notice files were found.")
    if gitlinks:
        print("\nWARNING: source repository contains gitlinks/submodules not included in git archive.")
    if not resolved_tags:
        print("\nNOTE: no remote tag points directly at the audited revision.")

    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("source-audits"))
    args = parser.parse_args()
    audit(args.manifest, args.output_dir)


if __name__ == "__main__":
    main()
