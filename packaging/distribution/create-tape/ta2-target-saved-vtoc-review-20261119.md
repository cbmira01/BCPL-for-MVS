# TA.2 — Saved MVS target evidence review and guarded VTOC recheck

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** Read-only MVS evidence verification tool implemented and synthetic-tested; no staging allocation or candidate production authorized.

## Actual owner-reported MVS checkpoint

At GitHub main `5e5d9b605da53ca44736fa29c387a284cbf1d12c`,
the owner executed the previously accepted `ta2-target-preflight`
with `--live --volume TSO002` and reported:

```text
TA.2 TARGET PREFLIGHT: 18/18 catalog-absence observations; 1 raw IEHLIST VTOC saved
Private MVS evidence: workarea/ta2-target-preflight/20261119T170234Z-17334
VTOC free capacity/uncataloged allocations still require review; no DASD/tape changes.
```

This establishes **reported** TSO LISTDS catalog-absence results for all
18 owner-approved staging DSNs and one saved raw IEHLIST report.
The assistant has **not inspected** the user's private JES or VTOC bytes;
the provided console report does not establish target free tracks, target
space fragmentation, source-byte identity or final DASD placement.

## Independent saved-evidence reviewer

The new
`packaging/distribution/create-tape/scripts/ta2-target-review`
accepts only one exact timestamped target-preflight run under ignored
`workarea/`. It checks the original three saved files and exact
`SHA256SUMS`, disallows extra/missing/linked files and contradictory
receipt data, validates both distinct MVS job IDs, and independently
replays the entire TA.2 source/capacity/stage-plan ancestry.

It re-checks the 18 exact staging DSNs, source worksheet checksum,
LISTDS catalog absence and IEHLIST VTOC volume identity. It identifies
formatted volume dataset names from the classic `SER NO / SEQNO`
listing, refuses ambiguous headers, conflicting data-set names,
unexpected VOLSERs, saved utility errors, or any staging dataset name
seen in the raw VTOC. Original reports are never overwritten.

With explicit `--live`, the tool repeats **two read-only MVS JES
inquiries** using the existing authenticated `ta2-target-preflight`
mechanism and verifies that the fresh *set of formatted VTOC dataset
names* matches the saved one. Both new full JES reports, the
independent review and SHA-256 digests are saved exclusively under
`workarea/ta2-target-review/`. Any failure leaves raw evidence and
a refusal record; no automatic retry or data-set modification is used.

## What capacity means

Classic IEHLIST `LISTVTOC FORMAT` may print a volume-level
`THERE ARE <n> EMPTY CYLINDERS PLUS <m> EMPTY TRACKS ON THIS VOLUME`
summary. The reviewer recognizes that specific output conservatively,
using **15 tracks per cylinder** as already documented in the project's
MVS TK5 `dspal-space.py`. If missing/ambiguous, it reports no verified
total. If present, it records the MVS-reported free-track figure as
**planning evidence only**. Total free tracks do not prove sufficiently
large individual free extents for 18 separate PDS allocations.

The review receipt also records summed **source** track allocations,
source high-water values and source PDS directory allocations, explicitly
marked as *not* available destination DASD space, compact curated
member size, or an approved staging `SPACE` allocation.

The VTOC free-space semantics and role of Format-5 DSCBs are described in
IBM's OS/VS2 MVS DADSM logic and IEHLIST documentation. The project's
live MVS output, not generalized modern z/OS samples, determines which
particular format and numeric fields are usable here.

References:

- IBM, *OS/VS2 MVS DADSM Logic*, Release 3.8 (SY26-3828-2):
  https://www.bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/SY26-3828-2_OS_VS2_MVS_DADSM_Logic_197808.pdf
- IBM, *IEHLIST sample output*:
  https://www.ibm.com/docs/en/zos/3.1.0?topic=listing-iehlist-sample-output

## Verification and outstanding gates

The assistant's isolated repository-root workspace passed **34/34 new
TA.2 target-review tests**, **26/26 prior target-preflight tests**, and
**43/43 staging JCL tests** (**103/103 focused tests**); Python syntax
checks passed. These tests use synthetic IEHLIST/JES results, including
VTOC volume mismatches, absent/extra/linked files, SHA-256 drift,
catalog collisions, duplicate DSCBs/names, conflicting free-space
summaries, invalid job identities, true no-write behavior, saved-vs-fresh
inventory drift, and failure preservation.

The owner must not interpret this offline acceptance as having already
run the new reviewer against the private actual IEHLIST report. Next
acceptance evidence is a user-run MVS-facing `--live` review of the
retained target run. Before staging write approval the project must
review actual volume free-space fragmentation and needed stage extent
sizes, choose 18 destination `SPACE` allocations, check live source
identity and target absence, then review one-shot selective IEBCOPY and
independently compare selected/restored records.

`TSO002` remains a **proposed** destination, not an approved allocation.
No `BCnnnn` tape VOLSER is reserved or used. TA.2 remains IN PROGRESS.
