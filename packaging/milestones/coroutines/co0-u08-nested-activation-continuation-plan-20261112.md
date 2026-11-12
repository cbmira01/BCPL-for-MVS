# CO.0 — U08 nested activation and continuation oracle candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source baseline:** `dad7a3573e5751d6810d3ddca3f720f76e252481`  
**Status:** INTERPRETED-MVS-TESTED (bounded), JOB 5332; native UNVERIFIED

## Investigated distinction

JOB 5331 established alternating suspension of two workers with independent
local accumulators, but each worker suspended directly in its own loop.
The older `continuation-divergence.bcpl` tested a nested leaf transfer and
identified the original wrong-continuation defect (JOB 5231); it was not
an accepted two-worker nested activation oracle.

This new candidate tests **two suspended, nested call chains concurrently**:
`WORKA/WORKB -> MIDDLE -> LEAF -> COWAIT`. Each `LEAF` retains the local
`SAVED`, each `MIDDLE` retains `ANCHOR`, and each worker returns a derived
value after suspension. The root alternates A, B, A, B and then deletes
both idle descriptors. No MR10 descriptor internals are used in assertions.

**Candidate:**
`mr10-kit-compiler/tests/10-coroutines/co0-nested-activation-continuation-candidate.bcpl`

## Predicted oracle — verified in JOB 5332

    LEAF 1 WAIT 33
    ROOT A1 33
    LEAF 2 WAIT 43
    ROOT B1 43
    LEAF 1 GOT 7
    MID 1 GOT 100
    A RESULT 100
    ROOT A2 101
    LEAF 2 GOT 8
    MID 2 GOT 131
    B RESULT 131
    ROOT B2 132
    DELETE A -1
    DELETE B -1

The first transfer from A yields `30+3=33`; B yields `40+3=43`.
On resume, A's deepest function returns `7+33=40`; its middle
activation adds the saved `60` and returns `100`. The worker then yields
`101`. B analogously returns `8+43+80=131` and yields `132`.

## Reproducibility and acceptance

Host-side structural review checks block delimiter balance, width, bounded
number of call sites and independently calculated arithmetic; these checks
are **not** an MR10 compiler execution. The candidate deliberately uses
accepted BCPL forms and canonical MR10 library modules.

Run `tools/mr10/compile-and-run --results --installed-icint MR10_LOAD` with
this BCPL source and separate `getvec-freevec.bcpl` and `coroutines.bcpl`
under the canonical ICLIB. Preserve complete output and the actual runner
RC. Require all fourteen predicted records in order, final interpreted
`CODE=0`, and an independent `tools/mvs/job-summary JOBNUMBER` confirming
all JES steps RC=0000. Promote only after those checks agree.

The equivalent native scenario will require an approved CO.1 global/header
mapping and an independently tested native implementation. MR10 globals
6-8, 87-95 are not approved native allocations. This does **not** verify
native registers, stack boundaries, invalid descriptors, exceptional worker
termination, recursive transfer, or the historical missing `KM10.COMAIN`.

CO.0 remains IN PROGRESS; CO.1–CO.5 NOT STARTED. No regression manifest was changed by this acceptance.


## 12 November 2026 — JOB 5332 verification and acceptance

**Source revision:** `cc9e4c36d2593e3d0486e9eced5faa8f59d738cf`.
**Execution:** JOB 5332 (`BCCO0NES`) via canonical installed ICINT19, canonical ICLIB, and separately compiled GETVEC/FREEVEC and COROUTIN BCPL units.

The owner-reported MVS output matched **all 14 expected records in their exact order**, including A/B nested `LEAF` resume values, `MIDDLE` local-variable results, worker results, root yields and both successful `DELETECO` operations. Final interpreter output: `EXECUTION CYCLES = 9017, CODE = 0`; runner RC=0. Preserved operator-local report: `workarea/co0-u08-nested-activation/20261112T162535Z.log` (not committed).

The independent `tools/mvs/job-summary 5332` display reports JOB RESULT SUCCESS, highest RC=0000 and **12/12 JES steps RC=0000** (STGSYNI, STGTRNI, STGCGI, STGBLIB, STGICLIB, COMP01–03, CG01–03 and RUN). CPU 1.02 sec, SRB 0.12 sec, SYSOUT 806 records. No shell RC for the summary command was separately printed, so none is asserted.

**Classification: INTERPRETED-MVS-TESTED for this bounded two-context nested-activation and continuation scenario.** No native System/370 stack, register restoration, global mapping or descriptor layout is established. CO0-U08 native comparability remains open pending CO.1 design and native MVS testing.
