# Candidate decision — Out Of Order

Decision: **HOLD — THIRD-PARTY REHOSTING RIGHT NOT ESTABLISHED**

This decision deliberately does not equate “freeware” with a redistribution grant.

## What passed

The exact ScummVM-hosted package was audited successfully:

- source: `https://downloads.scummvm.org/frs/extras/SLUDGE/ooo.zip`
- SHA-256: `b787789bbf31a9786f99a2e5fe67a1d4c63706925246b94679e8fc1b9791abb1`
- package size observed by CI: 8,781,072 bytes
- two safe archive members under the `ooo` directory
- pinned ScummVM runtime candidate: engine `sludge`, target `outoforder`

The game is widely described as freeware, and Debian packages it in the `non-free` archive with a `Custom, GPL-3+` license classification.

## What blocks hosting

The exact ScummVM ZIP contains **no readme, license, copyright, copying, or other legal notice**. Package provenance therefore cannot establish a grant allowing Kodaxa to mirror the game data.

Debian's packaging record identifies a custom license for the game data. A current independent license-review index points specifically to Debian's `out-of-order_1.0-3_copyright` record and characterizes the author's terms as restrictive, including restrictions on reverse engineering, selling, and separating the package. That is evidence that the game is not simply unrestricted freeware, but it is not a substitute for reviewing the exact author terms ourselves.

Because the authoritative Debian metadata endpoint is presently not returning the copyright text through our research tooling, this record does **not** claim that redistribution itself is forbidden. It only records the narrower fact we can support: an explicit third-party rehosting grant for this ScummVM payload has not been established.

## Current status

- technical candidate: **yes**
- exact ScummVM package provenance: **verified**
- package safety: **verified**
- freeware classification: **supported**
- package-level redistribution notice: **absent**
- external license classification: **custom / non-free**
- defensible Kodaxa mirror right: **not established**
- production manifest: **prohibited while this decision remains HOLD**
- public catalog: **do not add**

## Reconsideration trigger

This decision can be revisited only after obtaining the exact applicable author/license terms or direct rights-holder permission and confirming that they permit redistribution of the form we would host. In particular, we must determine whether any grant requires an original intact package and whether the ScummVM `ooo.zip` repack satisfies those conditions.

A freeware label, Debian package availability, or ScummVM hosting the payload is not by itself sufficient to promote the game.
