# Candidate decision — The Griffon Legend

Decision: **HOLD — EXPLICIT PORT LICENSE FOUND, BUT ORIGINAL-ASSET LICENSOR AUTHORITY AND NC/ND DEPLOYMENT BOUNDARY ARE UNRESOLVED**

This decision supersedes the earlier, narrower statement that no explicit redistribution grant existed anywhere in the surviving project ecosystem. New evidence from the maintained C port is materially stronger, but it still does not close the production rights chain under Abandonware's fail-closed policy.

## Exact game package

The exact ScummVM-hosted package was audited successfully:

- source: `https://downloads.scummvm.org/frs/extras/Griffon%20Legend/griffon-1.0.zip`
- SHA-256: `0aad5fb10f51afb5c121cf04cc86539a6f0d89db85809f9e1767dfdc8d3191a4`
- package size observed by CI: `9,552,316` bytes
- archive members: `344`
- package notice: `readme.txt`

ScummVM describes The Griffon Legend as freeware and distributes the exact package. Surviving original-project pages identify Daniel "Syn9" Kennedy as the author and continue to present the title as one of his full-length games.

## Stronger license evidence discovered later

The maintained C port at:

`https://github.com/dmitrysmagin/griffon_legend`

contains both the original FreeBASIC source and a later C port. Its checked-in `LICENSE` explicitly states:

- source code: **GPL-2.0**;
- all non-source-code assets — graphics, music, and binary data: **Creative Commons Attribution-NonCommercial-NoDerivs 3.0** (`CC-BY-NC-ND-3.0`).

The port `README` identifies the original authorship split as:

- Programming / graphics: Daniel "Syn9" Kennedy;
- Music / sound effects: David Turner;
- C port: Dmitry Smagin.

The asset-license statement first appears in Dmitry Smagin's 2013-10-10 commit `8c1207b3dd65e9e14f318a3ceb4deef7057fcc32` (`Add LICENSE and README`). Abandonware preserves this as important rights evidence rather than continuing to characterize the ecosystem as having no explicit license at all.

## What this evidence does and does not prove

The maintained-port license is strong evidence that the port community understood the original asset set to be distributable under CC-BY-NC-ND-3.0. It is substantially stronger than a generic freeware listing.

It does **not**, on the evidence currently preserved, establish that Dmitry Smagin was authorized by Daniel Kennedy and David Turner to place their original graphics/music/sound/binary data under that license. The repo itself credits those works to their respective original authors rather than to the port maintainer.

The current Syn9 site identifies The Griffon Legend as Daniel Kennedy's project, but its restored project links do not currently provide an original-author license statement that closes this authority chain.

Abandonware therefore does not treat a downstream maintainer's asset-license declaration as conclusive proof of relicensing authority without corroboration from the rights holders or contemporaneous authorized release evidence.

## NC/ND production constraint

Even if the authority chain is later established, `CC-BY-NC-ND-3.0` is not equivalent to the archive's normal unrestricted/open-content lane:

- **NC:** use is limited to noncommercial purposes;
- **ND:** redistribution of adapted/derivative asset material is restricted.

A compliant exact-package mirror may still be possible under those terms, but Abandonware does not currently assume a durable site-wide noncommercial deployment invariant, and it must not modify covered assets while relying on a NoDerivatives grant.

That means production would still require an explicit deployment rule documenting why the hosted artifact is noncommercial and unmodified with respect to the CC-covered assets.

## Current status

- technical candidate: **yes**
- exact ScummVM package provenance: **verified**
- freeware classification: **supported**
- explicit downstream asset-license declaration: **found — CC-BY-NC-ND-3.0**
- source-code license in maintained port: **GPL-2.0**
- original-asset licensor authority for the CC grant: **not established**
- durable noncommercial deployment boundary: **not established**
- no-derivatives compliance boundary: **not yet modeled for production**
- production manifest: **do not add**
- public catalog: **do not add**
- non-publishing source/compatibility work: **permitted**

## Reconsideration triggers

This decision can return to production review if one or more of the following are preserved:

1. Daniel Kennedy and David Turner, or another legitimate rights holder, confirm the CC-BY-NC-ND-3.0 asset license;
2. contemporaneous original-project evidence shows that Dmitry Smagin's asset-license statement was authorized;
3. the original rights holders provide a separate redistribution grant covering the exact game assets;
4. Abandonware intentionally adopts and enforces a noncommercial, unmodified-asset deployment boundary compatible with the proven license grant.

Until both **licensor authority** and **deployment compatibility** are established, The Griffon Legend remains HOLD.
