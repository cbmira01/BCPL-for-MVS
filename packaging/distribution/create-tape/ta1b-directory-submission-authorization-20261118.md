# TA.1 — Track B owner authorization of source/restored IEHLIST comparison

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics  
**Authorized:** 18 November 2026, 21:46 EST  
**State:** **AUTHORIZED, NOT EXECUTED**.

## Authority and exact operation

The owner has now explicitly approved the next gate following
the live read-only source/restored directory preflight PASS.

Only two read-only JES programs are in scope, in this order:

1. `TA1BSRC`: `IEHLIST LISTPDS FORMAT` of source
   `HERC02.BCPL.MR10KIT.LOAD`, DASD VOLSER `TSO003`.
2. `TA1BDST`: `IEHLIST LISTPDS FORMAT` of the restored
   `HERC02.BCPL.TA1B.LOAD`, DASD VOLSER `TSO002`.

Each directory DD is `DISP=SHR`. No tape media operation,
modification of either library, rerun of `TA1BREST`,
new DASD load PDS allocation or executable `ICINT19` GO
is authorized by this approval.

The original read-only preflight evidence is at:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T023717Z-11735/`.

## Reviewed one-shot execution gate

The already committed `packaging/distribution/create-tape/scripts/run-ta1-track-b-directory`
was reviewed at GitHub `main` `3978c1c738ba8ffd8797b47d960a3d4fffb156e2`.
No implementation change is required.

The script checks live source/restored MVS `stat/ls`
for PO/U/0/6144, source TSO003, restored TSO002 and exactly
`ICINT19`; original JOB 9136 summary and original
BTA102 SHA-256 must still match. Then the operator must type
`COMPARE ICINT19 DIRECTORIES`. A second live preflight
precedes an exclusive-create no-retry marker; the marker
precedes either job submission.

Each of the **two** MVS `IEHLIST` jobs must return RC=0000
and its accepted `IEF142I` message. The runner reads actual
`LISTPDS FORMAT` output, extracts the nonalias `ICINT19`
entry and attributes, and requires matching entry `000000`
and attributes `02E2`. A missing, contradictory or failed
receipt halts processing; neither job is automatically retried.
All private JES evidence stays under `workarea/ta1b-operations/`.
No report is fabricated as evidence before MVS executes.

**Verification:** 12/12 code-path invariant checks passed
during approval review. The unchanged source has the previous
35/35 offline test result; no new code or live result is claimed.

## Acceptance boundary

Successful IEHLIST checks would establish *directory metadata*
preservation only, not byte-for-byte equality or successful
System/370 execution. The canonical MR10 scalar/vector `ICINT19`
GO using the **restored STEPLIB** requires a separate
explicit owner authorization. TA.1 remains IN PROGRESS.
