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
