#!/usr/bin/env python3
"""Audit an external Git source repository without executing repository code.

This lane is for corresponding-source and license evidence only. It clones a bare
repository, records the exact commit/tree, inventories files and gitlinks, preserves
human-readable license/readme notices, and creates a deterministic git-archive tarball.
It never checks out or runs files from the audited repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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

    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="abandonware-source-audit-") as temp_dir:
        git_dir = Path(temp_dir) / "source.git"
        clone_bare(repository_url, git_dir)

        commit = str(run_git(git_dir, "rev-parse", "HEAD")).strip()
        tree = str(run_git(git_dir, "rev-parse", "HEAD^{tree}")).strip()
        branch = str(run_git(git_dir, "symbolic-ref", "--short", "HEAD")).strip()
        commit_time = str(run_git(git_dir, "show", "-s", "--format=%cI", "HEAD")).strip()

        raw_tree = str(run_git(git_dir, "ls-tree", "-r", "HEAD"))
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
        for record in files:
            path = record["path"]
            if record["type"] != "blob" or not notice_name(path):
                continue
            raw = run_git(git_dir, "show", f"HEAD:{path}", text=False)
            assert isinstance(raw, bytes)
            decoded = decode_notice(raw)
            notice_records.append({
                "path": path,
                "object": record["object"],
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "text": decoded,
            })

        archive_path = output_dir / f"{candidate_id}-{commit}.tar.gz"
        subprocess.run(
            [
                "git",
                f"--git-dir={git_dir}",
                "archive",
                "--format=tar.gz",
                f"--prefix={candidate_id}-{commit}/",
                f"--output={archive_path}",
                "HEAD",
            ],
            check=True,
        )

        record = {
            "schema": 1,
            "candidate_id": candidate_id,
            "title": manifest.get("title"),
            "repository_url": repository_url,
            "source_page": manifest.get("source_page"),
            "resolved_branch": branch,
            "resolved_commit": commit,
            "resolved_tree": tree,
            "commit_time": commit_time,
            "file_count": len(files),
            "gitlinks": gitlinks,
            "files": files,
            "notices": notice_records,
            "license_expectations": manifest.get("license_expectations", []),
            "archive_file": archive_path.name,
            "archive_sha256": sha256(archive_path),
            "decision": "REQUIRES_HUMAN_SOURCE_REVIEW",
            "warning": (
                "This audit records source identity and notice files only. It does not execute "
                "the repository and does not itself establish that every compiled game asset is "
                "covered by the expected licenses."
            ),
        }

    report_path = output_dir / f"{candidate_id}.json"
    report_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_id": candidate_id,
        "branch": record["resolved_branch"],
        "commit": record["resolved_commit"],
        "tree": record["resolved_tree"],
        "file_count": record["file_count"],
        "gitlinks": record["gitlinks"],
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

    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("source-audits"))
    args = parser.parse_args()
    audit(args.manifest, args.output_dir)


if __name__ == "__main__":
    main()
