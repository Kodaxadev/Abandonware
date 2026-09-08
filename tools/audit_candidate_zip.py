#!/usr/bin/env python3
"""Audit a candidate game ZIP without publishing or materializing it.

The candidate lane is intentionally separate from hosted-game manifests. It verifies the
exact source artifact, rejects unsafe paths, inventories archive structure, and records
license/readme/copyright/attribution notices for human rights review. Passing this tool
does NOT make a game hostable or browser-ready.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tempfile
import urllib.request
import zipfile

# Rights evidence is not always named LICENSE or README. Preserve common attribution,
# authorship and patent/third-party notice files as well so package audits do not silently
# omit material that can narrow or qualify a game's apparent license grant.
NOTICE_TOKENS = (
    "license",
    "licence",
    "readme",
    "copying",
    "copyright",
    "legal",
    "authors",
    "credits",
    "patents",
    "notice",
    "attribution",
    "third-party",
    "third_party",
)
MAX_NOTICE_BYTES = 256 * 1024
MAX_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024

# These are discovery markers, not an automatic legal classifier. A hit means the
# surrounding text deserves review; absence of a hit does not prove that no rights exist.
EVIDENCE_PATTERNS = {
    "redistribute": re.compile(r"\bredistribut(?:e|ed|es|ing|ion|able)\b", re.I),
    "distribute": re.compile(r"\bdistribut(?:e|ed|es|ing|ion|able)\b", re.I),
    "mirror": re.compile(r"\bmirror(?:ed|ing|s)?\b", re.I),
    "copy_permission": re.compile(r"\b(?:copy|copies|copying)\b", re.I),
    "freeware": re.compile(r"\bfreeware\b", re.I),
    "public_domain": re.compile(r"\bpublic\s+domain\b", re.I),
    "license": re.compile(r"\blicen[cs](?:e|ed|es|ing)\b", re.I),
    "modify": re.compile(r"\bmodif(?:y|ied|ies|ication|ications)\b", re.I),
    "commercial_restriction": re.compile(r"\b(?:non[- ]?commercial|commercial\s+use|not\s+for\s+sale|may\s+not\s+be\s+sold)\b", re.I),
    "all_rights_reserved": re.compile(r"\ball\s+rights\s+reserved\b", re.I),
    # License prose is commonly hard-wrapped. DOTALL is deliberate, but the bounded
    # gap prevents a "may not" in one paragraph from being paired with an unrelated
    # distribution word much later in the document.
    "redistribution_prohibited": re.compile(
        r"\b(?:may|shall|must)\s+not\b.{0,180}\b(?:redistribut(?:e|ed|es|ing|ion|able)|distribut(?:e|ed|es|ing|ion|able)|mirror(?:ed|ing|s)?|copy(?:ing|ies|ied)?)\b",
        re.I | re.S,
    ),
    "copying_prohibited": re.compile(
        r"\bcopying\b.{0,180}\b(?:strictly\s+)?(?:forbidden|prohibited|not\s+permitted)\b",
        re.I | re.S,
    ),
    "backup_only": re.compile(r"\b(?:solely|only)\s+for\s+(?:backup|archiv(?:e|al))\b", re.I),
}

RESTRICTION_MARKERS = {
    "redistribution_prohibited",
    "copying_prohibited",
    "backup_only",
    "commercial_restriction",
    "all_rights_reserved",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(name: str) -> PurePosixPath:
    normalized = PurePosixPath(name.replace("\\", "/"))
    if not normalized.parts or normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"Unsafe archive member path: {name!r}")
    return normalized


def is_notice_name(name: str) -> bool:
    """Return True for filenames likely to carry legal/rights/attribution evidence."""
    lower_name = name.casefold()
    return any(token in lower_name for token in NOTICE_TOKENS)


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Kodaxa-Abandonware-Candidate-Audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_ARCHIVE_BYTES:
            raise RuntimeError(f"Candidate archive exceeds {MAX_ARCHIVE_BYTES} bytes")
        with destination.open("wb") as output:
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise RuntimeError(f"Candidate archive exceeds {MAX_ARCHIVE_BYTES} bytes")
                output.write(chunk)


def decode_notice(data: bytes) -> str:
    data = data[:MAX_NOTICE_BYTES]
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def evidence_context(text: str, match: re.Match[str], radius: int = 140) -> str:
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    snippet = " ".join(text[start:end].split())
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet += "…"
    return snippet


def scan_evidence(text: str) -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {}
    for label, pattern in EVIDENCE_PATTERNS.items():
        snippets: list[str] = []
        seen: set[str] = set()
        for match in pattern.finditer(text):
            snippet = evidence_context(text, match)
            if snippet not in seen:
                snippets.append(snippet)
                seen.add(snippet)
            if len(snippets) >= 5:
                break
        if snippets:
            evidence[label] = snippets
    return evidence


def audit(manifest_path: Path, output_path: Path | None) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate_id = manifest["id"]
    source = manifest["source"]
    expected_sha = source["sha256"].casefold()

    if len(expected_sha) != 64 or any(ch not in "0123456789abcdef" for ch in expected_sha):
        raise RuntimeError("Candidate SHA-256 must contain exactly 64 hexadecimal characters")
    if not source["url"].startswith("https://"):
        raise RuntimeError("Candidate source URL must use HTTPS")

    with tempfile.TemporaryDirectory(prefix="abandonware-candidate-") as temp_dir:
        archive_path = Path(temp_dir) / "candidate.zip"
        print(f"Downloading candidate {candidate_id}: {source['url']}")
        download(source["url"], archive_path)

        actual_sha = sha256(archive_path)
        if actual_sha.casefold() != expected_sha:
            raise RuntimeError(
                f"SHA-256 mismatch for {candidate_id}: expected {expected_sha}, got {actual_sha}"
            )

        members: list[dict] = []
        notices: list[dict] = []
        direct_root_files: list[str] = []
        top_level_names: set[str] = set()
        aggregate_evidence: dict[str, list[dict]] = {}

        with zipfile.ZipFile(archive_path, "r") as archive:
            for info in archive.infolist():
                path = safe_path(info.filename)
                top_level_names.add(path.parts[0])
                members.append({
                    "path": path.as_posix(),
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                    "directory": info.is_dir(),
                })

                if not info.is_dir() and len(path.parts) == 1:
                    direct_root_files.append(path.name)

                if info.is_dir():
                    continue

                if is_notice_name(path.name):
                    raw = archive.read(info)
                    text = decode_notice(raw)
                    evidence = scan_evidence(text)
                    notice_record = {
                        "path": path.as_posix(),
                        "size": info.file_size,
                        "text": text,
                        "evidence_markers": evidence,
                    }
                    notices.append(notice_record)
                    for label, snippets in evidence.items():
                        aggregate_evidence.setdefault(label, []).append({
                            "path": path.as_posix(),
                            "snippets": snippets,
                        })

        restriction_evidence = {
            label: aggregate_evidence[label]
            for label in sorted(RESTRICTION_MARKERS)
            if label in aggregate_evidence
        }

        audit_record = {
            "schema": 3,
            "candidate_id": candidate_id,
            "title": manifest.get("title"),
            "source_url": source["url"],
            "source_page": source.get("page"),
            "sha256": actual_sha,
            "archive_size": archive_path.stat().st_size,
            "member_count": len(members),
            "top_level_names": sorted(top_level_names),
            "direct_root_files": sorted(direct_root_files),
            "notices": notices,
            "evidence_markers": aggregate_evidence,
            "restriction_markers": restriction_evidence,
            "members": members,
            "decision": "REQUIRES_HUMAN_RIGHTS_REVIEW",
            "warning": (
                "Evidence markers are search aids only. A successful package audit or keyword hit "
                "does not authorize hosting; a human must evaluate who granted which rights and "
                "whether the grant covers redistribution of this exact game data. Restriction "
                "markers are especially important conflicts but are not themselves a legal opinion."
            ),
        }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(audit_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_id": audit_record["candidate_id"],
        "sha256": audit_record["sha256"],
        "archive_size": audit_record["archive_size"],
        "member_count": audit_record["member_count"],
        "top_level_names": audit_record["top_level_names"],
        "direct_root_files": audit_record["direct_root_files"],
        "notice_paths": [notice["path"] for notice in notices],
        "evidence_marker_names": sorted(aggregate_evidence),
        "restriction_marker_names": sorted(restriction_evidence),
        "decision": audit_record["decision"],
    }, indent=2))

    for notice in notices:
        print(f"\n===== NOTICE: {notice['path']} ({notice['size']} bytes) =====")
        print(notice["text"][:MAX_NOTICE_BYTES])
        if notice["evidence_markers"]:
            print("\n----- EVIDENCE MARKERS (review aids, not approval) -----")
            for label, snippets in notice["evidence_markers"].items():
                print(f"[{label}]")
                for snippet in snippets:
                    print(f"  {snippet}")
        print(f"===== END NOTICE: {notice['path']} =====")

    if restriction_evidence:
        print("\nWARNING: explicit restriction-style language was detected; review before any hosting decision.")

    if not notices:
        print("\nWARNING: no legal/readme/authorship/attribution-style notice files were found in the package.")

    return audit_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit(args.manifest, args.output)


if __name__ == "__main__":
    main()
