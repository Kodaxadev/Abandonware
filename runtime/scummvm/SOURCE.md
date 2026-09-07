# Corresponding source and build record

This browser runtime is built from ScummVM 2026.3.0 at pinned commit:

`fed42f2068dcafc6aafa1c28c77e4c88def74b66`

Corresponding upstream source:

https://github.com/scummvm/scummvm/tree/fed42f2068dcafc6aafa1c28c77e4c88def74b66

Abandonware browser-hosting patches:

- `patches/scummvm-emscripten-relative-data.patch` changes only the HTTP URL backing the virtual `/data` filesystem from origin-absolute `/data` to document-relative `./data`. This keeps ScummVM virtual paths unchanged while allowing static hosting below an origin path.
- `patches/scummvm-emscripten-midi-permission.patch` handles a browser rejection of optional Web MIDI/SysEx access and continues without MIDI instead of leaving an unhandled promise rejection.

Enabled game engines:

- `sky`
- `queen`
- `lure`
- `adl`
- `drascula`
- `dreamweb`
- `cge2`
- `cge`
- `parallaction`

Audited game-data packages:

- Beneath a Steel Sky — target `sky` — rights: `docs/rights/beneath-a-steel-sky.md`
- Flight of the Amazon Queen — target `queen` — rights: `docs/rights/flight-of-the-amazon-queen.md`
- Lure of the Temptress — target `lure` — rights: `docs/rights/lure-of-the-temptress.md`
- Hi-Res Adventure #1: Mystery House — target `hires1-apple2` — rights: `docs/rights/mystery-house.md`
- Drascula: The Vampire Strikes Back — target `drascula` — rights: `docs/rights/drascula.md`
- DreamWeb — target `dreamweb` — rights: `docs/rights/dreamweb.md`
- Sfinx — target `sfinx` — rights: `docs/rights/sfinx.md`
- Sołtys — target `soltys` — rights: `docs/rights/soltys.md`
- Nippon Safes, Inc. — target `nippon` — rights: `docs/rights/nippon-safes.md`

Build method:

1. Check out the pinned ScummVM commit.
2. Apply both checked-in Emscripten browser-hosting patches.
3. Run `./dists/emscripten/build.sh build --enable-release --disable-all-engines --enable-engine=sky --enable-engine=queen --enable-engine=lure --enable-engine=adl --enable-engine=drascula --enable-engine=dreamweb --enable-engine=cge2 --enable-engine=cge --enable-engine=parallaction`.
4. SHA-256 verify and materialize each audited game-data package.

Game-data licenses are separate from ScummVM GPL licensing.
