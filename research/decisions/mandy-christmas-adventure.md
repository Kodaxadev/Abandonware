# Candidate decision — Mandy Christmas Adventure

Decision: **CONDITIONAL PASS — REDISTRIBUTION GRANTED, WEBSITE REPORTING CONDITION UNRESOLVED**

## Exact package reviewed

- source: `https://downloads.scummvm.org/frs/extras/SLUDGE/mandy-1.2.zip`
- SHA-256: `91627f0f43791cc2aa9b356d2e4075ea49f720263c09e668bb2b65c9648e2c75`
- observed archive size: 4,431,839 bytes
- ScummVM candidate: engine `sludge`, target `mandy`
- package notices: `mandy-1.2/License.txt` and `mandy-1.2/LicenseSK.txt`

## Rights basis found in the package

The English license identifies the 2003 authors as Rudolf Šlavka and Marián Mifkovič and explicitly says the game is freeware and may be copied and shared free of charge. It also imposes a non-profit restriction.

For website publication, the license additionally requires the publisher to provide the authors with the number of downloads. A separate condition applies to magazine CD/DVD distribution.

This is materially stronger than a generic freeware label: the exact package itself contains an affirmative copying/sharing grant and expressly contemplates website publication.

## Why this is not production-ready yet

Abandonware does not currently have a deployment-bound, first-party aggregate download/launch counter for this title. The only connected Supabase project belongs to an unrelated project and must not be reused implicitly. No connected Vercel team/project exists for this repository.

Publishing Mandy before implementing a reliable count/report mechanism would ignore an express condition in the shipped license.

The production site also must remain non-profit with respect to this game. If the site later gains ads, paid access, sponsorship tied to game access, or another profit-generating model, Mandy's license must be reviewed again before continued hosting.

## Current status

- exact package provenance: **verified**
- package safety: **verified**
- affirmative copy/share grant: **yes**
- website publication contemplated: **yes**
- profit from distribution permitted: **no**
- website download-count reporting condition: **not yet operationally satisfied**
- technical ScummVM target: **known** (`sludge:mandy`)
- production manifest: **do not add yet**
- public catalog: **do not add yet**

## Promotion gate

Mandy can move into the production ScummVM manifest only after all of the following are true:

1. a first-party aggregate counter records Mandy launches/downloads without storing unnecessary user-identifying data;
2. the counter has a durable admin/report path so the download number can actually be supplied to the authors;
3. the deployment remains non-profit for this distribution;
4. the exact package path/detection files pass the normal ScummVM intake gate;
5. the built runtime and actual Mandy payload pass Chromium smoke testing;
6. the rights record shipped with the site preserves these conditions rather than reducing them to the word “freeware.”

Until then this is a conditional pass, not approval to publish.
