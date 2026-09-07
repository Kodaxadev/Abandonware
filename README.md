# ABANDONWARE

A preservation-first browser arcade for keeping classic PC games playable.

The project name describes the cultural problem, **not a legal status**. Old or unavailable software is not automatically free to copy or redistribute. The site treats emulator compatibility, source provenance, and redistribution rights as separate gates.

## Current milestone

The archive now has **three audited browser-ready games across two execution engines**:

| Game | Runtime | Rights basis | Source gate |
| --- | --- | --- | --- |
| Xargon 3.0 | js-dos / DOSBox | Allen W. Pilgrim 2008 freeware grant | pinned FreeDOS package size + SHA-1, embedded SHA-256 provenance |
| Kiloblaster 2.0a | js-dos / DOSBox | Allen W. Pilgrim 2008 freeware grant | pinned FreeDOS package size + SHA-1, embedded SHA-256 provenance |
| Beneath a Steel Sky | ScummVM Web 2026.3.0 | Revolution Software freeware redistribution license | official ScummVM-hosted floppy package + published SHA-256 |

Commercial and uncertain titles remain local-files-only even when technically compatible.

The repository now contains:

- a responsive preservation-terminal website and searchable restoration catalog
- one-click hosted execution for audited redistributable games
- **js-dos v8 / DOSBox WebAssembly** for DOS titles
- a source-pinned **ScummVM 2026.3.0 WebAssembly** runtime for adventure-game preservation
- a machine-readable game catalog in `data/games.js`
- per-game audited DOS source manifests in `games/manifests/`
- runtime build manifests in `runtime/`
- rights/provenance records in `docs/rights/`
- deterministic DOS materialization tooling in `tools/build_audited_game.py`
- bundle verification in `tools/verify_audited_bundle.py`
- GitHub Actions gates for reproducibility, rights/source provenance, and catalog/artifact integrity
- local `.jsdos` bundle loading
- local ordinary `.zip` loading for DOS games
- client-side detection and ranking of `.EXE`, `.COM`, and `.BAT` boot targets
- client-side generation of `.jsdos/dosbox.conf` for ordinary ZIPs
- local filesystem saves through js-dos
- a rights confirmation gate before local game execution
- catalog states distinguishing browser-ready, local-files-only, and planned execution paths

## Run locally

This is a static site, but the WebAssembly runtimes require HTTP(S), not `file://`.

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

No front-end build step is required to serve an already-materialized checkout.

## Audited DOS pipeline

Hosted DOS games do not enter the archive by dropping random binaries into `games/`.

Each title gets a manifest such as `games/manifests/xargon.json` containing:

- upstream package URL
- upstream record URL
- expected byte size
- expected published package hash
- copying-policy name
- launch target
- DOSBox profile
- rights-record path
- generated artifact path

`tools/build_audited_game.py` then:

1. downloads the pinned upstream package
2. verifies its expected size
3. verifies its expected published SHA-1 package identity
4. computes SHA-256 for additional artifact provenance
5. locates the declared launch target inside the package
6. adds the js-dos configuration
7. embeds `.jsdos/provenance.json` inside the resulting bundle
8. writes generated ZIP metadata with fixed timestamps
9. produces the browser artifact only if every gate passes

`tools/verify_audited_bundle.py` checks archive safety, generated metadata, provenance, launch-target presence, DOSBox configuration, and deterministic timestamps.

`.github/workflows/materialize-audited-games.yml` builds every audited DOS title twice and compares final SHA-256 hashes. If identical source/manifests produce different bytes, CI fails rather than committing the artifact.

### DOS rights records

- [`docs/rights/xargon.md`](docs/rights/xargon.md)
- [`docs/rights/kiloblaster.md`](docs/rights/kiloblaster.md)

## ScummVM Web pipeline

Beneath a Steel Sky establishes the second execution-engine path.

`runtime/scummvm-build.json` pins:

- ScummVM version `2026.3.0`
- exact upstream commit `fed42f2068dcafc6aafa1c28c77e4c88def74b66`
- Emscripten SDK `4.0.10`
- only the ScummVM `sky` engine
- the exact official freeware game-data URL
- the published SHA-256 for the Floppy 1.3 archive
- the corresponding rights record

`.github/workflows/build-scummvm-sky.yml` then:

