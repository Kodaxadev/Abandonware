# Hi-Res Adventure #1: Mystery House — rights and provenance record

Status: **HOSTABLE / PUBLIC DOMAIN / AUDITED SOURCE**

This record applies to the Apple II public-domain package distributed by ScummVM. It does not claim public-domain status for unrelated Sierra titles, later anthologies, manuals, trademarks, promotional art, or modified third-party packages.

## Identity

- Title: Hi-Res Adventure #1: Mystery House
- Developer/publisher: On-Line Systems / Sierra On-Line
- Designers: Roberta Williams and Ken Williams
- Original release: 1980
- Platform used by this restoration: Apple II
- Browser interpreter: ScummVM
- ScummVM engine: ADL
- ScummVM launch target used by this archive: `hires1-apple2`

## Public-domain basis

ScummVM's 15 September 2016 project announcement states that Sierra On-Line released Mystery House into the public domain in 1987 for the company's seventh anniversary. The same announcement directs users to ScummVM's free download of the game.

https://www.scummvm.org/news/20160915/

The current ScummVM game-download catalog continues to identify the downloadable Apple II package as the **public domain version**.

https://www.scummvm.org/games/

## Exact package used by Abandonware

- URL: `https://downloads.scummvm.org/frs/extras/Mystery%20House/MYSTHOUS.zip`
- Published SHA-256: `ada412228a149394489b28c6c7f9ebab0722b52e04732fd0aa22949673cfa3a0`
- Current ScummVM label: `Hi-Res Adventure #1: Mystery House - public domain version (Apple II)`

The hash above is published by ScummVM's current game-download catalog.

## Independent technical corroboration

SerenityOS's current `mysthous` port independently pins the same ScummVM archive and the same SHA-256. Its package script installs `MYSTHOUS.DSK` and launches ScummVM with the `hires1-apple2` target.

https://github.com/SerenityOS/serenity/blob/master/Ports/mysthous/package.sh

This is useful technical corroboration for both the exact package identity and the expected ScummVM launch target; the public-domain basis itself comes from ScummVM's historical Sierra release record above.

## Notice policy

Unlike the freeware packages already in this archive, a public-domain Apple II disk image does not require an embedded redistribution license to create permission. The ScummVM intake therefore records this title with:

- `rights_basis: public_domain`
- an exact current upstream package hash
- this checked-in public-domain evidence record
- any package notices that happen to exist, without requiring one as a condition of public-domain status

The build still fails closed on source hash, unsafe archive paths, missing game data, runtime-build failure, or provenance mismatch.

## Scope warning

Mystery House being public domain does **not** imply that King's Quest, other Sierra Hi-Res Adventures, Sierra logos, collection artwork, or other Sierra game data are public domain. Those remain separate rights questions.
