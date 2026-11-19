# TA.2 — Source-bounded staging allocation readiness (read-only MVS gate)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** Readiness gate implemented and offline-tested; MVS execution pending.

## Owner-reported MVS allocation proposal

At GitHub `main` `995a323aa4860fc559488402a61501e85ed955c4`, the owner ran
`ta2-allocation-plan --live` and reported:

```text
TA.2 STAGING SPACE PROPOSAL: 18/18 libraries; 127 selected; TSO002 MVS free 16045 tracks
  primary 645, secondary reserve 65, proposed total 710 (max 50% free)
Private proposed allocations/JCL and MVS evidence: workarea/ta2-allocation-plan/20261119T204153Z-17905
Draft only: no PDS allocated, no IEBCOPY stage submitted, no VOLSER/tape change.
```

The 710 proposed tracks fit within the planning budget but **do not prove
that 18 suitable free extents exist**. The 18 individual primary/secondary/
directory allocations and actual raw JES reports are private and
**have not been inspected directly by the assistant**. No destination
DASD volume or per-PDS SPACE allocation is yet approved for MVS writes.

## Readiness verification implementation

`scripts/ta2-stage-readiness --allocation-evidence <saved-run>`
verifies six exact saved records and `SHA256SUMS`, original MVS job
identities, successful source-stat evidence, and the complete original
target/source/capacity/stage-plan ancestry against the single canonical
TA.0 inventory. It independently recomputes **all 18** source-bounded
SPACE triples and the entire **127-member** JOB-less IEBCOPY deck.
Rehashed alterations to allocations, selected members, generated JCL
or MVS reports are rejected on independent replay.

With explicit `--live`, the tool additionally runs *read-only* MVS:

1. One `dspal stat` source metadata inquiry, requiring DCB/space
   equality with the pinned 18-PDS source inventory.
2. TSO LISTDS for all 18 isolated staging PDS names: catalog
   absence must be reconfirmed without contradictory attributes.
3. IEHLIST LISTVTOC on the explicitly reviewed **proposed** TSO002:
   formatted dataset-name inventory and reported free tracks must
   match saved evidence exactly.

It saves raw MVS reports and positive/refusal evidence with checksums under
ignored `workarea/ta2-stage-readiness/<run>/`. Only after the live
checks succeed, it prints the **18 individual primary/secondary/directory
triples** for owner allocation review. It has no stage `--run` option.
No DASD stage writes, tape operations, or candidate/VOLSER reservations.

The JCL remains explicitly **NOT APPROVED FOR MVS SUBMISSION**.
The `MR10_LOAD` stage still requires `PO/U/0/6144`; all other
curated PDSes `PO/FB/80/800`. IBM *OS/VS2 MVS Utilities*
(GC26-3902-1) documents the historical IEBCOPY COPY/SELECT form;
only actual MVS 3.8J IEBCOPY and subsequent MVS readback can accept
the generated deck.

## Assistant workspace checks

**35/35 focused offline tests PASS**, executed under the assistant's
isolated repository-root `workarea/`. Tests cover symlink/checksum/
unexpected-file refusal, MVS job and report integrity, altered source
or SPACE selection, independently regenerated JCL, saved-to-fresh
VTOC and capacity drift, no-submission mode, simulated live read-only
MVS success/failure, and exclusive preservation of evidence. These
are simulated MVS responses; **no assistant live MVS run or full
historical project regression** is claimed.

## Next approval and execution boundary

After the owner reports the live readiness list, review and explicitly
approve **TSO002 and the complete 18 per-PDS SPACE triples** (or
revise and regenerate the proposal). The owner must separately authorize
one-shot selective IEBCOPY staging after its guarded runner is
implemented/tested. The stage runner must use one exclusive no-retry
attempt receipt and fresh catalog/source/VTOC preflight; on any partial
failure retain earlier newly cataloged PDSes rather than overwrite
or retry. Independently compare 127 selected members with no excluded
extras, DCBs, load-library binary attributes and actual MVS behavior.

**TA.2 remains IN PROGRESS.** No staging library, candidate
`BCnnnn`, tape image, MVS IEBCOPY write or publication was created
or approved by the readiness tool.
