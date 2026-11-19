# TA.2 — Source-bounded staging SPACE proposal and read-only MVS recheck

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**State:** Read-only proposal code, locally synthetic-tested; no DASD staging or candidate-media writes authorized.

## Real MVS evidence

From GitHub `main` `fc4b1b3e37d84f908dce71cf15c54f2439b17eaa`, the
owner reported the successful corrected target review:

```text
TA.2 TARGET REVIEW: 18/18 saved catalog checks; 30 VTOC dataset rows; fresh MVS check PASS
Private review evidence: workarea/ta2-target-review/20261119T181059Z-17632
IEHLIST reported 16045 free tracks on TSO002 (unverified contiguity; staging SPACE unapproved).
No staging allocation, candidate or tape changes.
```

This is owner-reported results from actual MVS LISTDS/IEHLIST. The complete
private MVS reports and per-PDS track/directory allocation values were not
transferred to the assistant; they must be read and independently validated
by the new on-host script before a proposal can be accepted.

The **approved** staging name range remains
`HERC02.BCPL.TA2STG.BT0003`–`BT0020`. `TSO002` is still a
**proposed DASD destination only**. The future production tape
VOLSER convention is `BCnnnn`, with no candidate or VOLSER reserved.

## Allocation sizing — proposal, not approval

`scripts/ta2-allocation-plan` reads the exact checksum-pinned successful
target-review receipt, replays original target, source/capacity and stage-plan
MVS evidence, verifies the 18 canonical member maps, then derives the following
**draft-only** per-PDS `SPACE=(TRK,(primary,secondary,directory))` proposal:

- `primary_tracks = source_tracks_allocated + max(4, ceil(source_tracks_allocated / 10))`;
- `secondary_tracks = max(2, ceil(source_tracks_allocated / 10))`;
- `directory_blocks = max(source_directory_allocated + max(2, ceil(source_directory_allocated / 4)), ceil(selected_members / 3) + 2)`.

This intentionally uses the **entire existing source PDS allocation** as a
conservative sizing reference; it does **not** pretend source high-water
tracks are live member bytes or that the 127 selected members occupy their
entire original PDSes. The 76 excluded development members are never copied
by the proposed IEBCOPY `SELECT` cards. One `MR10_LOAD` dataset must retain
`PO/U/0/6144`; all other selected PDSes retain `PO/FB/80/800`.

The sum of all 18 proposed `primary+secondary` tracks must not exceed
**50% of the exact MVS-reported volume free-track total**. This is a
conservative planning margin, *not* a proof that 18 compatible contiguous
free extents are available, nor an approved allocation. A failure of
that policy refuses the proposal rather than silently shrinking space.

## MVS-facing proposal gate

Usage after pulling GitHub `main`:

```bash
packaging/distribution/create-tape/scripts/ta2-allocation-plan \
  --target-review workarea/ta2-target-review/20261119T181059Z-17632 \
  --volume TSO002 --live
```

The single command:

1. Rechecks saved `review.json`, `catalog-report.txt`,
   `vtoc-report.txt` and exact `SHA256SUMS`, verifying original target
   and stage/source evidence from the one TA.0 design manifest.
2. Repeats **read-only** `dspal stat` MVS LISTDS/IEHLIST source
   capacity observations. Its temporary JES files remain in repository
   `workarea/`, not system temporary storage.
3. Repeats two **read-only** MVS TSO LISTDS target-absence and IEHLIST
   VTOC queries on the explicitly proposed DASD volume.
4. Requires current source DCB, allocation, directory, target catalog
   state, formatted VTOC dataset-name inventory and reported free-track
   total to agree with pinned earlier evidence. Refuses any drift.
5. Exclusively saves full raw MVS output, a SHA256-pinned
   `stage-allocations-proposed.json`, `planning-review.json`,
   JOB-less `stage-iebcopy-draft.jcl`, and `SHA256SUMS` under ignored
   `workarea/ta2-allocation-plan/<run>/` and prints only compact totals.

The draft `stage-allocations-proposed.json` is an **operational proposal**,
not a second member-selection manifest. It uses the existing
`ta2-stage-jcl` schema and validated renderer to generate exactly
18 guarded IEBCOPY steps and 127 `SELECT MEMBER` cards. The
JCL includes an explicit **NOT APPROVED FOR MVS SUBMISSION** warning,
and the runner has **no submit/write action**. Failed MVS queries retain
the original private reports and a failure receipt. No retries or
DASD/media mutations are performed.

The exact source/target MVS raw evidence stays in `workarea/` and is
not committed to GitHub. No created files or directories outside the
repository root are required by the new runner.

## Tests and remaining acceptance decisions

**40/40 new focused offline tests PASS** in the assistant's isolated
repository-root workspace. These exercise exact 18-PDS/127-member
sizing and ordering, bounded 50% primary+secondary budget, invalid
track and directory counts, load PDS DCB preservation in selection
metadata, evidence checksums and symlink refusal, saved VTOC and source
drift, a simulated live MVS operation with private evidence, no
target inquiry after source drift, and no MVS contact in offline mode.
The tests use synthetic records, not actual MVS execution. The full
historic project regression suite was not executed in this partial
assistant workspace.

**Next decision:** inspect the *actual* per-PDS totals and decide
whether to approve `TSO002` and all 18 proposed `SPACE` triples,
or refine the allocation policy. IEHLIST-reported total free tracks
does not by itself establish available extents; a later fresh MVS
one-shot staging execution must remain separately gated. Then verify
source-versus-staged exact 127-member sets, DCBs and binary fidelity
with MVS IEBCOPY/IEHLIST and actual execution where applicable.

**TA.2 remains IN PROGRESS.** No PDS allocation, IEBCOPY staging
submission, AWS image production, version freeze or `BCnnnn`
reservation is authorized or performed by this step.
