# CO.0 — U06 positive oversize refusal and recovery candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source checkpoint:** `a3e39083567f3a83b0e0a02e77212faf258e171a`  
**Status:** SOURCE-OBSERVED; MVS execution NOT YET VERIFIED

## Bounded source calculation

The canonical `CREATECO(FN,SIZE)` calls
`GETVEC(SIZE+9)`. The reconstructed MR10 arena allocator
reserves `NEED=N+3` words, including two block-header
words, so its required block length is `SIZE+12`.

A local `VEC 160` is initialized as a **161-word** free
arena. `CREATECO(WORKER,200)` needs **212 words** and must
return zero for this otherwise valid, positive oversize.
`CREATECO(WORKER,100)` needs **112 words** and fits.
A normal return and `DELETECO` should release the block,
permitting the same 100-word SIZE request again. The
test does not assume or assert pointer-address identity.

The 161-word arena is initialized exactly once. The
candidate does not request a bad pointer, negative SIZE,
overflow-inducing arithmetic or an intentional stack overrun.

## Predicted output (NOT accepted golden)

    OVERSIZE CREATE 0
    FIRST RESULT 11
    FIRST DELETE -1
    SECOND RESULT 21
    SECOND DELETE -1

Any other line, nonzero interpreter code, failed compilation
or abnormal JES result is a failure requiring diagnosis,
not an adjusted expected result.

## Reproducible MVS gate

Compile the isolated
`mr10-kit-compiler/tests/10-coroutines/co0-allocation-exhaustion-recovery-candidate.bcpl`
with canonical ICINT19/ICLIB and the existing separate
`getvec-freevec.bcpl` and `coroutines.bcpl` BCPL units.
Capture complete output, final interpreter CODE, runner RC,
independent job number/summary and 14/14 JES steps. These are
expected requirements only, not observed evidence.

A successful test supports only **bounded positive oversize
refusal and normal delete/reallocation**. It does not prove
all SIZE values, allocator arithmetic overflow, stack
bounds, worker exceptions, or native BCPLMEM behavior.
No accepted manifests, original tests or canonical runtime
are changed.

## JOB 5326 — accepted positive oversize and recovery evidence

On 12 November 2026 at source revision
`48818dab9483253ae0a2e56b7de8c9f60966b103`,
the operator ran the existing candidate through canonical
ICINT19/ICLIB with independent GETVEC and COROUTIN compilation
units. **JOB 5326 (BCCO0ALL)** produced all five expected
records, in the order shown above.

Final interpreted `EXECUTION CYCLES = 4085, CODE = 0`;
`compile-and-run --results` runner RC=0.
The independent `tools/mvs/job-summary 5326` returned RC=0,
`JOB RESULT: SUCCESS`, highest RC=0000;
**14/14 JES steps** (ASM, LKED, STGSYNI, STGTRNI,
STGCGI, STGBLIB, STGICLIB, COMP01, CG01, COMP02,
CG02, COMP03, CG03, RUN) each returned RC=0000.
Operator-local log:
`workarea/co0-u06-allocation/20261112T050129Z.log`.

**Accepted bounded classification: INTERPRETED-MVS-TESTED**
for refusal of a positive oversize request, subsequent normal
worker execution/deletion, and successful reallocation.
This does not prove exact-fit behavior, a generalized SIZE
contract, a real stack-guard mechanism, native BCPLMEM,
exceptional teardown, or address-identity reuse.
