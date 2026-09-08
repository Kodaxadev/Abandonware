# Candidate decision — Full Moon

Decision: **HOLD — NO EXPLICIT THIRD-PARTY REDISTRIBUTION GRANT FOUND**

This decision applies to Elliott Ridgway's 2009 SLUDGE adventure Full Moon and the exact package currently distributed by ScummVM. It does not claim that the author could not authorize preservation hosting later.

## Evidence reviewed

Reviewed on 2026-09-08:

- author-controlled itch.io page: `https://elliott-ridgway.itch.io/full-moon`
- ScummVM game downloads: `https://www.scummvm.org/games/`
- ScummVM package: `https://downloads.scummvm.org/frs/extras/SLUDGE/fullmoon.zip`
- package SHA-256: `6f24b3e875f38d60dc1691a3ecc6bda5404119224efa0106491e214e6ddc842c`
- ScummVM target: `sludge:fullmoon`
- ScummVM detector payload: `gamedata`, MD5 `66e0ee55b517970807b794f34feb500a`, size `95,645,674` bytes

The author's itch.io page identifies Elliott Ridgway as the author, dates the release to July 7, 2009, and continues to provide `FullMoon.zip` as a downloadable Windows game. No explicit third-party redistribution, mirroring, repackaging, or browser-hosting grant was found on that author-controlled page.

## Exact package audit

The non-publishing package audit verified the ScummVM archive exactly:

- observed archive size: `73,233,832` bytes
- SHA-256: `6f24b3e875f38d60dc1691a3ecc6bda5404119224efa0106491e214e6ddc842c`
- member count: `6`
- top-level directory: `fullmoon`
- rights/readme/authorship/attribution notice files found: **none**

The absence of a notice does not prove the work is proprietary, but it means the package supplies no license text that closes the missing redistribution grant.

## What passed

- technical candidate: **yes**
- ScummVM engine/target: **sludge / fullmoon**
- exact ScummVM package hash: **verified**
- current author-controlled download provenance: **established**
- ScummVM detector identity: **published**

## What did not pass

Those questions remain separate:

- **Free/current author download:** established.
- **ScummVM hosts a preservation copy:** established.
- **Kodaxa may redistribute the complete game data from its own browser archive:** not established.

Abandonware does not infer a redistribution grant from the game's age, zero-price download, ScummVM availability, or the open-source licensing of the SLUDGE engine.

## Current status

- rights state: **HOLD**
- author-controlled third-party redistribution grant: **not established**
- open-content license covering the game data/assets: **not established**
- production manifest: **prohibited while this decision remains HOLD**
- public catalog: **do not add**
- non-publishing compatibility/package-identity work: **permitted**

## Reconsideration trigger

This decision can be revisited if Elliott Ridgway or another legitimate rights holder publishes or provides one of the following:

1. explicit permission to redistribute or mirror the Full Moon game data;
2. explicit permission covering extracted/browser/WebAssembly hosting;
3. an open-content license covering the required game assets;
4. an author-controlled source/release repository whose terms clearly cover redistribution of the complete playable data set.

Another freeware/free-download listing, preservation mirror, or ScummVM package alone is not a reconsideration trigger.
