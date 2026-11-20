# TA.2 — Staged PDS directory and DCB verification gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026 EST / 20 November 2026 UTC  
**Status:** Staging IEBCOPY completed; independent MVS verification pending.

## Original MVS staging result

The owner invoked the approved `ta2-stage-once --run` against TSO002 and
reported **TA2STAGE JOB 9310**, all **18 IEBCOPY steps RC=0000**, selecting
127 canonical members. The private original MVS evidence was retained at
`workarea/ta2-stage-operations/20261120T002516Z-19547`.

This is **owner-reported JES evidence**, not a direct independent inspection
by the assistant of the private job report, the staged catalog or any record
bytes. Do not equate RC=0000 with complete stage fidelity.

## Operator interaction convention

Read-only evidence probes require **no typed confirmation**. An expressly
requested state-changing `--run` may use a **single `Y`** prompt as a secondary
operator safeguard; no long confirmation phrases. The updated TA.2 staging
runner uses `[y/N]` only for a future submission/retry. A verified-successful
JOB 9310 is not authorized to be repeated or used to overwrite existing PDSes.

## New independent read-only gate

`packaging/distribution/create-tape/scripts/ta2-stage-verify` requires the
**exact original JOB 9310 evidence** and replays the original SHA256-sealed
stage-result, JES report/summary, per-attempt journal, source allocation plan,
canonical TA.0 manifest, staging worksheet, and Git-tracked approvals.

With `--live`, it submits **two read-only TSO LISTDS JES jobs**, not 18
individual invocations:

1. `LISTDS '<staged-dsn>' LABEL` for all 18 PDSes, comparing `DSORG`, `RECFM`,
   `LRECL`, `BLKSIZE` and `VOLUME` against canonical source attributes.
   The load-library member case retains **PO/U/0/6144**.
2. `LISTDS '<staged-dsn>' MEMBERS` for all 18 PDSes, requiring exactly the
   **127 manifest-selected member names**, with no missing, extra or duplicate
   names in any library.

Both jobs retain their raw JES reports, summaries, and cursor receipts in
an ignored, SHA256-sealed directory under
`workarea/ta2-stage-verification/<run>/`. No user-supplied confirmation,
DASD writes, IEBCOPY, candidate/VOLSER reservation, or tape access occurs.

The resulting status, if all predicates pass, is
`MVS_STAGED_DCB_AND_DIRECTORY_PASS_RECORD_CONTENT_PENDING`.
**Record-by-record fidelity and binary load-module identity are NOT
established by LISTDS LABEL/MEMBERS**. Those require a separate MVS-driven
verification method before a tape candidate may consume the staged libraries.

## Assistant verification

The revised staging runner and new verification script passed **75/75
focused synthetic tests** in an isolated repository-root workspace, including
checksum/journal checks, correct/incorrect TSO DCB and member inventories,
load-library attributes, unexpected names, duplicate names, wrong JOB identity,
missing attempt marker, and consolidated read-only MVS inquiry contracts.
Python syntax checks passed. Actual post-staging MVS verification is **pending**.

**No TA.2 tape candidate, AWS image, production VOLSER or release publication
is authorized by this checkpoint.** TA.2 remains IN PROGRESS.
