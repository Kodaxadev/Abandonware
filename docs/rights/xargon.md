# Xargon 3.0 — rights and provenance record

Status: **HOSTABLE / AUDITED SOURCE**

This record supports the unchanged registered DOS release used by the browser bundle. It does not grant rights to unrelated Epic MegaGames material, later ports, unused artwork, trademarks, or derivative games.

## Identity

- Title: Xargon / The Xargon Trilogy
- Original developer/publisher: Epic MegaGames
- Programmer/author associated with the freeware release: Allen W. Pilgrim
- Original platform: DOS
- Original release: 1993
- Registered release version: 3.0
- Included episodes: Beyond Reality, The Secret Chamber, Xargon's Fury

## Redistribution basis

Allen W. Pilgrim released the registered version of Xargon as freeware on 4 August 2008 and released the source code at the same time. The surviving Kiloblaster and Xargon Freeware License states an intent to permit broad use, including commercial use, while placing restrictions on derivative games resembling the originals and on prohibited subject matter.

For this project, the conservative interpretation is simple: **serve the unchanged freeware game package and do not use this grant as a license to create or distribute a derivative Xargon-like game.**

## Independent evidence

1. FreeDOS archived package record
   - https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/repositories/1.1/html/en/games/xargon/20150826.2/index.html
   - Identifies Xargon 3.0, Allen Pilgrim, DOS, and the `Kiloblaster and Xargon Freeware License` as the copying policy.
   - Publishes package size and SHA-1 used by the automated ingestion gate.

2. DOS Games Archive
   - https://www.dosgamesarchive.com/download/xargon/
   - Identifies the full registered package as a 2008 freeware release and identifies `XARGON/XARGON.BAT` as the executable path for its copy.

3. DOS Games Archive — Kiloblaster license record
   - https://www.dosgamesarchive.com/download/kiloblaster/
   - Preserves the 4 August 2008 Allen Pilgrim freeware-license statement covering both Kiloblaster and Xargon.

4. MobyGames
   - https://www.mobygames.com/game/1057/xargon/
   - Independently records that the entire registered three-episode game was made freeware in 2008 and that the registered version/source release occurred on 4 August 2008.

## Exact upstream package used by Abandonware

The site does not ingest an arbitrary abandonware mirror. It uses the archived FreeDOS package below:

- URL: `https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/repositories/1.1/games/xargon.zip`
- Expected size: `1,763,626` bytes
- Expected SHA-1: `9539c4c370be772ac92b83b092e90410da90f8b2`
- Copying policy named by FreeDOS: `Kiloblaster and Xargon Freeware License`

SHA-1 is retained because it is the package identifier published by the FreeDOS archive. The ingestion script also computes SHA-256 and embeds it inside the generated `.jsdos` bundle's provenance record.

## Build policy

`tools/build_audited_game.py` downloads the exact source URL and refuses to produce a browser bundle unless both the expected byte size and SHA-1 match. It then finds `XARGON.BAT`, adds only the emulator configuration/provenance files needed by js-dos, and writes `games/xargon.jsdos`.

The generated bundle contains `.jsdos/provenance.json` so the artifact carries its upstream identity with it.

## Scope warning

The freeware status of Xargon does **not** imply that all Epic MegaGames games, box art, promotional art, soundtrack assets outside the package, or third-party Xargon material are freely redistributable. Each additional asset or game must pass its own rights intake.
