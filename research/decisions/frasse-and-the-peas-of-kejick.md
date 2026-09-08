# Candidate decision — Frasse and the Peas of Kejick

Decision: **HOLD — COPYING GRANT DOES NOT CLEANLY COVER BROWSER REPACKAGING**

This decision applies to the exact v1.04 package currently distributed by ScummVM. It does not claim that the game may never be hosted with additional permission from the author.

## What passed

The exact ScummVM package was audited successfully:

- source: `https://downloads.scummvm.org/frs/extras/SLUDGE/frasse-1.04.zip`
- SHA-256: `8c517241389073f8577b805ecd730cf255c867220ff108d837b21026d90c06cd`
- observed archive size: 12,769,570 bytes
- six safe archive members
- package notice: `frasse-1.04/Readme.rtf`
- version identified by the author readme: 1.04
- author/copyright: Rikard Peterson, 2003–2007

## Rights language found

The author grants permission to copy the game in **unaltered form** and give it to other people. The same paragraph explains what "unaltered form" means: the installer downloaded from the author's site, and it expressly says the game may not be packaged differently.

The readme also says the game may not be sold without the author's permission, including CD compilations and magazine cover discs.

That is materially stronger evidence than a generic freeware label, but it is also a narrower grant than Abandonware needs.

## Why browser hosting does not pass yet

Abandonware's ScummVM pipeline does not simply mirror the historical installer byte-for-byte. To make a title directly playable in a browser it extracts the game payload into a generated HTTP filesystem, supplies a ScummVM configuration, and serves the resulting files beside a WebAssembly runtime.

Because the author explicitly tied permitted copying to the original unaltered package and prohibited different packaging, treating that browser materialization as unquestionably authorized would ignore a stated condition of the grant.

The fact that ScummVM currently provides a ZIP containing the game is useful provenance but does not expand the author's license for Kodaxa.

## Current status

- technical candidate: **yes**
- ScummVM engine/target: **sludge / frasse**
- exact package provenance: **verified**
- package safety: **verified**
- affirmative copying permission: **yes, conditionally**
- browser-repackaging permission: **not established**
- commercial distribution: **permission required**
- production manifest: **prohibited while this decision remains HOLD**
- public catalog: **do not add**

## Reconsideration trigger

This can be revisited if one of the following is found:

1. direct permission from Rikard Peterson covering browser/WebAssembly hosting or extraction of the game payload,
2. a later license that explicitly permits redistribution in different packaging or formats,
3. an author-controlled open-source/open-content release with terms covering the required game assets.

Another freeware/download listing by itself is not enough.
