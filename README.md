# ABANDONWARE

A preservation-first browser arcade for keeping classic PC games playable on modern browsers.

The project name describes the cultural problem, **not a legal status**. Old, unsupported, unavailable, or commercially abandoned software is not automatically free to copy. Abandonware treats **compatibility**, **provenance**, and **redistribution rights** as separate gates.

## Current archive

There are currently **10 audited browser-ready games across 2 browser execution runtimes**.

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
| Sfinx | DOS | ScummVM Web | original L.K. Avalon developer redistribution permission |
| Sołtys | DOS | ScummVM Web | original L.K. Avalon developer redistribution permission |

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

The adventure-game execution layer is built from pinned ScummVM source rather than embedding an external retro-game service.

Pinned records:

- ScummVM version: `2026.3.0`
- source commit: `fed42f2068dcafc6aafa1c28c77e4c88def74b66`
- Emscripten SDK: `4.0.10`
- runtime files: `runtime/scummvm/`
- build manifest: `runtime/scummvm-build.json`
- generated provenance: `runtime/scummvm/PROVENANCE.json`
- corresponding-source record: `runtime/scummvm/SOURCE.md`

The current runtime builds only the engines needed by audited hosted titles:

`sky`, `queen`, `lure`, `adl`, `drascula`, `dreamweb`, `cge2`, and `cge`.

Each hosted ScummVM game launches directly through its configured target using the runtime URL hash, for example `runtime/scummvm/index.html#sky` or `#sfinx`.

#### Reviewed Emscripten hosting patches

The pinned upstream source is built with two small checked-in patches, both preserved in the generated runtime and source record:

- `patches/scummvm-emscripten-relative-data.patch` — keeps ScummVM's virtual `/data` filesystem but makes its browser HTTP root document-relative (`./data`) so the runtime works correctly when hosted under `/runtime/scummvm/` or another subpath.
- `patches/scummvm-emscripten-midi-permission.patch` — catches browser denial of optional Web MIDI/SysEx access and continues without MIDI instead of leaving an unhandled promise rejection.

The build workflow applies both with `git apply --check` before compilation. They are not opaque binary modifications.

### JSZip 3.10.1

The local ZIP-import workbench also has no functional CDN dependency. JSZip is materialized from pinned upstream source:

- version: `3.10.1`
- source commit: `0f2f1e4d0509514417db83fe5b86bde90e0ffe8d`
- runtime: `runtime/jszip/jszip.min.js`
- manifest: `runtime/jszip-build.json`
- provenance: `runtime/jszip/PROVENANCE.json`
- upstream license: `runtime/jszip/legal/LICENSE.markdown`

The top-level page loads this repository-local copy rather than jsDelivr.

## Audited game intake

A title does not become browser-ready because a download exists somewhere on the internet.

For a hosted game, the repository records:

- exact upstream package URL
- upstream rights/source record
- expected package hash
- rights basis
- runtime and target
- exact game-data path
- required detection files where useful
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

`runtime/scummvm-build.json` is the manifest for the shared ScummVM runtime and hosted game data.

`tools/materialize_scummvm_games.py`:

1. downloads each exact package
2. verifies its SHA-256
3. rejects unsafe ZIP paths
4. extracts into a dedicated game directory
5. applies the reviewed rights policy and requires package notices for redistributable freeware
6. validates the **exact** configured game directory rather than accepting arbitrary nested descendants
7. optionally requires declared detection files such as `vol.cat`, `vol.dat`, or `MYSTHOUS.DSK`
8. generates `scummvm.ini`
9. writes aggregate runtime/game provenance including direct payload files

This exact-path rule was added after Sfinx exposed a real nested-package edge case: its archive contains `sfinx-en-v1.1/sfinx-en-v1.1/`, so the correct configured payload path is explicitly recorded and tested instead of assuming the first extracted directory is launchable.

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
- `sfinx.md`
- `soltys.md`

