# Beneath a Steel Sky — rights and provenance record

Status: **HOSTABLE / AUDITED SOURCE**

This record applies to the original freeware game data used by the browser restoration. It does not apply to later remasters, storefront-specific extras, unrelated Revolution Software titles, third-party enhanced soundtracks, or promotional assets not contained in the audited archive.

## Identity

- Title: Beneath a Steel Sky
- Developer: Revolution Software Ltd
- Original release: 1994
- Original platform for this package: DOS
- Browser data package: Freeware Floppy Version 1.3
- Browser interpreter: ScummVM

## Redistribution basis

The freeware package's surviving readme grants permission to distribute the game for free on any medium provided the readme and associated copyright notices/disclaimers remain intact. It permits reasonable copying fees and aggregation in larger distributions, prohibits charging for the game itself, and permits modified versions when clearly marked as modified.

Abandonware uses the conservative path: the original game data is kept unchanged, the package notices are preserved, access is free, and the browser runtime is treated as a separate open-source component.

## Primary/current distribution evidence

ScummVM currently lists Beneath a Steel Sky among its downloadable freeware games and publishes both CD and floppy packages. For the floppy package it publishes SHA-256:

`d0bac1bd61747a67e885fa44b78c78887bf2b15d3dfa2790c483fad651078818`

Source page:

https://www.scummvm.org/games/

Exact source archive:

https://downloads.scummvm.org/frs/extras/Beneath%20a%20Steel%20Sky/BASS-Floppy-1.3.zip

## License corroboration

A preserved copy of the package readme is available through Debian Sources. It states that the game may be distributed for free on any medium if the readme and copyright notices/disclaimers remain intact and identifies the game content as copyright Revolution Software Ltd.

https://sources.debian.org/src/beneath-a-steel-sky/0.0372-6/readme.txt

Revolution Software's current product page also identifies the original game and notes that current desktop distributions are powered by ScummVM:

https://revolution.co.uk/games_catalog/beneath-a-steel-sky/

## ScummVM runtime provenance

The browser interpreter is built from ScummVM 2026.3.0, pinned to commit:

`fed42f2068dcafc6aafa1c28c77e4c88def74b66`

That is the commit referenced by the annotated upstream `v2026.3.0` tag. The runtime build uses ScummVM's own Emscripten/WebAssembly backend and enables only the `sky` engine for this first restoration.

ScummVM is distributed under the GPL. The generated browser runtime therefore ships with ScummVM's license/copyright materials and an exact corresponding-source pointer/build record. Abandonware's own MIT license does not replace or relicense ScummVM.

## Build gate

The automated build must:

1. check out the exact ScummVM commit above
2. build the official Emscripten target with the `sky` engine
3. download the exact ScummVM-hosted freeware game archive
4. verify the published SHA-256 before extracting it
5. preserve the game's readme/copyright notices in the served data
6. generate HTTP filesystem indexes required by ScummVM Web
7. include ScummVM COPYING/COPYRIGHT/license material and build provenance
8. refuse to commit any generated file at or above GitHub's 100 MB per-file limit

A failed source hash, missing license notice, failed compile, or oversized artifact leaves this game unavailable rather than weakening the gate.
