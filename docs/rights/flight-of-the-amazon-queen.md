# Flight of the Amazon Queen — rights and provenance record

Status: **HOSTABLE / AUDITED SOURCE**

This record applies to the unchanged freeware DOS floppy game data used by the browser restoration. It does not establish rights to unrelated artwork, later releases, third-party translations, or assets not contained in the audited package.

## Identity

- Title: Flight of the Amazon Queen
- Authors/game-content copyright holders identified by the freeware license: John Passfield and Steven Stamatiadis
- Original DOS release: 1995
- Browser package: Freeware Floppy Version
- Browser interpreter: ScummVM
- ScummVM target: `queen`

## Redistribution basis

The freeware package's surviving `readme.txt`, dated 15 March 2004, contains an explicit redistribution license. It permits free distribution of the game on any medium if the readme and associated copyright notices/disclaimers remain intact. It permits reasonable copying fees and aggregation in larger distributions, prohibits charging for the game itself, and permits modified game data when modified versions are clearly marked.

Abandonware preserves the original package notices and serves the game for free. It does not modify the game data except for placing the verified archive contents into the ScummVM HTTP filesystem.

## Primary/current package evidence

ScummVM currently publishes Flight of the Amazon Queen as a freeware game for ScummVM 2026.3.0. The selected small DOS package is:

- Edition: Freeware Floppy Version
- URL: `https://downloads.scummvm.org/frs/extras/Flight%20of%20the%20Amazon%20Queen/FOTAQ_Floppy.zip`
- Published SHA-256: `2e59de85f708cdb32bf85c85b394ac091c05f7647e856b71f5b3ae73fde761e0`
- ScummVM downloads record: https://www.scummvm.org/games/

## License corroboration

Debian Sources preserves the original freeware `readme.txt` and license text from the game package:

https://sources.debian.org/src/flight-of-the-amazon-queen/1.0.0-9/readme.txt

The license identifies all game content as copyright John Passfield and Steven Stamatiadis and explicitly grants the distribution/modification rights described above.

Debian also documents the game as DFSG-compliant game data whose license permits use, modification, and distribution:

https://sources.debian.org/src/flight-of-the-amazon-queen/1.0.0-8/debian/README.Debian/

## Runtime provenance

The browser interpreter is the same source-pinned ScummVM 2026.3.0 WebAssembly runtime used by the archive's other ScummVM titles. The exact ScummVM commit, Emscripten version, enabled engines, package URLs, package hashes, build command, and corresponding-source pointer are recorded in `runtime/scummvm-build.json` and `runtime/scummvm/PROVENANCE.json`.

## Build gate

Before this title is materialized, CI must:

1. download the exact ScummVM-hosted floppy archive above
2. verify the published SHA-256
3. preserve a readme/license notice from the archive
4. place the unchanged game data into its dedicated ScummVM HTTP filesystem directory
5. write a `[queen]` target pointing only to that directory
6. record the package identity in runtime provenance
7. fail closed on any hash, notice, build, or provenance mismatch

## Scope warning

This record does not grant blanket rights to commercial Krome Studios, Renegade, or ScummVM-supported titles. Each additional title and package must pass its own rights/source review.
