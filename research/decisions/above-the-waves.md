# Candidate decision — Above The Waves

Decision: **HOLD — NO EXPLICIT THIRD-PARTY REDISTRIBUTION GRANT FOUND**

This decision applies to the hash-pinned ScummVM v0.1 package currently queued by Abandonware. It does not claim that the authors could not authorize browser hosting later.

## Evidence reviewed

Reviewed on 2026-09-07:

- ScummVM game downloads: `https://www.scummvm.org/games/`
- ScummVM package: `https://downloads.scummvm.org/frs/extras/SLUDGE/atw.zip`
- package SHA-256: `270760dc77fa6b75ba1e9a8344df968698bdd73274992dc6d01fd6f9c352f1fa`
- ScummVM identifies the package as Above The Waves v0.1, SLUDGE engine, approximately 28.5 MiB
- ScummVM compatibility identifies `sludge:atw` as Excellent
- author-controlled game site: `https://atw.twolofbees.com/`
- author-controlled itch.io release: `https://cheeseness.itch.io/above-the-waves`
- current Two Lof Bees games page: `https://www.twolofbees.com/games.php`

The author-controlled sources identify the AdventureJam 2015 v0.1 release as free to play/download and continue to provide official platform downloads. The project is credited to Cheese/Cheeseness and Mim/Two Lof Bees.

## What passed

- technical candidate: **yes**
- ScummVM engine/target: **sludge / atw**
- exact ScummVM package hash: **published and recorded**
- current official-author provenance: **established**
- free download from the authors: **established**
- ScummVM runtime compatibility: **Excellent**

## What did not pass

Abandonware did not find author-controlled wording that explicitly grants third parties permission to redistribute, mirror, repackage, or browser-host the game data.

The official itch.io page offers the game for download, and the official site says the AdventureJam version is available to play for free. Neither statement is an affirmative redistribution license.

The official help page also tells users to use copies downloaded from the site's own download links. Abandonware is not treating that wording as a formal prohibition on redistribution, but it does not supply the missing rehosting grant either.

Those questions remain separate:

- **Free to download/play from the authors:** established.
- **Kodaxa may redistribute the game data from its own browser archive:** not established.

The LGPL/GPL licensing of the SLUDGE engine and tooling does not license Above The Waves' game data, artwork, audio, scripts, or other authored assets.

## Current status

- rights state: **HOLD**
- author-controlled third-party redistribution grant: **not established**
- open-content license covering the game assets: **not established**
- production manifest: **prohibited while this decision remains HOLD**
- public catalog: **do not add**
- local/upstream-sourced compatibility work: **permitted**

## Reconsideration trigger

This decision can be revisited if one of the following is found from Cheese/Cheeseness, Mim/Two Lof Bees, or another legitimate rights holder:

1. explicit permission to redistribute or mirror the v0.1 game data,
2. explicit permission covering extracted/browser/WebAssembly hosting,
3. an open-content license covering the required game assets,
4. an author-controlled source/release repository whose terms cover redistribution of the complete playable data set.

Another freeware/free-download listing, ScummVM package, or preservation mirror alone is not a reconsideration trigger.
