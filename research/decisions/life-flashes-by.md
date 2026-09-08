# Candidate decision — Life Flashes By

Decision: **HOLD — NO EXPLICIT THIRD-PARTY REDISTRIBUTION GRANT FOUND**

This decision applies to the exact Life Flashes By package currently distributed by ScummVM and the creator-hosted release identified by ScummVM. It does not claim the creator could not authorize preservation hosting later.

## Evidence reviewed

Reviewed on 2026-09-08:

- ScummVM game downloads: `https://www.scummvm.org/games/`
- ScummVM package: `https://downloads.scummvm.org/frs/extras/SLUDGE/life.zip`
- package SHA-256: `9c8e61a9509e2b10080e735eade2db7f3a8dabee3f0febafeb537ed4e7eb4999`
- creator-hosted installer linked by ScummVM: `https://games.squinky.me/downloads/lfb/LifeFlashesBy-setup.exe`
- ScummVM target: `sludge:life`
- ScummVM detector payload: `LifeFlashesBy.slg` or `gamedata`, MD5 `a471759e071e5d2c0e8e6887607df778`, size `163,794,266` bytes

The creator-hosted installer provides strong provenance that the game was released by its creator. No creator-controlled statement granting third parties permission to redistribute, mirror, repackage, or browser-host the complete game data has been established.

## Exact package audit

The non-publishing package audit verified the ScummVM archive exactly:

- observed archive size: `159,698,577` bytes
- SHA-256: `9c8e61a9509e2b10080e735eade2db7f3a8dabee3f0febafeb537ed4e7eb4999`
- archive members: `168`
- top-level directory: `life`

Two notice-style files were found:

1. `Life Flashes By.app/Contents/Resources/Credits.html`
2. `Life Flashes By.app/Contents/Frameworks/SDL.framework/Versions/A/Headers/SDL_copying.h`

Those files document the SLUDGE engine and its bundled third-party libraries, including LGPL/GPL/MIT/BSD-style software licenses. They do **not** grant redistribution rights in Life Flashes By's game scripts, artwork, writing, music, audio, or other game data.

Automated audit markers such as `redistribute`, `all rights reserved`, and `redistribution_prohibited` occur inside the bundled software-license texts. They are not treated as a game-data license decision in either direction.

## What passed

- technical candidate: **yes**
- ScummVM engine/target: **sludge / life**
- exact ScummVM package hash: **verified**
- creator-hosted release provenance: **established**
- ScummVM detector identity: **published**

## What did not pass

These remain separate questions:

- **Creator made the game available for download:** established.
- **ScummVM hosts a preservation package:** established.
- **Kodaxa may redistribute the complete game data from its own browser archive:** not established.

The LGPL/GPL/MIT/BSD licensing of SLUDGE, SDL, and other runtime libraries cannot be used to broaden rights in the game data.

## Current status

- rights state: **HOLD**
- creator-controlled third-party redistribution grant: **not established**
- open-content license covering the complete game data: **not established**
- production manifest: **prohibited while this decision remains HOLD**
- public catalog: **do not add**
- non-publishing compatibility/package-identity work: **permitted**

## Reconsideration trigger

This decision can be revisited if the creator or another legitimate rights holder provides one of the following:

1. explicit permission to redistribute or mirror the Life Flashes By game data;
2. explicit permission covering extracted/browser/WebAssembly hosting;
3. an open-content license covering the required game assets;
4. a creator-controlled source/release repository whose terms clearly cover redistribution of the complete playable data set.

Another freeware/free-download listing, preservation mirror, or engine license alone is not a reconsideration trigger.
