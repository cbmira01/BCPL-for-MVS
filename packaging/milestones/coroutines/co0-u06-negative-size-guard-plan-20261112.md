# CO.0 — U06 bounded negative SIZE refusal candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source baseline:** `03d83683cdca156215b7c7ccab50b71576237116`  
**Status:** SOURCE-OBSERVED; new candidate NOT MVS-TESTED

## Guard and exclusion

Canonical `CREATECO(FN,SIZE)` calls `GETVEC(SIZE+9)`.
The allocator immediately checks `IF N < 0 RESULTIS 0`.
Thus SIZE=-10 produces N=-1 and SIZE=-20 produces
N=-11, both strictly inside the early negative guard.
The test uses only these two negative inputs, then a
SIZE=100 normal coroutine, to test subsequent liveness.

The nearby range SIZE=-9 through SIZE=-1 is
**excluded**: N=0 through N=8 may allocate a block
that is too small for the unconditionally initialized
synthetic coroutine frame. A successful allocation there
may corrupt the fixed arena; no recovery promise applies.
Arithmetic wraparound and stack overflow are excluded.

## Predicted output (NOT accepted golden)

    NEG TEN CREATE 0
    NEG TWENTY CREATE 0
    NORMAL RESULT 51
    NORMAL DELETE -1

## MVS gate

Compile isolated
`mr10-kit-compiler/tests/10-coroutines/co0-negative-size-guard-candidate.bcpl`
with canonical ICINT19/ICLIB, plus existing separate
GETVEC/FREEVEC and COROUTIN units. Require exact four
records, final interpreted CODE=0, runner RC=0 and
independent 14/14 JES steps RC=0000. Preserve the
complete generated log and independent JES summary.

This candidate demonstrates only the source-guarded
negative-N allocator rejection path and normal
post-rejection liveness. It is not a new accepted
golden, native API validation rule or general policy
for invalid `SIZE`.

## 12 November 2026 — JOB 5330 acceptance

**INTERPRETED-MVS-TESTED (bounded):** Owner-executed JOB **5330** (`BCCO0NEG`) at source revision `40436cbc3f31c8a39426207754d609384b8d7bee` matched all four predicted records, in order:

    NEG TEN CREATE 0
    NEG TWENTY CREATE 0
    NORMAL RESULT 51
    NORMAL DELETE -1

Canonical ICINT19 completed with `EXECUTION CYCLES = 3163, CODE = 0`; runner RC=0. Independent `tools/mvs/job-summary 5330` returned RC=0, JOB RESULT SUCCESS, highest RC=0000 and **14/14 JES steps RC=0000**. Operator-local log: `workarea/co0-u06-negative-size/20261112T064450Z.log` (not claimed to be committed).

This accepts only SIZE=-10 and SIZE=-20 through the source-defined negative-N guard, followed by normal execution and cleanup. SIZE=-9..-1, integer overflow, general invalid-SIZE safety, stack overrun and native allocation remain **UNVERIFIED**. No native test or API validation policy is implied.
