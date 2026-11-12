# CO.0 — U06 middle-descriptor cleanup and survivor liveness

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source baseline:** `76e43378cf8b146c57bdc58bf8763903c98fb049`  
**Status:** SOURCE-OBSERVED; new candidate NOT MVS-TESTED

A 401-word arena holds three simultaneously live
SIZE=100 coroutines, each needing 112 block words.
Creation order A, B, C produces the descriptor list
`C -> B -> A -> ROOT`. Ordinary calls yield each
descriptor's initial return and clear its parent field.

The candidate deletes the **middle** descriptor B.
The canonical `DELETECO` is source-observed to assign
`P!2 := C!2` when unlinking a non-head member.
It checks the resulting live link `C!2 = A`,
then re-enters A and C without touching deleted B.
A new descriptor D is allocated in the same arena and
executes; D, A and C are deleted normally.

This is **not** a test of double deletion, stale B
dereference, pointer identity, native heap policy,
exceptional termination or stack exhaustion.

**Predicted exact ordered output (NOT an accepted golden):**

    A FIRST 11
    B FIRST 21
    C FIRST 31
    DELETE MIDDLE -1
    LINK OK
    A AGAIN 41
    C AGAIN 51
    D RESULT 61
    DELETE D -1
    DELETE A -1
    DELETE C -1

Run `mr10-kit-compiler/tests/10-coroutines/co0-middle-descriptor-cleanup-candidate.bcpl`
with canonical ICINT19/ICLIB, the existing separate
GETVEC/FREEVEC and COROUTIN BCPL units. Require all
eleven records, interpreted final CODE=0, runner RC=0,
and independently verified 14/14 JES steps RC=0000.
Retain the generated local report and job number.

No accepted manifest, runtime implementation, permanent
MVS dataset or native ABI is changed.

## JOB 5329 — accepted bounded middle-descriptor cleanup

On 12 November 2026 at GitHub revision
`03d83683cdca156215b7c7ccab50b71576237116`,
JOB **5329 (BCCO0MID)** matched all eleven records above
in order. Final interpreted **EXECUTION CYCLES = 7073,
CODE = 0**, `compile-and-run --results` runner **RC=0**.
Independent `tools/mvs/job-summary 5329` returned
**RC=0**, **JOB RESULT: SUCCESS**, highest RC=0000
and **14/14 JES steps RC=0000**.
Operator-local evidence log:
`workarea/co0-u06-middle-cleanup/20261112T060610Z.log`.

**Accepted INTERPRETED-MVS-TESTED scope:** deleting a
non-head/middle live-list descriptor, preserving both
neighboring live descriptors for re-entry, normal reuse
of recovered capacity and final ordinary cleanup.
The freed descriptor B was never dereferenced again;
this proves neither stale-pointer safety nor double-free
behavior, exceptional cleanup, or native ownership.
