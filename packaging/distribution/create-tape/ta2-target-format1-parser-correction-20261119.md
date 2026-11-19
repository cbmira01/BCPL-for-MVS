# TA.2 — Target review FORMAT-1 DSCB field correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** Parser correction prepared and locally tested; actual saved MVS report still requires successful review.

## Actual owner-reported refusal

From GitHub `main` `40af1dfd3c3e06a00cd1d1b79d727139fa1672b0`,
the owner invoked the existing read-only target reviewer twice against
`workarea/ta2-target-preflight/20261119T170234Z-17334`.
Both attempts terminated with:

```text
TA.2 TARGET REVIEW REFUSED: VTOC has no recognizable FORMAT-1 dataset rows; raw review needed
```

The exception is raised by `inspect_vtoc()` during **saved evidence**
review, before the optional fresh MVS inquiry. The earlier
`ta2-target-preflight` had reported 18/18 catalog-absence observations
and a saved IEHLIST VTOC. These refusals do not establish an MVS
failure, a catalog collision, or free DASD space. The private saved
IEHLIST report is not directly accessible in the assistant workspace.

## Grounded parser defect

The initial `ta2-target-review` `ENTRY` regular expression
mistakenly expected the MVS FORMAT-1 dataset-name field to be followed
*immediately* by `SER NO` and `SEQNO`:

```text
SYS1.PARMLIB                 TSO002  1  2026.323
```

But the repository's established `tools/datasets/dspal-space.py`
`_vtoc_entry` parser explicitly recognizes the intervening DSCB
format type **1** in an actual MVS IEHLIST VTOC listing:

```text
SYS1.PARMLIB              1  TSO002  1  00001
```

The new reviewer omitted that type field, and its synthetic VTOC
fixture repeated the omission. This is a source-supported cause of a
false refusal; until the saved raw MVS evidence passes the corrected
parser, it remains a **diagnosis**, not a claim of confirmed byte-level
inspection of the owner's report.

## Correction and retained safety conditions

The reviewer now accepts the established FORMAT-1 DSCB row
(`DSN 1 VOLSER SEQNO ...`) and retains compatibility with the
earlier synthetic fixture without the explicit type. It does **not**
classify a different DSCB type as a FORMAT-1 dataset row.

All existing fail-closed checks are preserved: exact saved
`SHA256SUMS`, source/capacity/stage ancestry, original JES report
and catalog checks, matching volume header/row identities, duplicate
DSN rejection, selected staging-name absence, IEHLIST utility errors,
and fresh-vs-saved VTOC dataset-name identity. No free-space inference
is drawn from individual PDS high-water marks.

The existing regression fixture now includes FORMAT-1 type `1`.
Four new tests check the actual project layout, compatibility with
the old fixture, non-1 DSCB-type exclusion, and wrong-volume refusal.
In the assistant's independent repository-root `workarea/` workspace,
**17/17 focused Python parsing/inspection tests passed**, including
the full logical VTOC inspection path and negative volume, duplicate,
and catalog-collision cases. The full GitHub test suite could not
be executed in the assistant workspace because only GitHub remote
sources are available there, not a complete local repository
checkout. **No MVS job was submitted by the assistant.**

## Next read-only acceptance checkpoint

Re-run the same `ta2-target-review --live` command against the exact
immutable saved target evidence. The corrected program **first**
reviews the existing private evidence and contacts MVS only if the
saved report is accepted. If the genuine MVS listing has a further
unrecognized format, retain the refusal and investigate the actual
record layout; never weaken the target-collision gate merely to
produce a PASS.

`TSO002` remains a proposed destination. Neither selected staging
`SPACE` nor volume fragmentation is established. The approved
`HERC02.BCPL.TA2STG.BT0003`–`BT0020` staging namespace and
the approved `BCnnnn` VOLSER naming policy remain unchanged.
No production candidate, VOLSER reservation, DASD allocation,
selective IEBCOPY, or tape operation is authorized or performed.
**TA.2 remains IN PROGRESS.**
