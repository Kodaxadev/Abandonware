# Kiloblaster 2.0a — rights and provenance record

Status: **HOSTABLE / AUDITED SOURCE**

This record supports the unchanged DOS freeware release used by the browser bundle. It does not treat other Epic MegaGames titles or unrelated promotional assets as redistributable.

## Identity

- Title: Kiloblaster
- Developer/publisher: Epic MegaGames
- Author associated with the freeware release: Allen W. Pilgrim
- Original platform: DOS
- Original release: 1992
- FreeDOS package version: 2.0a

## Redistribution basis

Allen W. Pilgrim's 4 August 2008 Kiloblaster and Xargon Freeware License covers both Kiloblaster and Xargon. The surviving statement permits broad use while imposing restrictions on derivative games resembling the originals and on prohibited subject matter.

Abandonware uses the conservative path: it serves the unchanged freeware game package and does not rely on the license as permission to create a derivative Kiloblaster-like game.

## Independent evidence

1. FreeDOS 1.4 archived package record
   - https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/repositories/1.4/html/en/games/kiloblas/20250410.0/index.html
   - Identifies Kiloblaster 2.0a, Allen Pilgrim, DOS, and `Kiloblaster and Xargon Freeware License` as the copying policy.
   - Publishes the exact package size and SHA-1 used by the automated ingestion gate.

2. DOS Games Archive
   - https://www.dosgamesarchive.com/download/kiloblaster/
   - Preserves full registered Kiloblaster volumes and the Allen Pilgrim 4 August 2008 freeware-license statement covering Kiloblaster and Xargon.
   - Its full-version package identifies `KILO.BAT` as the DOS launch command.

## Exact upstream package used by Abandonware

- URL: `https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/repositories/1.4/games/kiloblas.zip`
- Expected size: `1,586,517` bytes
- Expected SHA-1: `260a79198aaa221a9742d91af1a639b249c93d51`
- Copying policy named by FreeDOS: `Kiloblaster and Xargon Freeware License`

SHA-1 is retained because it is the identity published by the FreeDOS archive. The ingestion process additionally calculates SHA-256 and embeds it in the generated browser bundle's provenance record.

## Build policy

`tools/build_audited_game.py` refuses to emit `games/kiloblaster.jsdos` unless the downloaded FreeDOS package matches both its pinned size and SHA-1. The script then locates `KILO.BAT`, writes the js-dos configuration, and embeds `.jsdos/provenance.json`.

## Scope warning

The freeware grant for Kiloblaster and Xargon does not establish a blanket redistribution license for the rest of the Epic MegaGames catalog, trademarks, box art, or third-party assets. Those require separate review.
