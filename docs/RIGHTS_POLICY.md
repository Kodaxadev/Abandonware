# Game Rights & Hosting Policy

This project treats **technical compatibility** and **permission to redistribute game data** as separate gates.

A title may be perfectly playable in the browser and still remain local-files-only.

## Status model

### LOCAL FILES

The emulator profile may exist, but the repository/site does not distribute the game data. The user supplies a legally obtained copy from their own machine or storage.

Use this status whenever redistribution rights are absent, uncertain, incomplete, or unsupported by primary/strong secondary evidence.

### RIGHTS REVIEW

There is evidence that a title may be redistributable, but the exact grant, package provenance, or file set still needs review.

A title in this state is not hosted.

### HOSTABLE

The project has a documented basis to publicly distribute the exact game-data package being served. The evidence and package hash must be recorded before the binary is added.

### BROWSER READY

The exact hosted or local-file profile has passed runtime verification for boot, controls, audio, saves, scaling, and a defined browser matrix.

`HOSTABLE` does not imply `BROWSER READY`, and `BROWSER READY` does not imply `HOSTABLE`.

## Evidence hierarchy

Prefer evidence in this order:

1. Direct license text distributed by the author/rights holder with the game.
2. Direct statement from the author/rights holder granting redistribution.
3. Official publisher/developer release page with explicit distribution terms.
4. A maintained archival distribution whose copying policy identifies the title-specific license and preserves package hashes/provenance.
5. Multiple reputable secondary archives that reproduce the same license text and release history.

The following are **not** enough on their own:

- “abandonware” labels
- age
- publisher closure
- lack of current sales
- a download being easy to find
- no known takedown request
- a source-code release that does not also cover required proprietary data
- “freeware” without checking what redistribution is actually permitted

## Package rule

Rights review applies to the **exact bytes we intend to serve**, not merely the game title.

Before hosting a package, record:

- title and version
- original author/developer/publisher
- package source URL
- date retrieved
- SHA-256
- package size
- license/permission text
- whether the grant covers executable code, data, music, artwork, and documentation
- any restrictions
- reviewer notes

## Initial candidate: Xargon

**State:** RIGHTS REVIEW — strong candidate, not yet hosted.

Evidence collected on 2026-09-07:

- DOS Games Archive identifies the full DOS release as a 2008 freeware release and states that author Allen W. Pilgrim released it as freeware: https://www.dosgamesarchive.com/download/xargon
- RGB Classic Games states that Allen Pilgrim released Xargon under the “Kiloblaster and Xargon Freeware License” on 4 August 2008: https://www.classicdosgames.com/game/Xargon.html
- The maintained SDL port states that all three episodes were released as freeware: https://github.com/Malvineous/xargon
- FreeDOS/ibiblio currently redistributes Xargon 3.0 and records its copying policy as “Kiloblaster and Xargon Freeware License,” with package checksum/provenance metadata: https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/repositories/1.1/html/en/games/index.html
- DOS Games Archive reproduces the license statement associated with Kiloblaster/Xargon, including Allen Pilgrim’s intent to allow broad use of the released source with stated restrictions: https://www.dosgamesarchive.com/download/kiloblaster/

Why it is not yet `HOSTABLE` here:

- We still need the exact package we intend to serve, its SHA-256, and the license text contained in or accompanying that package.
- The license language reproduced online discusses the included source code explicitly; the project should verify that the distributed registered-game package and accompanying materials clearly support public redistribution of the exact game data before rehosting it ourselves.

Until that final package-level check is complete, Xargon should remain a local/upstream-sourced test candidate rather than a binary committed to this repository.

## Takedown / dispute handling

If a rights holder or credible representative disputes a hosted title:

1. Disable public game-data delivery first.
2. Preserve the compatibility profile and metadata separately.
3. Reclassify the title as `LOCAL FILES` while the claim is reviewed.
4. Keep the emulator/runtime code available if it is independently licensed.
5. Record the decision and evidence trail.

The preservation goal is to keep software playable without making unsupported ownership claims.
