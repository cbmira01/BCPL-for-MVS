# TA.2 — Guarded one-shot selective IEBCOPY staging preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** Guarded runner implemented; write approval and MVS staging still pending.

## Owner-reported MVS readiness

The owner reported a successful `ta2-stage-readiness --live` on GitHub
`main` `31050fd6ce95820e08511dc1e222c44f58bb26e5`:

- 18/18 PDS staging targets and 127 selected members;
- proposed TSO002 with **16,045 IEHLIST-reported empty tracks**;
- fresh source/catalog/VTOC MVS inquiries PASS;
- **645 primary tracks + 65 secondary reserve = 710** proposed tracks;
- retained private evidence:
  `workarea/ta2-stage-readiness/20261119T210718Z-18180`.

The 18 exact proposed `SPACE=(TRK,(primary,secondary,directory))` triples
are recorded as structured **PROPOSED_ONLY_NOT_APPROVED** data in
`ta2-stage-space-proposal-20261119.json`, bound to the owner's exact
saved MVS readiness and allocation evidence. The proposal is not a
release dataset/member manifest. The TA.0 inventory remains authoritative
for all 127 selected members.

**TSO002 has not been approved as a staging destination, and the per-PDS
allocation triples have not been approved for writes.** The MVS free-track
total alone does not establish free-extent contiguity or guaranteed 18
successful allocations.

## Implementation

`scripts/ta2-stage-once --readiness-evidence <saved-run>` defaults to
independent **saved-evidence replay only**. With `--live` it repeats
read-only source `dspal stat`, TSO LISTDS absence for all 18 targets,
and IEHLIST VTOC for TSO002. It refuses changed source attributes,
selected members, exact allocation amounts, saved/current VTOC inventory
or free tracks, or any catalog/uncataloged target collision.

For a future separately approved `--run`, it requires an additional,
explicit **Git-tracked on `main`**
`packaging/distribution/create-tape/ta2-stage-write-approval.json`.
That file is **deliberately absent** from the repository at this stage.
The runner refuses the write mode until such an approved file is separately
committed, matches the full staging proposal SHA-256, the pinned readiness
receipt SHA-256, and authorizes precisely the one TSO002/18-PDS operation.
It additionally requires an interactive confirmation, a second fresh MVS
preflight, and exclusive creation of
`workarea/ta2-stage-operations/TA2STG-TSO002-attempt.json`
**before** any possible JES submission. Never delete this marker or retry
a partly successful staging. Earlier `DISP=(NEW,CATLG,DELETE)` outputs
may remain cataloged even if a later IEBCOPY step fails.

On a future authorized attempt the runner derives 18 IEBCOPY steps and
127 `SELECT MEMBER` controls from the canonical source manifest, attaches
an authenticated MVS job card, and requires all 18 IEBCOPY RC=0000 steps
and distinct IEF142I confirmations. Full JES and private evidence stay in
ignored `workarea/`; never persist an authenticated password-bearing deck.
RC=0000 is **not** final acceptance of the staged payload: independently
verify exact 127-member sets without extras, DCB and partitioned-library
directory attributes, the `MR10_LOAD` PO/U/0/6144 case, source-to-staged
record/binary fidelity, and executable-use where applicable.

All generated files from this workflow are inside repository-root
`workarea/` or tracked `packaging/`. No tape image, `BCnnnn` production
VOLSER, candidate registry entry, or publication operation is included.

## Assistant offline checks

**35/35 focused synthetic tests passed** under the assistant's isolated
repository-root workspace. Coverage includes exact 18 proposed allocations,
checksum and path integrity, forbidden symlinks, source/job receipt mismatch,
owner approval absent or forged, Git-main binding, budget drift, raw JCL
counts/card widths, one-shot attempt marker, all 18 MVS step RCs, IEF142I
completeness, ABEND refusal and simulated live VTOC drift. Python syntax
checks also pass. The actual private MVS evidence has not been imported
into the assistant workspace and the live one-shot runner has **not** been
executed on MVS; no acceptance of staging execution is claimed.

**Next owner gate:** explicitly approve or revise TSO002 and all 18
`SPACE` triples. A separate owner authorization is required before any
state-changing IEBCOPY job. TA.2 remains IN PROGRESS.
