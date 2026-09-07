# ABANDONWARE

A preservation-first browser arcade for keeping classic PC games playable.

The project name describes the cultural problem, **not a legal status**. Old or unavailable software is not automatically free to copy or redistribute. The site therefore separates the emulator/runtime from copyrighted game data.

## What exists now

- A responsive preservation-terminal website and restoration catalog.
- A browser-native DOS workbench powered by **js-dos v8 / DOSBox WebAssembly**.
- Local `.jsdos` bundle loading.
- Local ordinary `.zip` loading for DOS games.
- Client-side detection and ranking of `.EXE`, `.COM`, and `.BAT` boot targets.
- Client-side generation of the required `.jsdos/dosbox.conf` for ordinary ZIPs.
- Local filesystem saves through js-dos.
- No hosted commercial game binaries.
- A rights confirmation gate before local game execution.
- Catalog states that distinguish local-file support from planned execution engines.

## Run locally

This is a static site, but browser emulator assets require HTTP(S), not `file://`.

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

No build step is required.

## How the local workbench works

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
- required user files
- boot target and configuration
- keyboard/mouse/controller mapping
- audio configuration
- scaling/aspect-ratio behavior
- save/load behavior
- known browser compatibility
- test date and test browser
- rights status
- source(s) supporting that rights status
- whether game data may be hosted or must remain local-only

## Rights states

Game data should only be hosted when there is a documented basis for redistribution, such as:

- public-domain dedication
- an open-source/open-content license that covers the required game data
- an explicit freeware redistribution grant
- direct permission from the rights holder
- another reviewed authorization that actually permits public distribution

If that basis is missing or uncertain, the title remains **LOCAL FILES** even when the emulator compatibility is perfect.

“Not sold anymore,” “company closed,” “old,” “available on an abandonware site,” or “nobody has complained” are not sufficient rights evidence.

## Runtime roadmap

### Layer 1 — DOS / active

`js-dos v8` with DOSBox. Generic local ZIP import is active now. Next step is tested per-title profiles.

### Layer 2 — ScummVM / planned

For supported adventure and RPG titles. Game data remains user-supplied unless redistribution rights are documented.

### Layer 3 — Windows 9x / planned

`js-dos` supports DOSBox-X / Windows 95/98 execution paths, but the site will not claim support until reproducible profiles and practical large-file handling are implemented.

### Later candidates

Only after the first three layers are stable: browser-native source ports, additional open emulator cores, controller profiles, install-media workflows, and preservation metadata ingestion.

## Dependency policy

Current browser dependencies are loaded from their official/current distribution paths:

- js-dos v8
- JSZip 3.10.1
- Google Fonts for IBM Plex Mono and Space Grotesk

Before a production preservation release, dependencies should be pinned and self-hosted where their licenses permit it so a CDN change cannot break the archive.

## Project rule

**Compatibility and redistribution are two independent questions.**

A game can be technically perfect in the browser and still remain local-files-only. Conversely, a freely redistributable game is not browser-ready until its runtime profile is actually tested.
