# Dračí Historie — rights and provenance record

Status: **RIGHTS APPROVED / SOURCE PRESERVATION PENDING / DO NOT HOST YET**

This record applies to the original NoSense game Dračí Historie and, for the first production target, the English 2012 game archive supplied by the original developer site. Production remains fail-closed until the corresponding GPL source/archive set is hash-pinned and preserved beside the runtime.

## Identity

- Title: Dračí Historie
- Original release: 1995
- Original group: NoSense
- Programming: Pavel Pospíšil, Lukáš Svoboda, Robert Špalek
- Graphics: Jakub Dvorský, Pavel Jura, Jan Pokorný
- Music: Radovan Kramář
- Browser interpreter candidate: ScummVM
- ScummVM engine/target: `draci` / `draci`
- First archive target: English 2012 release

The original developer-maintained project page is:

`https://www.ucw.cz/draci-historie/`

It identifies the original team, describes the 1995 release and later restoration work, publishes the game archives and source materials, and states that the game is now released under GNU GPL version 2.

## Explicit license grant

The original developer site does not merely call the title freeware. It states that:

- the game is now released under **GNU GPL version 2**;
- the game may be downloaded for free including source code;
- source code for the game scripts is available;
- source graphics, sounds and animations are available;
- original game files, including complete graphics, animations, sounds, scripts, editor working files and variants, are available separately;
- the original MIDI music is available separately.

This is the rights basis for Abandonware. ScummVM availability and Gentoo packaging are corroborating evidence, not the source of the grant.

## Exact English game artifact

Original developer URL:

`https://www.ucw.cz/draci-historie/binary/dh-en-2012.zip`

Independent Gentoo packaging identifies the same original-site filename and URL, classifies the game `GPL-2`, and pins the archive by size and SHA-512.

Abandonware's direct-author-release audit verified the original-site bytes against those independent pins and against ScummVM's detector:

- archive size: `3,310,860` bytes
- SHA-256: `807c625902051639a35871da2c5138615ae2c327c5f12eebb8dd22628874ae23`
- SHA-512: `a9b5ff15305c961f288fdf915f56ca204a2ebe5370dcf56c20a0057cf721c45445a20479a39fe1f5443e79e7c95bd5771abef2115396c418442d2e5e400ce10a`
- archive members: `82`
- detector payload: `init.dfw`
- detector payload size: `906` bytes
- detector payload MD5: `b890a5aeebaf16af39219cba2416b0a3`
- detector payload SHA-256: `17f605245497c04a2ba7901c50d2d3760c445b16a5602877f2ed70b12818d860`

The detector identity matches ScummVM's English Dračí Historie entry exactly.

The archive's `readme.txt` is an old CD-era operational readme and does not itself contain the later GPL release declaration. The authoritative license evidence is therefore the original developer's current restoration/download page, corroborated by the separately published source set and Gentoo's GPL-2 package metadata.

## Independent packaging corroboration

Gentoo's `games-rpg/draci-historie` package:

- uses the original developer URL as `SRC_URI`;
- classifies the game as `LICENSE="GPL-2"`;
- defaults to the English 2012 package;
- runs it with ScummVM target `draci`;
- independently pins the English archive's exact size and SHA-512.

This is useful independent provenance, but Abandonware does not rely on Gentoo to grant rights that the original developers did not grant themselves.

## Corresponding source set

The original developer page exposes the pieces needed to preserve the modifiable source forms rather than only the compiled game archive:

1. `old-sources.zip` — original source code, with later bug fixes;
2. `old-gfx.zip` — complete original graphics, animations, sounds and scripts, including variants/editor working files, excluding MIDI;
3. `old-midi.zip` — original MIDI music.

These source archives are currently in the direct-release hash-discovery/pinning lane. Discovery-mode hashes are not accepted as production evidence. Each archive must be updated to an exact pinned size/SHA-256 or SHA-512 record, rerun successfully in pinned mode, and then preserved in the repository with provenance before this candidate can become production-approved.

## Production gate

Until source preservation closes:

- do not add Dračí Historie to `runtime/scummvm-build.json`;
- do not expose it in the browser catalog;
- do not materialize the game archive into the public runtime;
- compatibility work and non-publishing artifact/source audits may continue;
- do not change the candidate to `APPROVED_OPEN_LICENSE` merely because the game archive itself is already verified.

## Intended production handling

Once the source set is pinned and preserved:

- use the exact original developer English archive identified above;
- preserve GPL-2 license/provenance material beside the game runtime;
- preserve the corresponding source archives and their hashes;
- compile/include ScummVM's `draci` engine from the already pinned ScummVM source revision;
- run target-path validation and browser smoke testing before catalog promotion.

No modification of the original game archive is required for the planned ScummVM route.
