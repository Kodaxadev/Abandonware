#!/usr/bin/env python3
"""Materialize a pinned external Git source snapshot without executing it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(git_dir: Path, *args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", f"--git-dir={git_dir}", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    return result.stdout


def clone_bare(url: str, destination: Path) -> None:
    subprocess.run(
        [
            "git",
            "-c", "protocol.file.allow=never",
            "clone",
            "--bare",
            "--no-tags",
            url,
            str(destination),
        ],
        check=True,
    )


def safe_output_name(path: str) -> str:
    return path.replace("\\", "/").replace("/", "__")


def materialize(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repository_url = manifest["repository_url"]
    parsed = urlparse(repository_url)
    if parsed.scheme != "https":
        raise RuntimeError("Source repository URL must use HTTPS")
    if parsed.hostname != manifest["allowed_host"]:
        raise RuntimeError(
            f"Source host mismatch: expected {manifest['allowed_host']}, got {parsed.hostname}"
        )

    commit = manifest["commit"].casefold()
    expected_tree = manifest["tree"].casefold()
    expected_archive_sha = manifest["archive_sha256"].casefold()
    if len(commit) != 40 or len(expected_tree) != 40 or len(expected_archive_sha) != 64:
        raise RuntimeError("Pinned commit/tree/archive hashes have invalid lengths")

    output = Path(manifest["output"])
    staging = output.with_name(output.name + ".staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory(prefix="abandonware-source-materialize-") as temp_dir:
            git_dir = Path(temp_dir) / "source.git"
            clone_bare(repository_url, git_dir)

            subprocess.run(
                ["git", f"--git-dir={git_dir}", "cat-file", "-e", f"{commit}^{{commit}}"],
                check=True,
            )
            actual_tree = str(git(git_dir, "rev-parse", f"{commit}^{{tree}}")).strip().casefold()
            if actual_tree != expected_tree:
                raise RuntimeError(
                    f"Source tree mismatch: expected {expected_tree}, got {actual_tree}"
                )

            raw_tree = str(git(git_dir, "ls-tree", "-r", commit))
            file_records: list[dict] = []
            gitlinks: list[str] = []
            paths: set[str] = set()
            for line in raw_tree.splitlines():
                metadata, path = line.split("\t", 1)
                mode, object_type, object_sha = metadata.split(" ", 2)
                paths.add(path)
                file_records.append({
                    "path": path,
                    "mode": mode,
                    "type": object_type,
                    "object": object_sha,
                })
                if mode == "160000" or object_type == "commit":
                    gitlinks.append(path)

            if gitlinks:
                raise RuntimeError(
                    "Pinned source contains gitlinks/submodules that are not included in git archive: "
                    + ", ".join(gitlinks)
                )
            if len(file_records) != int(manifest["file_count"]):
                raise RuntimeError(
                    f"Source file-count mismatch: expected {manifest['file_count']}, "
                    f"got {len(file_records)}"
                )

            for required in manifest.get("required_paths", []):
                if required not in paths:
                    raise RuntimeError(f"Required source path missing: {required}")

            archive_name = f"{manifest['id']}-{commit}.tar.gz"
            archive_path = staging / archive_name
            subprocess.run(
                [
                    "git",
                    f"--git-dir={git_dir}",
                    "archive",
                    "--format=tar.gz",
                    f"--prefix={manifest['id']}-{commit}/",
                    f"--output={archive_path}",
                    commit,
                ],
                check=True,
            )
            actual_archive_sha = sha256_file(archive_path)
            if actual_archive_sha.casefold() != expected_archive_sha:
                raise RuntimeError(
                    f"Source archive SHA-256 mismatch: expected {expected_archive_sha}, "
                    f"got {actual_archive_sha}"
                )

            legal_dir = staging / "legal"
            legal_dir.mkdir(parents=True, exist_ok=True)
            preserved: list[dict] = []
            for record in manifest.get("preserve_files", []):
                source_path = record["path"]
                if source_path not in paths:
                    raise RuntimeError(f"Preserved source notice missing: {source_path}")
                raw = git(git_dir, "show", f"{commit}:{source_path}", text=False)
                assert isinstance(raw, bytes)
                actual = sha256_bytes(raw)
                expected = record["sha256"].casefold()
                if actual.casefold() != expected:
                    raise RuntimeError(
                        f"Preserved notice hash mismatch for {source_path}: "
                        f"expected {expected}, got {actual}"
                    )
                destination = legal_dir / safe_output_name(source_path)
                destination.write_bytes(raw)
                preserved.append({
                    "source_path": source_path,
                    "materialized_path": destination.relative_to(staging).as_posix(),
                    "sha256": actual,
                    "size": len(raw),
                })

            provenance = {
                "schema": 1,
                "id": manifest["id"],
                "title": manifest["title"],
                "repository_url": repository_url,
                "source_page": manifest.get("source_page"),
                "branch_at_audit": manifest.get("branch"),
                "commit": commit,
                "tree": actual_tree,
                "file_count": len(file_records),
                "archive_file": archive_name,
                "archive_sha256": actual_archive_sha,
                "authors": manifest.get("authors", []),
                "license_summary": manifest.get("license_summary", {}),
                "preserved_notices": preserved,
                "build_manifest": manifest_path.as_posix(),
            }
            (staging / "PROVENANCE.json").write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            lines = [
                f"# Corresponding source — {manifest['title']}",
                "",
                "This directory preserves the exact source snapshot used as the corresponding-source record for the hosted game data.",
                "",
                f"- repository: `{repository_url}`",
                f"- commit: `{commit}`",
                f"- tree: `{actual_tree}`",
                f"- archive SHA-256: `{actual_archive_sha}`",
                f"- source files: {len(file_records)}",
                "",
                "The archive is generated with `git archive` from the pinned commit. Repository code is not executed during source materialization.",
                "",
                "## Licensing and attribution",
                "",
            ]
            for key, value in manifest.get("license_summary", {}).items():
                lines.append(f"- {key.replace('_', ' ')}: {value}")
            lines.extend([
                "",
                "The preserved author README contains the detailed third-party sound/music attribution record and the source tree contains the corresponding asset/source files.",
                "",
            ])
            (staging / "SOURCE.md").write_text("\n".join(lines), encoding="utf-8")

        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
        print(json.dumps(provenance, indent=2, sort_keys=True))
        return provenance
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    materialize(args.manifest)


if __name__ == "__main__":
    main()
