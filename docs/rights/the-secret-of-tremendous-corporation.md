# The Secret of Tremendous Corporation — rights and provenance record

Status: **HOLD — THIRD-PARTY ASSET RIGHTS INCOMPLETE — DO NOT HOST**

This record applies only to the Version 6 game data identified below. The title has strong first-party open-license evidence, but the pinned release source also contains separately credited third-party music, sound effects, voice work, and a font. Several of those credits carry noncommercial or otherwise asset-specific terms. Until those exceptions are resolved at asset level, the exact compiled game data is not approved for Abandonware production hosting.

## Identity

- Title: The Secret of Tremendous Corporation
- Developers: Sebastian Krzyszkowiak, Konrad Burandt, Paweł Radej
- Public release date: 12 October 2015
- Engine: SLUDGE
- Browser interpreter candidate: ScummVM
- ScummVM target: `tsotc`
- Audited edition: Version 6

The authors' current itch.io page identifies the three developers, labels the game Open Source/free-software, publishes Version 6 downloads/source, and states:

- code license: GNU Lesser General Public License v3.0 (LGPL-3.0)
- asset license: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)

https://dos.itch.io/the-secret-of-tremendous-corporation

That is strong evidence for material the developers have authority to license. It is not, by itself, treated as proof that every separately credited third-party work embedded in the game was relicensed by its copyright holder.

## Pinned corresponding source

The repository's `steam` tag resolves to the release-era source used for this preservation record:

- Git ref: `refs/tags/steam`
- commit: `29a5bc7fd603b6ccd41d93481bbcd3a1aa456d79`
- commit time: `2015-10-12T18:11:47+02:00`
- tree: `4558536cb66605e8213eec16c482896fe524fb98`
- file count: 135
- gitlinks/submodules: none
- deterministic source archive SHA-256: `8edfd894388f44f6cb21a3c75cc332069a6d6a6c4e15a34b8d50a8c50e5e7a4f`

Preserved source evidence includes:

- `COPYING` — CC-BY-SA-4.0 text — SHA-256 `a0bd498de6b7991f563789715e3cf9f9a77860b6bb5b2c2b072fb3bb36361008`
- `README.md` — SHA-256 `713f6e1cef85f510713b206509a20a9cddecf1bf4d4a2589803f34ea3b445043`
- `rooms/room06/room06.slu` — in-game credit and license text — SHA-256 `f275cf3deb5a36d7b95b3b7e8ee7fe4489eab25afb940c3596948143b3e042c6`

The in-game credit script is material rights evidence and must remain preserved beside the source snapshot. It explicitly says the **game code and original assets** are CC-BY-SA 3.0 while separately listing third-party works and their own licenses/attributions.

https://github.com/dos1/AdventureTheGame/tree/steam

## Exact ScummVM package

ScummVM's downloadable-games catalog identifies the Version 6 package audited by Abandonware:

- URL: `https://downloads.scummvm.org/frs/extras/SLUDGE/tsotc-v6.zip`
- SHA-256: `4493047914318167cf1e955795028c65592be99fe620a389745c5d6bec97d24b`
- archive size observed by Abandonware audit: 34,612,275 bytes
- archive top-level directory: `tsotc-v6`
- expected detection payload: `gamedata.slg`
- ScummVM detection MD5: `7d677e79fb842df00c4602864da13829`
- ScummVM detection size: 34,740,918 bytes

https://www.scummvm.org/games/

The package also contains SLUDGE/runtime notices (`AUTHORS.TXT`, `Credits.html`, `LICENSE.TXT`, `PATENTS.TXT`). They are preserved as package evidence but do **not** license the game data as a whole.

## Why the prior approval was withdrawn

The source-backed review originally relied too heavily on the current itch.io `Asset license: CC-BY-SA-4.0` field and the source `COPYING` file. The pinned Steam-tag source shows that this is insufficient for the complete compiled payload because the game itself distinguishes original material from third-party material.

The end credits enumerate:

