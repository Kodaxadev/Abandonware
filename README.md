# ABANDONWARE

A preservation-first browser arcade for keeping classic PC games playable.

The project name describes the cultural problem, **not a legal status**. Old or unavailable software is not automatically free to copy or redistribute. The site therefore treats emulator compatibility and redistribution rights as two independent gates.

## Current milestone

**Xargon 3.0 is the first audited browser-ready title.**

The registered three-episode DOS release was made freeware by author Allen W. Pilgrim in 2008. Abandonware builds its browser artifact from a hash-pinned package archived by FreeDOS rather than accepting an arbitrary download with the right filename.

The repository now contains:

- a responsive preservation-terminal website and restoration catalog
- a browser-native DOS runtime powered by **js-dos v8 / DOSBox WebAssembly**
- one-click hosted execution for audited redistributable games
- a machine-readable game catalog in `data/games.js`
- per-game audited source manifests in `games/manifests/`
- rights/provenance records in `docs/rights/`
- deterministic materialization tooling in `tools/build_audited_game.py`
- a GitHub Actions gate that verifies upstream source identity before producing hosted `.jsdos` artifacts
- local `.jsdos` bundle loading
- local ordinary `.zip` loading for DOS games
- client-side detection and ranking of `.EXE`, `.COM`, and `.BAT` boot targets
- client-side generation of `.jsdos/dosbox.conf` for ordinary ZIPs
- local filesystem saves through js-dos
- a rights confirmation gate before local game execution
- catalog states distinguishing browser-ready, local-files-only, and planned execution engines

## Run locally

This is a static site, but browser emulator assets require HTTP(S), not `file://`.

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

No front-end build step is required.

## Audited hosted-game pipeline

Hosted games do not enter the archive by dropping random binaries into `games/`.

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
3. verifies its expected SHA-1 package identity
4. computes SHA-256 for additional artifact provenance
5. locates the declared launch target inside the package
6. adds the js-dos configuration
7. embeds `.jsdos/provenance.json` inside the resulting bundle
8. writes the browser artifact only if every gate passes

`.github/workflows/materialize-audited-games.yml` runs this process on GitHub infrastructure and commits changed generated bundles back to the repository. A changed upstream file therefore fails closed instead of silently becoming a new game build.

### Xargon provenance

See [`docs/rights/xargon.md`](docs/rights/xargon.md).

The first source package is pinned to the FreeDOS 1.1 archive record for Xargon 3.0. The materialization workflow has successfully produced `games/xargon.jsdos` from that audited source.

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
- runtime/engine
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
- exact provenance of every hosted artifact

## Rights states

Game data should only be hosted when there is a documented basis for redistribution, such as:

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

### Layer 2 — ScummVM / planned

For supported adventure and RPG titles. Game data remains user-supplied unless redistribution rights are documented.

### Layer 3 — Windows 9x / planned

`js-dos` supports DOSBox-X / Windows 95/98 execution paths, but the archive will not mark individual titles browser-ready until reproducible profiles and practical large-file handling are verified.

### Later candidates

Browser-native source ports, additional open emulator cores, controller profiles, install-media workflows, preservation metadata ingestion, and richer game-specific presentation.

## Dependency policy

Current browser dependencies are loaded from their public distribution paths:

- js-dos v8
- JSZip 3.10.1
- Google Fonts for IBM Plex Mono and Space Grotesk

Before a production preservation release, dependencies should be pinned and self-hosted where their licenses permit it so a CDN change cannot break the archive.

## Project rule

**Compatibility, provenance, and redistribution are separate questions.**

A game can be technically perfect in the browser and still remain local-files-only. A freely redistributable game is not browser-ready until its runtime profile and exact source artifact are reproducible.
