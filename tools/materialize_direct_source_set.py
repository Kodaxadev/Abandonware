#!/usr/bin/env python3
"""Preserve a hash-pinned set of author-hosted source archives.

This complements the Git-based corresponding-source materializer. Every component must be
pinned by exact size and SHA-256; optional SHA-512 is verified too. Archives are downloaded
as inert bytes, never extracted or executed, then written under the requested source output
alongside a copied rights record and deterministic provenance.
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

USER_AGENT = "Kodaxa-Abandonware-Direct-Source-Preservation/1.0"
MAX_COMPONENT_BYTES = 512 * 1024 * 1024


def safe_relative(value: str) -> Path:
    normalized = PurePosixPath(value.replace("\\", "/"))
    if not normalized.parts or normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"Unsafe repository-relative path: {value!r}")
    return Path(*normalized.parts)


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_set_hash(components: list[dict]) -> str:
    normalized = [
        {
            "name": component["name"],
            "size": int(component["size"]),
            "sha256": str(component["sha256"]).casefold(),
            "source_url": component["source_url"],
        }
        for component in components
    ]
    raw = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def download_component(component: dict, destination: Path) -> None:
    url = component["source_url"]
    allowed_host = component["allowed_host"]
    expected_size = int(component["size"])
    expected_sha256 = str(component["sha256"]).casefold()
    expected_sha512 = str(component.get("sha512", "")).casefold()
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != allowed_host:
        raise RuntimeError(f"Source component must use HTTPS on {allowed_host}: {url}")
    if expected_size <= 0 or expected_size > MAX_COMPONENT_BYTES:
        raise RuntimeError(f"Invalid source component size for {component['name']}: {expected_size}")
    if len(expected_sha256) != 64:
        raise RuntimeError(f"Source component lacks SHA-256 pin: {component['name']}")

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)
    if destination.stat().st_size != expected_size:
        raise RuntimeError(
            f"Source component size mismatch for {component['name']}: expected {expected_size}, "
            f"got {destination.stat().st_size}"
        )
    actual_sha256 = digest(destination, "sha256")
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            f"Source component SHA-256 mismatch for {component['name']}: "
            f"expected {expected_sha256}, got {actual_sha256}"
        )
    if expected_sha512:
        actual_sha512 = digest(destination, "sha512")
        if actual_sha512 != expected_sha512:
            raise RuntimeError(
                f"Source component SHA-512 mismatch for {component['name']}: "
                f"expected {expected_sha512}, got {actual_sha512}"
            )


def materialize(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    components = manifest.get("components")
    if not isinstance(components, list) or not components:
        raise RuntimeError("Direct source set must contain at least one component")
    names = [component.get("name") for component in components]
    if not all(isinstance(name, str) and name for name in names) or len(set(names)) != len(names):
        raise RuntimeError("Direct source component names must be unique non-empty strings")

    output = safe_relative(manifest["output"])
    rights_record = safe_relative(manifest["rights_record"])
    if not rights_record.is_file():
        raise RuntimeError(f"Rights record is missing: {rights_record}")

    if output.exists():
        shutil.rmtree(output)
    artifacts_root = output / "artifacts"
    legal_root = output / "legal"
    artifacts_root.mkdir(parents=True)
    legal_root.mkdir(parents=True)

    materialized_components: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="abandonware-direct-source-") as temp_dir:
        temp = Path(temp_dir)
        for index, component in enumerate(components):
            name_path = safe_relative(component["name"])
            if len(name_path.parts) != 1:
                raise RuntimeError(f"Source component name must be a filename: {component['name']!r}")
            staged = temp / f"component-{index}"
            download_component(component, staged)
            target = artifacts_root / name_path.name
            shutil.copyfile(staged, target)
            materialized_components.append({
                "name": name_path.name,
                "role": component.get("role"),
                "source_url": component["source_url"],
                "size": target.stat().st_size,
                "sha256": digest(target, "sha256"),
                "sha512": digest(target, "sha512"),
                "materialized_path": f"artifacts/{name_path.name}",
            })

    rights_target = legal_root / "RIGHTS.md"
    shutil.copyfile(rights_record, rights_target)
    rights_sha = digest(rights_target, "sha256")
    rights_notice = {
        "source_path": rights_record.as_posix(),
        "materialized_path": "legal/RIGHTS.md",
        "size": rights_target.stat().st_size,
        "sha256": rights_sha,
    }

    provenance = {
        "schema": 1,
        "id": manifest["id"],
        "title": manifest.get("title"),
        "source_kind": "direct_archives",
        "source_page": manifest.get("source_page"),
        "license_identifiers": manifest.get("license_identifiers", []),
        "source_set_sha256": source_set_hash(materialized_components),
        "components": materialized_components,
        "preserved_notices": [rights_notice],
        "rights_record": rights_record.as_posix(),
        "build_manifest": manifest_path.as_posix(),
    }
    (output / "PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "SOURCE.md").write_text(
        "\n".join([
            f"# {manifest.get('title', manifest['id'])} corresponding source",
            "",
            "Source kind: hash-pinned original-developer archives.",
            f"Source page: {manifest.get('source_page', '')}",
            f"Source-set SHA-256: `{provenance['source_set_sha256']}`",
            "",
            "Preserved components:",
            *[
                f"- `{component['name']}` — {component['size']} bytes — SHA-256 `{component['sha256']}` — {component.get('role') or 'source component'}"
                for component in materialized_components
            ],
            "",
            "`legal/RIGHTS.md` is a copy of the checked-in audited rights record used when this source set was materialized.",
            "",
        ]),
        encoding="utf-8",
    )
    print(
        f"Preserved {manifest['id']} direct source set: {len(materialized_components)} component(s), "
        f"identity {provenance['source_set_sha256']}"
    )
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    materialize(args.manifest)


if __name__ == "__main__":
    main()