- Kevin MacLeod music under CC-BY 3.0;
- `Pamiętam (5th Anniversary Edition) [instrumental]` by Behedos under CC-BY-SA 3.0;
- `Captain` by Jakub Marszałkowski under CC-BY-NC-SA 3.0;
- 21 separately credited Freesound effects;
- an elevator voice by Linnea Sage / LinneaS88;
- the `Cool Story` font by Peter Olexa.

Those works need their own rights chain. A blanket project-level license cannot be assumed to override third-party licenses unless there is evidence that the project authors had authority to do so.

## Known third-party findings

The asset ledger is incomplete, but the following findings are already enough to block a blanket production approval.

| Credited work | Evidence | Current review state |
| --- | --- | --- |
| `tv turn off.aif` — harpoyume | The developers' own early release page labels it `Attribution Noncommercial`; the current Freesound page identifies Attribution-NonCommercial 3.0. | **Blocking:** redistribution may be allowed, but commercial use is restricted. Abandonware has no site-wide noncommercial deployment invariant and must not silently depend on one. |
| `Phone Call Tone.wav` — henrique85n | Current Freesound page identifies Attribution-NonCommercial 4.0. | **Blocking:** known NC restriction unless separate permission/relicense evidence is established. |
| `Nail Scratch.wav` — twiggles | Current Freesound page identifies the Sampling+ license. Its whole-sound distribution permission is noncommercial, while commercial permission is tied to sampling/creative transformation. | **Blocking/unclear:** simple inclusion or format conversion is not assumed to satisfy the commercial transformation branch. |
| `Captain` — Jakub Marszałkowski | Pinned Steam-tag credits say CC-BY-NC-SA 3.0. A current Behedos/Bandcamp page links the track to CC-BY-SA 4.0. | **Potentially resolvable:** later open-license evidence exists, but Abandonware has not yet established the authority/timing chain for the exact copy compiled into Version 6. |
| `Cool Story` — Peter Olexa | Current DaFont author page states 100% free and the font page says free for personal and commercial use. | **Likely non-blocking**, but attribution/source evidence should still be preserved. |

Primary review pages:

- `https://dosowisko.net/gjgagsas/`
- `https://dos.itch.io/the-game-jam-game-about-games-secrets-and-stuff`
- `https://freesound.org/people/harpoyume/sounds/86034/`
- `https://freesound.org/people/henrique85n/sounds/162019/`
- `https://freesound.org/people/twiggles/sounds/94667/`
- `https://behedos.bandcamp.com/track/captain`
- `https://www.dafont.com/coolstory.font`

The remaining Freesound entries, voice credit, music mappings, and any asset-specific notices must be completed before reconsideration.

## Production rule

While this record is HOLD:

- do not list TSOTC in `runtime/scummvm-build.json`;
- do not add it to the public browser catalog;
- do not materialize or deploy `gamedata.slg` as a public production game;
- compatibility experiments and source/package audits may continue in non-publishing research lanes;
- retain the exact package hash and source snapshot so later findings can be evaluated against a stable release identity.

## Reconsideration paths

Production review can resume only when one of these paths closes the third-party exceptions:

1. **Complete rights ledger:** identify every embedded third-party asset, its exact source/version, license, required attribution, and whether that license permits Abandonware's deployment model.
2. **Additional permissions:** preserve author/rightsholder evidence granting the missing redistribution/commercial rights for NC or otherwise unclear works.
3. **Clean rebuild:** replace/remove unresolved or NC assets from the open source project, rebuild the SLUDGE data from a pinned source revision, preserve modification/ShareAlike notices, and audit the rebuilt payload as a new exact artifact rather than claiming it is the original ScummVM Version 6 package.
4. **Explicit noncommercial product boundary:** only if Abandonware intentionally adopts and enforces a durable noncommercial deployment policy that satisfies every relevant license. No such policy currently exists, so this is not an assumed workaround.

## Scope warning

This record does not claim that the developers acted improperly or that the game cannot legally be redistributed. It records a narrower preservation conclusion: **the evidence currently preserved by Abandonware is not sufficient to approve redistribution of the exact Version 6 compiled game data under a simple LGPL/CC-BY-SA blanket.**

The repository's fail-closed rights policy therefore controls until the third-party asset chain is complete.
