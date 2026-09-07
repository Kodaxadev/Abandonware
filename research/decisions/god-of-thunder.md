# Candidate decision — God of Thunder

Decision: **HOLD — SHIPPED LICENSE EXPRESSLY PROHIBITS REDISTRIBUTION**

This decision is based on the exact package currently distributed by ScummVM, not on the general meaning of “freeware.”

## What passed

The exact ScummVM-hosted package was audited successfully:

- source: `https://downloads.scummvm.org/frs/extras/God%20of%20Thunder/gotfree.zip`
- SHA-256: `94962e6fcbc6d547debda11224d00fdec7a0d03bacdf7d82d08ed8ea289c0c5e`
- package size observed by CI: 1,059,686 bytes
- 10 safe archive members
- flat DOS payload including `GOT.EXE` and `GOTRES.DAT`
- package license found: `LICENSE.TXT`
- pinned ScummVM runtime candidate: engine `got`, target `got`

Adept Software's current site labels God of Thunder freeware, and its classics page says the old games were released as freeware because they are no longer sold. ScummVM likewise publishes the exact package as a freeware version.

## What blocks hosting

The exact `LICENSE.TXT` shipped inside `gotfree.zip` is an Impulse Games, Inc. end-user license. It grants use of one copy on one computer and expressly says the end user may not rent, lease, sell, or otherwise distribute the software. It permits only one copy for backup or archival purposes and separately states that copying is forbidden.

That is direct package-level evidence against third-party redistribution. A later web page calling the game freeware may establish that end users can obtain it without charge, but the wording we have found does not explicitly supersede the no-distribution clause or authorize third-party mirrors.

Under Abandonware's policy, we do not infer a redistribution grant from “freeware” when the exact payload contains contrary license language.

## Current status

- technical candidate: **yes**
- exact package provenance: **verified**
- package safety: **verified**
- current free-download/freeware classification: **supported**
- shipped license: **explicitly restricts redistribution**
- defensible Kodaxa mirror right: **not established**
- production manifest: **prohibited while this decision remains HOLD**
- public catalog: **do not add**

## Reconsideration trigger

This decision can be revisited only with rights-holder evidence that supersedes or amends the packaged restriction, such as:

1. an explicit Adept Software / Ron Davis authorization for third-party redistribution or mirroring,
2. a newer license tied to this full-version game data that permits redistribution,
3. direct permission from the legitimate rights holder.

Another freeware listing, a download button, or ScummVM hosting the package is not by itself sufficient to override the license text bundled with the exact archive.
