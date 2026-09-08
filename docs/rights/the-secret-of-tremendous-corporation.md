# The Secret of Tremendous Corporation — rights and provenance record

Status: **HOLD — THIRD-PARTY ASSET RIGHTS INCOMPLETE — DO NOT HOST**

This record applies only to the Version 6 game data identified below. The title has strong first-party open-license evidence, but the pinned release source also contains separately credited third-party music, sound effects, voice work, and a font. Several of those credits carry noncommercial or otherwise asset-specific terms. Until those exceptions are resolved at asset level, the exact compiled game data is not approved for Abandonware production hosting.

The machine-readable asset ledger is:

`research/asset-rights/the-secret-of-tremendous-corporation.json`

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
- `rooms/room06/room06.slu` — English in-game credit/license text — SHA-256 `f275cf3deb5a36d7b95b3b7e8ee7fe4489eab25afb940c3596948143b3e042c6`
- `translations/polish.tra` — Polish translation containing the same credit/license material — SHA-256 `9df52bb72a95c795146ca1d711f4d2a0c1550c8a91867581ee083ae03b89f67b`

The in-game credit material is rights evidence and remains preserved beside the source snapshot. It explicitly says the **game code and original assets** are CC-BY-SA 3.0 while separately listing third-party works and their own licenses/attributions.

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

- eight Kevin MacLeod tracks under CC-BY 3.0;
- `Pamiętam (5th Anniversary Edition) [instrumental]` by Behedos under CC-BY-SA 3.0;
- `Captain` by Jakub Marszałkowski under CC-BY-NC-SA 3.0;
- 21 separately credited Freesound effects;
- an elevator voice by Linnea Sage / LinneaS88;
- the `Cool Story` font by Peter Olexa.

Those works require their own rights chain. A blanket project-level license is not assumed to override third-party licenses unless there is evidence that the project authors had authority to do so.

## Asset-ledger status

The current ledger contains **33 separately credited third-party records**:

- **23 clear records** under preserved CC0, CC-BY, or CC-BY-SA evidence;
- **4 known restrictive records**;
- **6 unresolved or provisional records**;
- **10 total production-blocking records** under the repository's fail-closed policy.

The four known restrictive records are:

| Credited work | Embedded mapping | Current state |
| --- | --- | --- |
| `Captain` — Jakub Marszałkowski | `rooms/room05/muzyczka.ogg` is a probable mapping; its 40.377 s duration closely matches the 0:41 credited soundtrack track. | **Blocking:** pinned credits say CC-BY-NC-SA 3.0. Replace it or preserve a rights-holder grant/relicense that covers the exact embedded work. |
| `Nail Scratch.wav` — twiggles | `rooms/room04/scratch.ogg`; upstream and embedded duration are both 0.608 s, and the game plays it directly as a scratch effect. | **Blocking:** Sampling+ evidence plus apparent whole-sound use is not sufficient for the current unrestricted production lane. |
| `Phone Call Tone.wav` — henrique85n | `rooms/room01/phone.ogg`; the game plays the excerpt during phone-call interactions. | **Blocking:** current source is CC-BY-NC 4.0. |
| `tv turn off.aif` — harpoyume | `rooms/room06/shutdown.ogg`; the game plays it when the machine is powered down. The developers' historical page also labels the upstream work Attribution Noncommercial. | **Blocking:** current source is CC-BY-NC 3.0. |

The six unresolved/provisional records are:

- `01002 closing safety lock.wav` — probable `rooms/room05/safe.ogg`; historical source license not yet recovered;
- `Drawer Slam 2.wav` — probable `rooms/room05/drawer-close.ogg`; historical source license not yet recovered;
- `toilette lid.wav` — probable `rooms/room06/lidopen.ogg` / `lidclose.ogg`; historical source license not yet recovered;
- `keyboarding2.wav` — `rooms/room05/keyboard.ogg`; strong historical CC0 evidence exists but primary/historical license evidence still needs preservation;
- Linnea Sage / LinneaS88 elevator voice — permission/license record unresolved; the intro source plays `rooms/roomElevator/elevator.webm`, making the movie the likely container for the credited voice, but that mapping is not yet promoted to exact evidence;
- `Cool Story` font — `coolstoryfont.duc`; author page allows personal/commercial use, but strict redistribution/derivative scope for the compiled font asset is not yet preserved.

Primary review pages include:

- `https://dosowisko.net/gjgagsas/`
- `https://dos.itch.io/the-game-jam-game-about-games-secrets-and-stuff`
- `https://freesound.org/people/harpoyume/sounds/86034/`
- `https://freesound.org/people/henrique85n/sounds/162019/`
- `https://freesound.org/people/twiggles/sounds/94667/`
- `https://www.dafont.com/coolstory.font`

## Bounded clean-rebuild target

A clean rebuild is now a bounded restoration task rather than an open-ended rights search. At minimum, a replacement build must eliminate or resolve every production-blocking ledger entry.

Known file targets are:

- `rooms/room05/muzyczka.ogg` — replace `Captain`;
- `rooms/room04/scratch.ogg` — replace `Nail Scratch.wav`;
- `rooms/room01/phone.ogg` — replace `Phone Call Tone.wav`;
- `rooms/room06/shutdown.ogg` — replace `tv turn off.aif`;
- `rooms/room05/safe.ogg` — resolve or replace the credited safety-lock effect;
- `rooms/room05/drawer-close.ogg` — resolve or replace `Drawer Slam 2.wav`;
- `rooms/room06/lidopen.ogg` and `rooms/room06/lidclose.ogg` — resolve or replace the credited lid sound;
- `rooms/room05/keyboard.ogg` — preserve primary CC0 evidence or replace;
- likely `rooms/roomElevator/elevator.webm` — resolve the Linnea Sage voice permission or rebuild the movie without unresolved voice content;
- `coolstoryfont.duc` — preserve adequate redistribution evidence or replace with an unambiguous open font.

A rebuilt title must receive a **new artifact identity**. Abandonware must not describe a modified rebuild as the original hash-pinned ScummVM Version 6 package.

## Production rule

While this record is HOLD:

- do not list TSOTC in `runtime/scummvm-build.json`;
- do not add it to the public browser catalog;
- do not materialize or deploy `gamedata.slg` as a public production game;
- compatibility experiments and source/package audits may continue in non-publishing research lanes;
- retain the exact package hash and source snapshot so later findings can be evaluated against a stable release identity.

The archive validation suite now also treats linked asset ledgers as part of the production rights boundary: an approved candidate cannot retain any `production_blocking` ledger entries.

## Reconsideration paths

Production review can resume only when one of these paths closes the third-party exceptions:

1. **Complete rights resolution:** every currently blocking asset obtains preserved permission/license evidence sufficient for the intended deployment.
2. **Clean rebuild:** replace/remove every blocking asset from a pinned source tree, rebuild the SLUDGE data, update credits and required ShareAlike/change notices, and audit the rebuilt payload as a new exact artifact.
3. **Explicit noncommercial product boundary:** only if Abandonware intentionally adopts and enforces a durable noncommercial deployment policy that satisfies every relevant license. No such policy currently exists, so this is not an assumed workaround.

## Scope warning

This record does not claim that the developers acted improperly or that the game cannot legally be redistributed. It records a narrower preservation conclusion: **the evidence currently preserved by Abandonware is not sufficient to approve redistribution of the exact Version 6 compiled game data under a simple LGPL/CC-BY-SA blanket.**

The repository's fail-closed rights policy therefore controls until the linked asset ledger contains no production-blocking entries.
