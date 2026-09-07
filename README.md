# ABANDONWARE

A preservation-first browser arcade for keeping classic PC games playable on modern browsers.

The project name describes the cultural problem, **not a legal status**. Old, unsupported, unavailable, or commercially abandoned software is not automatically free to copy. Abandonware therefore treats **compatibility**, **provenance**, and **redistribution rights** as separate gates.

## Current archive

There are currently **8 audited browser-ready games across 2 browser execution runtimes**.

| Game | Original platform | Browser runtime | Rights basis |
| --- | --- | --- | --- |
| Xargon 3.0 | DOS | js-dos / DOSBox | Allen W. Pilgrim 2008 freeware grant |
| Kiloblaster 2.0a | DOS | js-dos / DOSBox | Allen W. Pilgrim 2008 freeware grant |
| Beneath a Steel Sky | DOS | ScummVM Web | Revolution Software freeware redistribution license |
| Flight of the Amazon Queen | DOS | ScummVM Web | freeware redistribution license |
| Lure of the Temptress | DOS | ScummVM Web | Revolution Software freeware redistribution license |
| Mystery House | Apple II | ScummVM Web | public-domain release |
| Drascula: The Vampire Strikes Back | DOS | ScummVM Web | Alcachofa Soft freeware redistribution permission |
| DreamWeb | DOS | ScummVM Web | Creative Reality freeware redistribution license; game data remains unmodified |

Commercial titles such as DOOM, Commander Keen 4, Jazz Jackrabbit, SimCity 2000, Monkey Island, and Diablo are **not** hosted merely because they are old. They remain local-file or future compatibility targets unless a valid redistribution basis is established.

## Execution architecture

### js-dos 8.4.1 / DOSBox

The DOS execution layer is self-hosted from the official js-dos `8.4.1` release artifact.

Pinned records:

- js-dos commit: `be548f4fb3616c956bfcd35d7c36f6db91d6a8b8`
- emulator commit: `0d840292a74dad4574d5068d8cf934a4e580ea11`
- official release SHA-256: `26118692bbb180aec78ec1697eb1ea6b28ff410101870cfa3e68309914c7eaa6`
- runtime files: `runtime/jsdos/`
- provenance: `runtime/jsdos/PROVENANCE.json`
- source record: `runtime/jsdos/SOURCE.md`

`runtime/jsdos/bridge.js` forces js-dos to load emulator workers/binaries from `runtime/jsdos/emulators/`. The site does **not** depend on the mutable `v8.js-dos.com/latest` execution path.

### ScummVM Web 2026.3.0

The adventure-game execution layer is built from pinned ScummVM source rather than embedding a third-party iframe.

Pinned records:

- ScummVM version: `2026.3.0`
- source commit: `fed42f2068dcafc6aafa1c28c77e4c88def74b66`
- Emscripten SDK: `4.0.10`
- runtime files: `runtime/scummvm/`
- build manifest: `runtime/scummvm-build.json`
- generated provenance: `runtime/scummvm/PROVENANCE.json`
- corresponding-source record: `runtime/scummvm/SOURCE.md`

The current runtime only builds the engines needed by audited hosted titles: `sky`, `queen`, `lure`, `adl`, `drascula`, and `dreamweb`.

Each hosted ScummVM game launches directly through its configured target using the runtime URL hash, for example `runtime/scummvm/index.html#sky`.

## Audited game intake

A title does not become browser-ready because a download exists somewhere on the internet.

For a hosted game, the repository records:

- exact upstream package URL
- upstream rights/source record
- expected package hash
- rights basis
- runtime and target
- required launch configuration
- preserved license/readme notices where applicable
- generated artifact provenance

If any required gate fails, the title stays out of the browser-ready catalog.

### DOS pipeline

DOS manifests live in `games/manifests/`.

`tools/build_audited_game.py`:

1. downloads the pinned package
2. checks expected size and published hash
3. locates the declared launch target
4. creates the js-dos configuration
5. embeds provenance
6. writes deterministic generated ZIP metadata
7. produces a `.jsdos` artifact only after validation succeeds

`tools/verify_audited_bundle.py` verifies the final generated bundle.

`.github/workflows/materialize-audited-games.yml` rebuilds audited DOS bundles twice and compares hashes so nondeterministic output fails closed.

