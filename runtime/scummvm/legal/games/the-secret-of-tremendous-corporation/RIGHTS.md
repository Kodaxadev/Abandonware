# The Secret of Tremendous Corporation — rights and provenance record

Status: **OPEN-LICENSE CANDIDATE / SOURCE-BACKED / VERSION 6**

This record applies only to the Version 6 game data identified below. It does not grant or infer rights to unrelated trademarks, store artwork, DLC, soundtrack files, or third-party material outside the audited game/source packages.

## Identity

- Title: The Secret of Tremendous Corporation
- Developers: Sebastian Krzyszkowiak, Konrad Burandt, Paweł Radej
- Public release date: 12 October 2015
- Engine: SLUDGE
- Browser interpreter: ScummVM
- ScummVM target: `tsotc`
- Audited edition: Version 6

The authors' current itch.io page identifies the three developers, labels the game Open Source/free-software, dates the release to 12 October 2015, and publishes Version 6 Windows, GNU/Linux, and source downloads.

https://dos.itch.io/the-secret-of-tremendous-corporation

The official project site identifies the same team and carries a CC-BY-SA 4.0 notice.

https://tremendouscorp.com/

Steam independently records the same three developers and the 12 October 2015 release date.

https://store.steampowered.com/app/380140

## License basis

The authors' current itch.io release metadata explicitly states:

- code license: GNU Lesser General Public License v3.0 (LGPL-3.0)
- asset license: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)

The author-linked source repository contains a full CC-BY-SA-4.0 `COPYING` file. Abandonware preserves that file from the exact `steam` release tag beside the corresponding-source snapshot.

https://github.com/dos1/AdventureTheGame

The source repository itself does not contain a separate LGPL notice. Abandonware therefore does not pretend that the preserved `COPYING` file is evidence of LGPL. The LGPL code declaration is sourced from the authors' official itch.io Version 6 metadata; the CC-BY-SA license text is independently preserved in the tagged source snapshot.

## Pinned corresponding source

The repository's `steam` tag resolves to the release-era source used for this preservation record:

- Git ref: `refs/tags/steam`
- commit: `29a5bc7fd603b6ccd41d93481bbcd3a1aa456d79`
- commit time: `2015-10-12T18:11:47+02:00`
- tree: `4558536cb66605e8213eec16c482896fe524fb98`
- file count: 135
- gitlinks/submodules: none
- deterministic source archive SHA-256: `8edfd894388f44f6cb21a3c75cc332069a6d6a6c4e15a34b8d50a8c50e5e7a4f`

Preserved source notices:

- `COPYING` SHA-256 `a0bd498de6b7991f563789715e3cf9f9a77860b6bb5b2c2b072fb3bb36361008`
- `README.md` SHA-256 `713f6e1cef85f510713b206509a20a9cddecf1bf4d4a2589803f34ea3b445043`

The source audit is performed through a bare Git repository. No source file, installer, build script, or game binary is executed during audit.

## Exact ScummVM package

ScummVM's current downloadable-games catalog identifies the SLUDGE Version 6 package used by Abandonware.

- URL: `https://downloads.scummvm.org/frs/extras/SLUDGE/tsotc-v6.zip`
- SHA-256: `4493047914318167cf1e955795028c65592be99fe620a389745c5d6bec97d24b`
- archive size observed by Abandonware audit: 34,612,275 bytes
- archive top-level directory: `tsotc-v6`
- expected ScummVM detection payload: `gamedata.slg`
- ScummVM detection MD5: `7d677e79fb842df00c4602864da13829`
- ScummVM detection size: 34,740,918 bytes

https://www.scummvm.org/games/

## Package notice is not the game license

The exact ScummVM ZIP contains `tsotc-v6/LICENSE.TXT`. That file is a Google copyright notice using a BSD-style license which expressly permits redistribution and use in source and binary forms, with or without modification, subject to its listed conditions.

It is preserved because it ships in the exact package. It is **not** used as evidence that Google licenses the whole game. The game's rights basis is the authors' open-license declaration and author-linked source described above.

The phrase `All rights reserved` inside that BSD-style notice is not treated as a redistribution prohibition because the same notice immediately grants redistribution rights. Automated candidate-audit restriction markers are review aids, not legal classifiers.

## Attribution and ShareAlike handling

Abandonware distributes the game data unmodified from the exact hash-pinned ScummVM package and preserves its bundled notice. The archive also preserves the author-linked Version 6 source record and CC-BY-SA license text and identifies Sebastian Krzyszkowiak, Konrad Burandt, and Paweł Radej as the developers.

If Abandonware later modifies CC-BY-SA-covered game material rather than merely performing technical hosting/runtime adaptation, that modified material must be reviewed for the ShareAlike and change-indication requirements before publication.

## Scope warning

This record does not imply that:

- the game's title or logos are licensed as trademarks;
- paid soundtrack/DLC packages are covered by this game-data record;
- every unrelated file published by the developers uses these licenses;
- the Google BSD-style package notice licenses the game as a whole.

Production hosting remains fail-closed on exact package hash, source provenance, preserved license evidence, runtime materialization, target-path validation, and browser execution tests.
