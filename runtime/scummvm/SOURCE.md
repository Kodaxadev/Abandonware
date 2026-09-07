# Corresponding source and build record

This browser runtime is an unmodified build of ScummVM 2026.3.0 at commit:

`fed42f2068dcafc6aafa1c28c77e4c88def74b66`

Corresponding source:

https://github.com/scummvm/scummvm/tree/fed42f2068dcafc6aafa1c28c77e4c88def74b66

Enabled game engines:

- `sky`
- `queen`
- `lure`

Audited freeware data packages:

- Beneath a Steel Sky — target `sky` — rights: `docs/rights/beneath-a-steel-sky.md`
- Flight of the Amazon Queen — target `queen` — rights: `docs/rights/flight-of-the-amazon-queen.md`
- Lure of the Temptress — target `lure` — rights: `docs/rights/lure-of-the-temptress.md`

Build method:

`./dists/emscripten/build.sh build --enable-release --disable-all-engines --enable-engine=sky --enable-engine=queen --enable-engine=lure`

Every game package is downloaded from its manifest URL and SHA-256 verified before extraction. Game-data licenses are separate from ScummVM GPL licensing.