### ScummVM pipeline

`runtime/scummvm-build.json` is the manifest for the shared ScummVM runtime and its hosted game data.

`tools/materialize_scummvm_games.py`:

1. downloads each exact package
2. verifies its SHA-256
3. rejects unsafe ZIP paths
4. extracts into a dedicated game directory
5. requires package notices for licensed freeware unless the manifest explicitly records another reviewed rights basis such as public domain
6. validates the configured target path
7. generates `scummvm.ini`
8. writes aggregate runtime/game provenance

`.github/workflows/build-scummvm-sky.yml` builds the pinned ScummVM WebAssembly runtime and materializes all audited ScummVM titles.

## Rights records

Per-title records live under `docs/rights/`.

Current hosted records include:

- `xargon.md`
- `kiloblaster.md`
- `beneath-a-steel-sky.md`
- `flight-of-the-amazon-queen.md`
- `lure-of-the-temptress.md`
- `mystery-house.md`
- `drascula.md`
- `dreamweb.md`

A hosted package must have a defensible basis such as public-domain status, explicit freeware redistribution permission, an applicable open license, or direct rights-holder authorization. “Abandonware,” “not sold anymore,” or “available elsewhere” are not sufficient.

## Local restoration workbench

Games that cannot be redistributed can still be compatibility targets.

The browser workbench accepts:

- prepared `.jsdos` bundles
- ordinary DOS `.zip` archives

For ordinary ZIPs, the browser:

1. opens the archive locally with JSZip
2. detects `.EXE`, `.COM`, and `.BAT` candidates
3. ranks likely game executables above setup/config/uninstall utilities
4. lets the user choose a target
5. creates a temporary js-dos configuration in memory
6. launches the result through the self-hosted js-dos runtime

The selected local game archive is not uploaded to a Kodaxa backend.

This generic path will not handle every DOS title. CD-ROM layouts, copy protection, unusual disk images, Windows installers, large installations, and specialized audio/input setups require dedicated profiles.

## Repository integrity gate

`.github/workflows/validate-site.yml` verifies the archive as a whole.

It currently checks:

- front-end JavaScript syntax
- unique and complete catalog records
- every hosted record points to a real artifact
- every hosted record has a rights record and provenance source
- every hosted ScummVM hash target exists in the generated ScummVM provenance
- all audited DOS bundles still match their manifests
- self-hosted js-dos 8.4.1 files still match their recorded hashes
- the local js-dos emulator bridge still points to `runtime/jsdos/emulators/`
- the mutable js-dos `/latest/` CDN has not been reintroduced
- ScummVM runtime/game provenance still matches the pinned build manifest

A UI-only change therefore cannot silently turn an unaudited or missing file into a browser-ready game without CI failing.

## Run locally

The site is static, but WebAssembly assets must be served over HTTP(S) rather than opened through `file://`.

```bash
python -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

No front-end build step is required for an already-materialized checkout.

## Main repository layout

```text
index.html                         archive UI shell
app.js                             catalog + launcher behavior
data/games.js                      public restoration catalog
styles.css                         main visual system
restoration.css                    runtime/restoration UI styles
covers-extra.css                   additional original catalog cover treatments

games/*.jsdos                     generated audited DOS artifacts
games/manifests/*.json             audited DOS intake manifests

runtime/jsdos/                     pinned self-hosted js-dos 8.4.1 runtime
runtime/jsdos-build.json            js-dos source/release pins
runtime/scummvm/                   generated ScummVM Web runtime + audited data
runtime/scummvm-build.json          ScummVM source/game pins

docs/rights/                      per-title rights/provenance records
tools/                             materialization and verification tools
.github/workflows/                 build and integrity gates
```

## Next technical layers

The strongest next additions are:

1. more individually audited freeware/public-domain titles
2. local user-data intake for commercial ScummVM games
3. tested Windows 9x/DOSBox-X profiles
4. save export/import portability
5. controller and touch profiles
6. self-hosting the remaining non-runtime browser dependencies
7. automated browser launch smoke tests
8. richer game-specific restoration records and controls documentation

## Project rule

**Compatibility, provenance, and redistribution are separate questions.**

A game can work perfectly in a browser and still remain local-files-only. A freely redistributable game is not browser-ready until its exact source artifact, execution path, and rights basis are reproducible and auditable.
