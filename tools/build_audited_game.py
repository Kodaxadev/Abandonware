#!/usr/bin/env python3
"""Build a js-dos bundle from an audited, hash-pinned upstream ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.request
import zipfile


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "Kodaxa-Abandonware-Preservation/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def locate_launch_target(archive: zipfile.ZipFile, basename: str) -> str:
    wanted = basename.casefold()
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and PurePosixPath(name).name.casefold() == wanted
    ]
    if not candidates:
        raise RuntimeError(f"Launch target {basename!r} was not found in the verified source archive")
    candidates.sort(key=lambda value: (len(PurePosixPath(value).parts), len(value), value.casefold()))
    return candidates[0]


def make_dosbox_config(target: str, launch: dict) -> str:
    target_path = PurePosixPath(target)
    directory = "\\".join(target_path.parts[:-1])
    executable = target_path.name
    cd_line = f'cd "\\{directory}"' if directory else "cd \\"
    run_line = f'call "{executable}"' if executable.casefold().endswith(".bat") else f'"{executable}"'
    machine = launch.get("machine", "svga_s3")
    memory = int(launch.get("memory_mb", 16))
    cycles = launch.get("cycles", "auto")

    return (
        "[sdl]\n"
        "autolock=true\n\n"
        "[dosbox]\n"
        f"machine={machine}\n"
        f"memsize={memory}\n\n"
        "[cpu]\n"
        "core=auto\n"
        "cputype=auto\n"
        f"cycles={cycles}\n\n"
        "[mixer]\n"
        "rate=44100\n"
        "blocksize=1024\n"
        "prebuffer=25\n\n"
        "[sblaster]\n"
        "sbtype=sb16\n\n"
        "[autoexec]\n"
        "@echo off\n"
        "mount c .\n"
        "c:\n"
        f"{cd_line}\n"
        f"{run_line}\n"
    )


def build(manifest_path: Path) -> Path:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = manifest["source"]
    output = Path(manifest["output"])
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="abandonware-") as temp_dir:
        source_path = Path(temp_dir) / "source.zip"
        print(f"Downloading {source['url']}")
        download(source["url"], source_path)

        actual_size = source_path.stat().st_size
        expected_size = int(source["size"])
        if actual_size != expected_size:
            raise RuntimeError(f"Source size mismatch: expected {expected_size}, received {actual_size}")

        actual_sha1 = digest(source_path, "sha1")
        expected_sha1 = source["sha1"].casefold()
        if actual_sha1.casefold() != expected_sha1:
            raise RuntimeError(f"Source SHA-1 mismatch: expected {expected_sha1}, received {actual_sha1}")

        source_sha256 = digest(source_path, "sha256")
        with zipfile.ZipFile(source_path, "r") as source_zip:
            target = locate_launch_target(source_zip, manifest["launch"]["basename"])
            config = make_dosbox_config(target, manifest["launch"])

            provenance = {
                "schema": 1,
                "game_id": manifest["id"],
                "title": manifest["title"],
                "version": manifest.get("version"),
                "upstream_url": source["url"],
                "upstream_page": source.get("page"),
                "upstream_size": actual_size,
                "upstream_sha1": actual_sha1,
                "upstream_sha256": source_sha256,
                "copying_policy": source.get("copying_policy"),
                "launch_target": target,
                "rights_record": manifest.get("rights_record"),
            }

            with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
                for item in source_zip.infolist():
                    if item.filename.startswith(".jsdos/"):
                        continue
                    bundle.writestr(item, source_zip.read(item.filename))
                bundle.writestr(".jsdos/dosbox.conf", config)
                bundle.writestr(".jsdos/jsdos.json", json.dumps({"version": 1}, indent=2) + "\n")
                bundle.writestr(".jsdos/provenance.json", json.dumps(provenance, indent=2, sort_keys=True) + "\n")

    print(f"Built {output} ({output.stat().st_size} bytes)")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    build(args.manifest)


if __name__ == "__main__":
    main()
