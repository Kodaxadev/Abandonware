# Robin's Rescue — rights and provenance record

Status: **HOSTABLE / OPEN LICENSE / SOURCE PRESERVED**

This record applies only to the Robin's Rescue game data identified below. It does not grant rights to unrelated SLUDGE games, the SLUDGE trademarks, third-party works outside the game's own attribution record, or other Cheeseness/Mimness projects.

## Identity

- Title: Robin's Rescue
- Authors: Josh "Cheeseness" Bush and Miriam "Mimness" Roser
- Original release: July 2015
- Browser interpreter: ScummVM
- ScummVM engine: `sludge`
- ScummVM target: `robinsrescue`
- Detection payload: `robins_rescue.slg`
- Detection MD5: `16cbf2bf916ed89f9c1b14fab133cf96`
- Detection size: `14,413,769` bytes

The detection identity above is pinned in the ScummVM 2026.3.0 source used by this archive.

## Rights basis

The authors' current itch.io release page describes Robin's Rescue as a Free/Open Source SLUDGE demonstration game, labels the code license GNU Lesser General Public License v3.0, and continues to publish v1.0 Windows, macOS and Linux downloads:

https://cheeseness.itch.io/robins-rescue

The authors' source repository provides the more precise license split used by Abandonware. At the repository's `v1.0` release tag:

- source code is licensed under GNU LGPL 3.0;
- first-party images/audio are licensed under Creative Commons Attribution 3.0 Unported;
- the README enumerates third-party sound and music under CC0 1.0 or CC-BY 3.0 as applicable;
- Medieval Sharp is covered by SIL Open Font License 1.1.

Abandonware preserves the original `COPYING`, `README.md`, SLUDGE notice and font license with their exact hashes rather than flattening the whole game into a single license label.

## Corresponding source

The source repository migrated from its historical GitLab location to Codeberg. Abandonware audited the Codeberg Git repository without executing repository code and pinned the release tag:

- repository: `https://codeberg.org/Cheeseness/robins-rescue.git`
- revision: `refs/tags/v1.0`
- commit: `62b0920ea93b38f54a8678cdee1d1434803c3e4c`
- tree: `f2b1e2da131ee1ed12827844c2e088e10363bcd7`
- source files: `147`
- source archive SHA-256: `c063f3a0a1bf1369ddb1bb9d80fdb57658bd00fc74040afe61107b65033fd7a4`

The complete immutable source archive and preserved legal/attribution files are stored under:

`runtime/sources/robins-rescue/`

The source tag does not commit the generated `.slg` binary itself. This record therefore does **not** claim that Git contains a byte-identical compiled artifact. The authors' current itch.io page identifies the v1.0 releases and states that the game data file is `data/robins_rescue.slg`; the repository tag `v1.0` is the preserved release source corresponding to that release line.

A separate non-publishing audit attempts to compare the author-hosted v1.0 `.slg` directly to the ScummVM payload. At the time of this record, GitHub's hosted runner receives HTTP 526 from the itch.io author subdomain before any binary is downloaded. That transport failure is recorded separately and is **not** represented as a successful binary-hash comparison.

## Exact game package used by Abandonware

Abandonware uses ScummVM's current Robin's Rescue package:

- URL: `https://downloads.scummvm.org/frs/extras/SLUDGE/robinsrescue.zip`
- SHA-256: `5727726234a85633f4bc5327f238de82cf6844cbc68d097c9ba3c9e798314859`
- package payload: `robinsrescue/robins_rescue.slg`
- ScummVM detector MD5: `16cbf2bf916ed89f9c1b14fab133cf96`
- ScummVM detector size: `14,413,769` bytes

The package audit found one game payload and no embedded legal notice. For that reason, Robin's Rescue uses the archive's `open_license` intake path rather than the normal freeware-package path. Production materialization must verify the checked-in rights record, preserved source provenance, source archive hash, and preserved license/attribution files before the game can be published.

## Required attribution and notices

Distribution must retain or expose the following source-preserved evidence:

- `runtime/sources/robins-rescue/legal/COPYING`
- `runtime/sources/robins-rescue/legal/README.md`
- `runtime/sources/robins-rescue/legal/sludge__doc__README`
- `runtime/sources/robins-rescue/legal/sprite_sources__medieval_sharp__SIL - Open Font License.txt`

The README is material because it contains third-party attribution details that cannot safely be reconstructed from a generic CC-BY label.

## Scope warning

Robin's Rescue being open-licensed does not imply that every game downloadable from ScummVM, itch.io, or a SLUDGE archive may be mirrored. Each title remains a separate rights decision.
