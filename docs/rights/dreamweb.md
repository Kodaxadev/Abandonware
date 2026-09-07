# DreamWeb — rights and provenance record

Status: **HOSTABLE / AUDITED FREEWARE SOURCE**

This record applies to the English UK freeware floppy DOS package distributed by ScummVM. It does not cover CD editions, other language packages, manuals outside the selected archive, promotional art, trademarks, or third-party repacks unless separately audited.

## Identity

- Title: DreamWeb
- Original developer: Creative Reality
- Authors/copyright holders identified by the freeware record: Neil Dodwell and David Dew trading as Creative Reality
- Original release: 1994
- Platform used by this restoration: DOS
- Browser interpreter: ScummVM
- ScummVM engine: `dreamweb`

## Redistribution basis

ScummVM announced the official freeware release of DreamWeb on 21 October 2012, crediting Creative Reality and Neil Dodwell and publishing the freeware versions from its own download infrastructure.

https://www.scummvm.org/news/20121021/

The preserved DreamWeb 1.1 license permits free distribution on any medium provided the license and copyright notices/disclaimers remain intact. It permits reasonable copying fees and aggregation, but does not permit modifying the game data. Abandonware therefore treats the selected game-data files as **immutable**: the verified archive is extracted into the ScummVM filesystem without altering the files inside it; emulator configuration/provenance remain separate.

A Fedora FESCo licensing discussion preserves the DreamWeb 1.1 license text and identifies it as redistributable but non-modifiable:

https://pagure.io/fesco/issue/1465

## Exact package selected by Abandonware

ScummVM's current 2026.3.0 game catalog publishes:

- Edition: Freeware Floppy DOS Version (English UK)
- URL: `https://downloads.scummvm.org/frs/extras/Dreamweb/dreamweb-uk-1.1.zip`
- Published SHA-256: `0f98e5fbeedfff5f5b904220d3bd3288da5a272f9192da03f2160c5edb8cdfb3`
- Current catalog: https://www.scummvm.org/games/

The much larger CD/language/manual packages are outside this first restoration record.

## Build gate

Before this title is browser-ready, CI must verify the exact published SHA-256, safely extract the archive without rewriting game files, preserve its in-package license/readme notice, build the exact pinned ScummVM `dreamweb` engine, validate the configured data path, and record package provenance.

## Content note

ScummVM notes that DreamWeb was rated 15 on its original release and contains a disturbing story and violence. That does not prevent preservation, but the eventual game card should carry an age/content note rather than presenting it as an all-ages title.

## Scope warning

The DreamWeb freeware grant applies to the released DreamWeb packages under their stated terms. It does not imply rights to other Creative Reality or Empire Interactive titles.