1. checks out the exact ScummVM source commit
2. builds the official Emscripten/WebAssembly target with only `sky` enabled
3. downloads the official ScummVM-hosted Beneath a Steel Sky freeware package
4. verifies its published SHA-256
5. refuses the package if its readme/license notice is missing
6. generates ScummVM HTTP filesystem indexes
7. writes the pinned Steel Sky launcher configuration
8. preserves ScummVM GPL/COPYRIGHT materials and a corresponding-source record
9. writes runtime/game provenance
10. rejects generated files above the repository safety threshold
11. materializes the verified static runtime into `runtime/scummvm/`

Rights record: [`docs/rights/beneath-a-steel-sky.md`](docs/rights/beneath-a-steel-sky.md).

The generated runtime carries `runtime/scummvm/PROVENANCE.json`, `SOURCE.md`, ScummVM legal materials, the WebAssembly runtime, and the audited freeware data filesystem.

## Archive validation

`.github/workflows/validate-site.yml` is the repository-wide integrity gate. It checks:

- JavaScript syntax
- unique/complete game records
- every browser-ready title points to a real repository artifact
- every hosted title has a rights record and source record
- all audited DOS bundles still match their manifests
- ScummVM runtime provenance still matches its pinned build manifest
- required ScummVM source/license/runtime files remain present

A UI edit therefore cannot silently point a Play button at a missing or unaudited file without CI noticing.

## Local restoration workbench

### Prepared `.jsdos`

A `.jsdos` file is a ZIP-based bundle containing the game and a `.jsdos/dosbox.conf` file. The workbench creates an object URL for the user's local file and gives that URL to js-dos. The project does not upload the bundle to a Kodaxa backend.

### Ordinary DOS `.zip`

1. JSZip opens the archive in the browser.
2. The workbench finds `.EXE`, `.COM`, and `.BAT` files.
3. Obvious setup/config/uninstall utilities are ranked lower and likely game launchers are ranked higher.
4. The user chooses the boot target.
5. The workbench writes a temporary `.jsdos/dosbox.conf` into the in-memory archive.
6. A temporary local bundle is created and launched with js-dos.
7. The object URL and emulator resources are disposed when the session stops.

This generic path will not work for every DOS title. CD-ROM games, unusual disk images, copy protection, special sound configurations, Windows installers, and large installations need per-title profiles.

## Restoration record model

A title should eventually have:

- original platform and release metadata
- runtime/engine and exact version
- required files
- boot target and configuration
- keyboard/mouse/controller mapping
- audio configuration
- scaling/aspect-ratio behavior
- save/load behavior
- known browser compatibility
- test date and test browser
- rights status
- sources supporting that rights status
- whether game data may be hosted or must remain local-only
- exact provenance/fingerprints of every hosted artifact

## Rights states

Game data is only hosted when there is a documented basis for redistribution, such as:

- public-domain dedication
- an open-source/open-content license that covers the required game data
- an explicit freeware redistribution grant
- direct permission from the rights holder
- another reviewed authorization that actually permits public distribution

If that basis is missing or uncertain, the title remains **LOCAL FILES** even when emulator compatibility is perfect.

“Not sold anymore,” “company closed,” “old,” “available on an abandonware site,” or “nobody has complained” are not sufficient rights evidence.

## Runtime roadmap

### Layer 1 — DOS / active

`js-dos v8` with DOSBox. Generic local ZIP import and audited hosted-game execution are active.

### Layer 2 — ScummVM / active

A pinned ScummVM WebAssembly runtime is active with Beneath a Steel Sky as the first audited title. Additional freeware/openly redistributable ScummVM games can reuse this execution class after individual rights/source review. Commercial ScummVM games can later receive local-data profiles without hosting their game data.

### Layer 3 — Windows 9x / planned

`js-dos` supports DOSBox-X / Windows 95/98 execution paths, but the archive will not mark individual titles browser-ready until reproducible profiles and practical large-file handling are verified.

### Later candidates

Browser-native source ports, additional open emulator cores, controller profiles, install-media workflows, preservation metadata ingestion, richer game-specific presentation, save portability, and compatibility telemetry that does not collect game data.

## Dependency policy

Current top-level browser dependencies are loaded from their public distribution paths:

- js-dos v8
- JSZip 3.10.1
- Google Fonts for IBM Plex Mono and Space Grotesk

The ScummVM runtime is self-materialized from pinned source. A later hardening pass should pin and self-host the remaining top-level dependencies where their licenses permit it so an upstream CDN change cannot break the archive.

## Project rule

**Compatibility, provenance, and redistribution are separate questions.**

A game can be technically perfect in the browser and still remain local-files-only. A freely redistributable game is not browser-ready until its runtime profile and exact source artifact are reproducible and auditable.