A hosted package must have a defensible basis such as public-domain status, explicit freeware redistribution permission, an applicable open license, or direct rights-holder authorization. “Abandonware,” “not sold anymore,” or “available elsewhere” are not sufficient.

## Local restoration workbench

Games that cannot be redistributed can still be compatibility targets.

The browser workbench accepts:

- prepared `.jsdos` bundles
- ordinary DOS `.zip` archives

For ordinary ZIPs, the browser:

1. opens the archive locally with the pinned repository copy of JSZip
2. detects `.EXE`, `.COM`, and `.BAT` candidates
3. ranks likely game executables above setup/config/uninstall utilities
4. lets the user choose a target
5. creates a temporary js-dos configuration in memory
6. launches the result through the self-hosted js-dos runtime

The selected local game archive is not uploaded to a Kodaxa backend.

This generic path will not handle every DOS title. CD-ROM layouts, copy protection, unusual disk images, Windows installers, large installations, and specialized audio/input setups require dedicated profiles.

## Automated verification

### Static archive integrity

`.github/workflows/validate-site.yml` checks:

- JavaScript syntax
- Python intake unit tests
- unique and complete catalog records
- every hosted record points to a real artifact
- every hosted record has a rights record and provenance source
- every hosted ScummVM target exists in generated provenance
- all audited DOS bundles still match their manifests
- self-hosted js-dos 8.4.1 files still match recorded hashes
- local js-dos emulator path remains `runtime/jsdos/emulators/`
- the mutable js-dos `/latest` CDN has not been reintroduced
- ScummVM runtime/game provenance matches the pinned manifest
- exact ScummVM `relative_game_path`, required detection files, and direct payload records match
- generated ScummVM patches byte-match their checked-in reviewed versions
- repository-local JSZip 3.10.1 matches its manifest/provenance and jsDelivr has not been reintroduced

Synthetic unit tests reproduce the nested-game-directory failure mode and path-escape attempts so later packages cannot regress that intake logic.

### Browser execution smoke

`.github/workflows/browser-smoke.yml` uses Playwright/Chromium against a locally served checkout.

It currently proves, through the actual UI:

- the repository-local JSZip global loads
- Xargon launches through js-dos
- js-dos loads its worker/WASM files from `runtime/jsdos/emulators/`
- no mutable js-dos or JSZip functional CDN is contacted
- Beneath a Steel Sky launches through ScummVM
- ScummVM loads its WebAssembly binary and document-relative HTTP filesystem
- the real `sky.dsk` payload is requested
- no origin-root `/data/index.json` regression occurs
- Sfinx launches through the corrected nested payload path and requests its real `vol.cat` and `vol.dat`
- unexpected browser page/console errors fail the job

The headless browser has no speech-synthesis voices, so ScummVM's known optional “No voice is available” capability warning is excluded from fatal-console classification; actual page errors remain fatal.

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
runtime/jszip/                     pinned self-hosted JSZip 3.10.1
runtime/jszip-build.json            JSZip source pin
runtime/scummvm/                   generated patched ScummVM Web runtime + audited data
runtime/scummvm-build.json          ScummVM source/game pins

patches/                           reviewed ScummVM browser-hosting patches
docs/rights/                       per-title rights/provenance records
tools/                             materialization and verification tools
tests/                             static and browser-level regression tests
.github/workflows/                 build, materialization, and integrity gates
```

## Next technical layers

The strongest next additions are:

1. more individually audited freeware/public-domain titles
2. local user-data intake for commercial ScummVM games
3. tested Windows 9x/DOSBox-X profiles
4. save export/import portability
5. controller and touch profiles
6. richer game-specific restoration records and controls documentation
7. deployment-specific caching/content headers
8. visual polish using title-specific legal artwork only where its use is separately cleared

## Project rule

**Compatibility, provenance, and redistribution are separate questions.**

A game can work perfectly in a browser and still remain local-files-only. A freely redistributable game is not browser-ready until its exact source artifact, execution path, and rights basis are reproducible and auditable.
