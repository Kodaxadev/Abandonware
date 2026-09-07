# Sfinx — rights and provenance record

Status: **approved for audited hosted intake, pending package/build verification**

## Rights basis

ScummVM credits Janusz Wiśniewski and Miroslaw Liminowicz of Laboratorium Komputerowe Avalon with providing the full source code for **Sołtys and Sfinx and letting ScummVM redistribute the games**.

ScummVM also announced in September 2014 that, thanks to the original developers, Sfinx had become freeware and could be downloaded from the ScummVM site.

This is stronger evidence than an abandonware listing: it identifies the original developer relationship and an explicit redistribution permission relied on by the preservation project that hosts the package.

Sources:

- https://docs.scummvm.org/en/v2.9.0/help/credits.html
- https://www.scummvm.org/news/20140918/
- https://www.scummvm.org/games/

## Audited package

Edition: **Sfinx — English v1.1**

Source package:

`https://downloads.scummvm.org/frs/extras/Sfinx/sfinx-en-v1.1.zip`

Current ScummVM-published SHA-256:

`f516b30a046526f78cbc923d8f907d267ab964ccd9b770afc72350e8d467ec4d`

The package must still pass Abandonware's normal intake checks before catalog promotion: exact hash, safe extraction, package notice preservation, configured data path, ScummVM engine build, runtime provenance, and repository integrity validation.

## Runtime target

- ScummVM engine: `cge2`
- ScummVM game target: `sfinx`
- Original platform: DOS

## Decision

**Hostable only through the audited package pipeline.** This record does not authorize substituting other Sfinx archives, modified packages, translations, or releases with different hashes without a new review.
