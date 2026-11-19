# TA.1 — Track B source/restored directory read-only preflight PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 18 November 2026 EST / 19 November 2026 UTC  
**Status:** Live preflight **PASS**; IEHLIST submissions **NOT EXECUTED**.

## Owner-provided actual MVS-facing evidence

The owner invoked the Git-controlled preflight using `main` at
`58f98db10dd5b790ea52c488070c6de2a98b98d5`,
without `--run`:

    TA.1B IEHLIST preflight PASS: MR10_LOAD TSO003; restored LOAD TSO002; both PO/U/0/6144.
    BTA102 SHA-256 and JOB 9136 receipt PASS; no tape media operation.
    No IEHLIST JES submission or ICINT19 GO executed.
    Evidence: workarea/ta1b-operations/BTA102-track-b-directory-20261119T023717Z-11735

The live preflight verifies the source `HERC02.BCPL.MR10KIT.LOAD`
on **TSO003**, restored `HERC02.BCPL.TA1B.LOAD` on **TSO002**,
each with `DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144` and member
`ICINT19`. It revalidates the independent JOB 9136
IEBCOPY restoration receipt and preserved BTA102 tape SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.

These claims rely on the owner's terminal output and the reviewed
Git-controlled source; the private ignored evidence directory was
not separately inspected by the assistant. No source/restored
IEHLIST FORMAT report exists from this invocation.

## Authorized boundary and next gate

The prepared runner `scripts/run-ta1-track-b-directory --run`
must not be invoked until **separate explicit owner authorization**.
It will recheck the source and restored dataset/volume identities,
then require an exact interactive confirmation, write an irreversible
one-shot receipt, and submit **two read-only IEHLIST JES jobs** in order:
`TA1BSRC` for TSO003 and `TA1BDST` for TSO002.
Both read the load libraries using `DISP=SHR`; they may create
JES printer/report output but must not alter existing MVS data.
The runner checks IEHLIST RC=0000, successful IEF142I
and matching nonalias `ICINT19` entry `000000` and
attributes `02E2`. A stopped/uncertain submission is not retried.

An IEHLIST directory match alone would not establish binary
equivalence or successful ICINT19 program fetch/execution.
The canonical restored-STEPLIB eight-step MR10 scalar/vector
execution remains separately gated.
TA.1 is **IN PROGRESS**.

## Subsequent owner approval of IEHLIST submission (18 November 2026, 21:46 EST)

After the above read-only PASS, the owner expressly authorized
one `TA1BSRC` and one `TA1BDST` read-only IEHLIST FORMAT job,
with no tape operation and no restored `ICINT19` GO.
The guarded one-shot runner was re-reviewed without source changes;
this note records permission only, **not** any JES execution result.
See [IEHLIST authorization](ta1b-directory-submission-authorization-20261118.md).
