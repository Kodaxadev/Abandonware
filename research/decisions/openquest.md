# Candidate decision — OpenQuest

Decision: **HOLD — THIRD-PARTY VERB BAR HAS NO FORMAL REDISTRIBUTION LICENSE**

This decision applies to the author-controlled OpenQuest Wintermute v1.0 release and source tag. It does not reject OpenQuest as a preservation target; it records the one rights exception that currently prevents the strict production lane from treating the whole release as CC-BY-4.0.

## Strong evidence in favor

OpenQuest has unusually strong first-party preservation evidence:

- Michael Sheail's original `README.AGS` says the source project and final executable are available, describes the project as a learning/reuse resource, and answers `what can be reused?` with `Anything you want.`
- the current OpenQuest repository README says the code and all assets are free to modify and distribute;
- the repository carries a CC-BY-4.0 `LICENSE`;
- JenniBee publishes the Wintermute source and v1.0 Windows/Linux/macOS releases from an author-controlled GitHub repository;
- ScummVM supports the Wintermute port as target `openquest` and records the `data.dcp` detection identity used for release comparison.

## Exact source and creator-release identity

The rights review is pinned to the actual `v1.0` tag rather than current `master`.

- repository: `https://github.com/JenniBee/openquest.git`
- ref: `refs/tags/v1.0`
- commit: `4f02a085fb2684aecc07413b9e804376d022b12d`
- creator Windows release: `openquest-win32.zip`
- creator archive size: `89,380,745` bytes
- creator archive SHA-256: `8a559d2c546bbc75ac81371adb94bd5bbdfd90471cb514c1b494a84d2f7949f7`
- payload: `data/data.dcp`
- payload size: `82,281,736` bytes
- payload SHA-256: `a4218ac420e6ba7221e8aabfa5df7cf08757e9cd5192e584353706482a580193`
- payload full-file MD5: `339df37f3e61b3b8fc22007d8f077f9c`
- ScummVM detector MD5: `16893e3fc15a211a49654ae66f684f28`
- detector hash span: first `5,000` bytes

ScummVM's Advanced Detector defaults to a 5,000-byte MD5 and the pinned Wintermute detector does not override that value. The creator-hosted `data.dcp` matches both the ScummVM detector MD5 under that rule and the full expected file size. Binary provenance is therefore established; the remaining HOLD is a rights issue, not an identity uncertainty.

## Release-tag exception

At `refs/tags/v1.0`, the repository `LICENSE` says the work is CC-BY-4.0 but adds that some libraries/assets were sourced outside the contributing community and directs readers to JenniBee's `dfafadventure` issue #1 for their licenses.

That author-controlled issue records:

- Wintermute engine — MIT;
- Verb Bar — **No license**, with a note that the original author allows modification.

The corresponding Wintermute verb-bar code is present in the tagged OpenQuest source under `data/interface/verbbar/`.

A surviving forum discussion provides useful context: the original verb-bar author said he would happily redistribute it under MIT if a formal license was needed. Abandonware does **not** convert that offer into an executed MIT license grant without clearer evidence that the code was actually relicensed.

## Current status

- first-party OpenQuest reuse/redistribution permission: **strongly established**
- repository project license: **CC-BY-4.0**
- author-controlled v1.0 binary release: **established and detector-matched**
- creator release archive/payload hashes: **recorded**
- ScummVM Wintermute runtime candidate: **yes**
- third-party Wintermute engine issue: **non-blocking / MIT**
- third-party Verb Bar issue: **HOLD — no formal redistribution license in the release record**
- production manifest: **do not add**
- public catalog: **do not add**
- non-publishing compatibility/rebuild work: **permitted**

## Reconsideration triggers

OpenQuest can return to production review if one of these is preserved:

1. an explicit MIT or other redistribution license from the Verb Bar rights holder covering the code used by OpenQuest;
2. an author/rightsholder statement clearly granting redistribution of the Verb Bar code, not merely modification;
3. a clean OpenQuest source revision/rebuild replacing the unlicensed Verb Bar with code under a documented compatible license.

Because source identity and creator-binary identity are now closed, this is a narrow blocker rather than a general uncertainty about the game.
