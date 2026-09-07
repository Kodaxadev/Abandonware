#!/usr/bin/env python3
"""Materialize audited ScummVM freeware packages into a built Web runtime.

This tool does not build ScummVM itself. It operates on an already-built Emscripten
runtime directory, verifies each pinned game archive, extracts it safely, writes the
ScummVM target configuration, and emits runtime/game provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.request
import zipfile

NOTICE_NAMES = ("readme", "license", "licence", "copying", "copyright")


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Kodaxa-Abandonware-Preservation/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def safe_member_path(name: str) -> PurePosixPath:
    normalized = PurePosixPath(name.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"Unsafe ZIP member path: {name!r}")
    if not normalized.parts:
        raise RuntimeError(f"Empty ZIP member path: {name!r}")
    return normalized


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in archive.infolist():
        member = safe_member_path(item.filename)
        target = destination.joinpath(*member.parts)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(item, "r") as source, target.open("wb") as output:
            shutil.copyfileobj(source, output)


def find_notices(root: Path) -> list[str]:
    notices: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        lower = path.name.casefold()
        if any(token in lower for token in NOTICE_NAMES):
            notices.append(path.relative_to(root).as_posix())
    return sorted(notices)


def normalize_games(manifest: dict) -> list[dict]:
    games = manifest.get("games")
    if games is None and "game" in manifest:
        games = [manifest["game"]]
    if not isinstance(games, list) or not games:
        raise RuntimeError("ScummVM manifest must contain at least one game")
    return games


def game_target_path(data_root: Path, game: dict) -> Path:
    outer = data_root / game["data_directory"]
    relative = game.get("relative_game_path", ".")
    target = outer if relative in ("", ".") else outer.joinpath(*PurePosixPath(relative).parts)
    return target


def write_scummvm_ini(runtime_root: Path, games: list[dict], version: str) -> None:
    lines = [
        "[scummvm]",
        f"versioninfo={version}",
        "always_run_fallback_detection_extern=false",
        "",
    ]

    for game in games:
        config = game.get("config", {})
        target = game["target"]
        data_directory = game["data_directory"]
        relative = game.get("relative_game_path", ".")
        path = f"/data/games/{data_directory}"
        if relative not in ("", "."):
            path += "/" + PurePosixPath(relative).as_posix()

        lines.extend([
            f"[{target}]",
            f"gameid={config.get('gameid', target)}",
            f"engineid={config.get('engineid', target)}",
            f"path={path}",
        ])
        for key in ("description", "platform", "language", "extra", "guioptions"):
            value = config.get(key)
            if value:
                lines.append(f"{key}={value}")
        lines.append("")

    (runtime_root / "scummvm.ini").write_text("\n".join(lines), encoding="utf-8")


def materialize(manifest_path: Path, runtime_root: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runtime = manifest["runtime"]
    games = normalize_games(manifest)
    data_root = runtime_root / "data" / "games"
    data_root.mkdir(parents=True, exist_ok=True)

    # The build directory is regenerated, but clean any declared target dirs anyway so
    # rerunning locally cannot merge a new package with stale files.
    for game in games:
        destination = data_root / game["data_directory"]
        if destination.exists():
            shutil.rmtree(destination)

    provenance_games: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="abandonware-scummvm-") as temp_dir:
        temp = Path(temp_dir)
        for index, game in enumerate(games, start=1):
            archive_path = temp / f"game-{index}.zip"
            print(f"Downloading {game['title']}: {game['source_url']}")
            download(game["source_url"], archive_path)

            actual_sha256 = digest(archive_path, "sha256")
            expected_sha256 = game["sha256"].casefold()
            if actual_sha256.casefold() != expected_sha256:
                raise RuntimeError(
                    f"SHA-256 mismatch for {game['id']}: expected {expected_sha256}, "
                    f"received {actual_sha256}"
                )

            destination = data_root / game["data_directory"]
            with zipfile.ZipFile(archive_path, "r") as archive:
                safe_extract(archive, destination)

            notices = find_notices(destination)
            if not notices:
                raise RuntimeError(
                    f"Audited package {game['id']} contains no preserved readme/license/copyright notice"
                )

            target_path = game_target_path(data_root, game)
            if not target_path.is_dir():
                raise RuntimeError(
                    f"Configured game path does not exist for {game['id']}: {target_path}"
                )
            if not any(path.is_file() for path in target_path.rglob("*")):
                raise RuntimeError(f"Configured game path is empty for {game['id']}: {target_path}")

            provenance_games.append({
                "id": game["id"],
                "target": game["target"],
                "title": game["title"],
                "edition": game.get("edition"),
                "source_url": game["source_url"],
                "source_page": game.get("source_page"),
                "sha256": actual_sha256,
                "data_directory": game["data_directory"],
                "relative_game_path": game.get("relative_game_path", "."),
                "rights_record": game["rights_record"],
                "preserved_notices": notices,
            })
            print(
                f"Verified {game['id']} ({archive_path.stat().st_size} bytes, "
                f"{len(notices)} notice file(s))"
            )

    write_scummvm_ini(runtime_root, games, runtime["version"])

    engines = runtime.get("engines")
    if engines is None:
        engine = runtime.get("engine")
        engines = [engine] if engine else []

    provenance = {
        "schema": 2,
        "runtime": {
            **runtime,
            "engines": engines,
        },
        "games": provenance_games,
        "corresponding_source": (
            f"https://github.com/{runtime['repository']}/tree/{runtime['commit']}"
        ),
        "build_manifest": manifest_path.as_posix(),
    }
    (runtime_root / "PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("runtime_root", type=Path)
    args = parser.parse_args()
    materialize(args.manifest, args.runtime_root)


if __name__ == "__main__":
    main()
