# CO.0 — U06 bounded fragmentation and coalescing candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Baseline:** GitHub main `68de4fcc234c91d67e4f126f7fceeadc49bf7749`  
**Status:** SOURCE-OBSERVED; MVS candidate NOT EXECUTED

## Source-derived expected allocation sequence

`CREATECO(WORKER,SIZE)` requests `GETVEC(SIZE+9)`,
which requires **SIZE+12** block words. In a 241-word
arena (`VEC 240`), allocate two independent coroutines
with SIZE=100: each consumes 112 words, leaving 17 free.
Both are resumed normally and remain allocated.

A SIZE=200 request needs 212 contiguous words and must
fail while both remain allocated. After deleting the
first coroutine, the 112-word released block is separated
from the 17-word tail by the second live coroutine, so
the same 212-word request must still fail.
Deleting the second coroutine should merge the adjacent
free blocks, restoring a contiguous 241-word block.
The SIZE=200 coroutine then executes and deletes normally.

This tests normal free-list coalescing and list unlinking,
not pointer-address identity, stale descriptors, double
free, stack overrun, negative SIZE or native storage policy.

## Predicted exact output (NOT accepted golden)

    FIRST RESULT 11
    SECOND RESULT 21
    BIG BEFORE 0
    DELETE FIRST -1
    BIG PARTIAL 0
    DELETE SECOND -1
    BIG AFTER OK
    BIG RESULT 31
    BIG DELETE -1

## Verification gate

Run `mr10-kit-compiler/tests/10-coroutines/co0-allocation-coalescing-candidate.bcpl`
through canonical ICINT19/ICLIB with the existing separate
GETVEC/FREEVEC and COROUTIN library BCPL units.
Require the exact nine lines, final interpreted CODE=0,
runner RC=0 and independent **14/14 JES steps RC=0000**.
Preserve the local log and job number. Never infer complete
BCPL phase success from zero JES RC alone.

No canonical runtime, golden fixture, accepted suite manifest,
MVS permanent dataset or native ABI change accompanies this
research candidate.

## JOB 5328 — accepted bounded fragmentation/coalescing evidence

At source revision `76e43378cf8b146c57bdc58bf8763903c98fb049`,
JOB **5328 (BCCO0ALL)** produced all nine exact records
predicted above, in order. Final interpreted report:
**EXECUTION CYCLES = 6511, CODE = 0**;
runner RC=0. Independent `tools/mvs/job-summary 5328`:
**JOB RESULT: SUCCESS**, highest RC=0000,
summary RC=0 and **14/14 JES steps RC=0000**.
Operator-local log:
`workarea/co0-u06-coalescing/20261112T051949Z.log`.

**Accepted INTERPRETED-MVS-TESTED scope:** the tested
two-coroutine fragmentation, one-deletion insufficiency,
full deallocation, adjacent free-block coalescing and
subsequent large-coroutine execution/deletion. It does
not validate malformed SIZE, arbitrary pointers, stack
guards, native BCPLMEM or exceptional cleanup.
