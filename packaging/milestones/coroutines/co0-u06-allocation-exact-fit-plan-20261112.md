# CO.0 — U06 exact-fit allocator boundary candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source checkpoint:** `48818dab9483253ae0a2e56b7de8c9f60966b103`  
**Status:** SOURCE-OBSERVED; exact-fit candidate NOT MVS-TESTED

The canonical `CREATECO` requests `GETVEC(SIZE+9)`,
and the fixed-arena `GETVEC` requires `N+3` total
words. Hence `SIZE+12` words are required.
A `VEC 160` supplies a 161-word arena.

- `CREATECO(WORKER,150)` needs 162 words; expect zero.
- `CREATECO(WORKER,149)` needs exactly 161 words,
  exercising the allocator's no-split path.
- Delete and re-create with SIZE=149 to exercise reuse
  of the entire recovered arena. No pointer identity
  or generic overflow-safety conclusion is asserted.

**Predicted ordered output, NOT accepted golden:**

    ONE TOO LARGE 0
    EXACT RESULT 31
    EXACT DELETE -1
    REUSE RESULT 41
    REUSE DELETE -1

The isolated source is
`mr10-kit-compiler/tests/10-coroutines/co0-allocation-exact-fit-candidate.bcpl`.
Use canonical ICINT19/ICLIB, compile and link the existing
separate GETVEC and COROUTIN units, preserve all output,
interpreter codes, runner RC and independent JES summary.
Acceptance requires exact five records, CODE=0,
runner RC=0 and 14/14 JES steps RC=0000.
Unexpected output must be investigated, not retroactively
declared acceptable.

No invalid-pointer use, negative SIZE, arithmetic
overflow, forced stack overrun, permanent dataset change,
native ABI decision, or accepted-test manifest edit.

## JOB 5327 — accepted exact-fit boundary evidence

On 12 November 2026 at GitHub revision
`68de4fcc234c91d67e4f126f7fceeadc49bf7749`,
JOB **5327 (BCCO0ALL)** produced all five predicted
output records: `ONE TOO LARGE 0`, `EXACT RESULT 31`,
`EXACT DELETE -1`, `REUSE RESULT 41`,
`REUSE DELETE -1`. The interpreter reported
**3849 cycles, CODE=0** and the runner returned **RC=0**.
The independently requested `tools/mvs/job-summary 5327`
returned **RC=0**, **JOB RESULT: SUCCESS**, highest
RC=0000 and all **14/14 JES steps RC=0000**.
Operator log: `workarea/co0-u06-exact-fit/20261112T051006Z.log`.

**Accepted INTERPRETED-MVS-TESTED scope:** one-word-over
refusal, exact-fit allocation, ordinary deletion and subsequent
exact-fit reuse under canonical ICINT19/ICLIB. General SIZE
validation, malformed/negative requests, arithmetic overflow,
stack exhaustion and native BCPLMEM remain unverified.
