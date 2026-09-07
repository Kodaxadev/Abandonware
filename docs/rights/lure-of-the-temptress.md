# Lure of the Temptress — rights and provenance record

Status: **HOSTABLE / AUDITED SOURCE**

This record applies to the unchanged English DOS freeware package used by the browser restoration. It does not establish rights to unrelated Revolution Software games, promotional assets, fan translations, or third-party material outside the audited package.

## Identity

- Title: Lure of the Temptress
- Copyright holder identified by the freeware license: Revolution Software Ltd
- Original DOS release: 1992
- Browser package: Freeware Version 1.1 (English)
- Browser interpreter: ScummVM
- ScummVM target: `lure`

## Redistribution basis

The preserved Lure of the Temptress license explicitly permits free distribution of the game on any medium provided the license and associated copyright notices/disclaimers remain intact. It permits reasonable copying fees and aggregation in larger distributions, prohibits charging for the game itself, and permits modified versions when prominently identified as modified.

Abandonware keeps the game data unchanged, preserves the package notices, and serves access for free.

## Primary/current package evidence

ScummVM currently lists Lure of the Temptress as one of its downloadable freeware games for version 2026.3.0. The selected package is:

- Edition: Freeware Version 1.1 (English)
- URL: `https://downloads.scummvm.org/frs/extras/Lure%20of%20the%20Temptress/lure-1.1.zip`
- Published SHA-256: `f3178245a1483da1168c3a11e70b65d33c389f1f5df63d4f3a356886c1890108`
- ScummVM downloads record: https://www.scummvm.org/games/

ScummVM's 30 November 2007 announcement also records that Lure of the Temptress was made available as freeware and directs users to the available language packages.

https://www.scummvm.org/news/20071130/

## License corroboration

Debian Sources preserves the complete Lure of the Temptress redistribution license and identifies the game data as copyright Revolution Software Ltd:

https://sources.debian.org/copyright/license/lure-of-the-temptress/1.1%2Bds2-3/

The preserved license grants the distribution/modification rights described above.

## Runtime provenance

The browser interpreter is the source-pinned ScummVM 2026.3.0 WebAssembly runtime shared by the archive's audited ScummVM titles. `runtime/scummvm-build.json` pins the exact source commit, Emscripten SDK, enabled engines, game packages, hashes, and rights records. The generated runtime carries the same information in `runtime/scummvm/PROVENANCE.json` plus corresponding-source information and ScummVM GPL materials.

## Build gate

Before this title is materialized, CI must:

1. download the exact ScummVM-hosted English package above
2. verify the published SHA-256
3. preserve the package license/readme notice
4. place the unchanged game data into its dedicated ScummVM HTTP filesystem directory
5. write a `[lure]` target pointing only to that directory
6. record the package identity in runtime provenance
7. fail closed on any hash, notice, build, or provenance mismatch

## Scope warning

Revolution Software's freeware grants for specific older titles do not imply a blanket license over the company's catalog. Each additional game and data package requires its own audit.
