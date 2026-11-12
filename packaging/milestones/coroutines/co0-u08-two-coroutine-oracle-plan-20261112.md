# CO.0 — U08 two-coroutine local-state oracle candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source baseline:** `362026463d5c060e88cc90f4eca406df04852f5e`  
**Status:** INTERPRETED-MVS-TESTED (bounded), JOB 5331; native UNVERIFIED

## Gap and scope

Existing CO.0 cases separately exercise worker return/re-entry (JOB 5324),
parent chains (RESUMECO), and multiple descriptors with a stateless worker
(JOB 5329). This candidate adds **two simultaneously live, alternately
called coroutines**, each preserving its own local `TOTAL` and
post-`COWAIT` local `NEXT` across three suspensions. Its observable contract
is independent of the MR10 descriptor layout and allocator address reuse.

The implementation uses reconstructed MR10 test initialization and
provisional global numbers for the interpreted execution substrate only.
Native globals, descriptor layout, stack ownership, and first-entry ABI
are **not** approved by this probe.

## Candidate source and predicted result

`mr10-kit-compiler/tests/10-coroutines/co0-two-coroutine-local-state-candidate.bcpl`

The source calls A with 1,2,3 and B with 10,20,30 in alternating order.
A starts at 100; B starts at 1000. Each worker updates its own `TOTAL`
and yields with `COWAIT(TOTAL)`. The next call supplies its next `NEXT`.
Both suspended descriptors are deleted after the final yields.

**Eight-record expected oracle; matched exactly in JOB 5331:**

    A ONE 101
    B ONE 1010
    A TWO 103
    B TWO 1030
    A THREE 106
    B THREE 1060
    DELETE A -1
    DELETE B -1

## Verification gate

Use canonical installed ICINT19 and canonical ICLIB with separate
`getvec-freevec.bcpl` and `coroutines.bcpl` units. Require exact eight
ordered records, interpreter `CODE=0`, runner RC=0, and independent
`tools/mvs/job-summary JOBNUMBER` verification (all JES steps RC=0000).
Retain the full run log, source revision, job number, and module identities.
JOB 5331 confirms this bounded interpreted oracle. Do not enroll it in accepted regression manifests or claim native verification without separate owner review.

## Explicit exclusions

No arbitrary descriptors, forced stack overflow, exotic SIZE, recursive
coroutine entry, worker exceptional termination, automatic cleanup, or
native System/370 operation is tested. A matching interpreted result is
an oracle for later native comparison, not native acceptance.

## 12 November 2026 — JOB 5331 acceptance evidence

**Executed source revision:** `3540202e6da809d2cba55b61ea48f7d3638ef195`.
Owner-executed `tools/mr10/compile-and-run --results --installed-icint MR10_LOAD` with the source and canonical separate GETVEC/FREEVEC and COROUTIN BCPL units produced **all eight expected records in exact order**. ICINT19 final completion: `EXECUTION CYCLES = 5138, CODE = 0`; runner RC=0. Local report: `workarea/co0-u08-two-coroutine/20261112T135926Z.log` (operator-local, not committed).

**Independent JES check supplied by owner:** `tools/mvs/job-summary 5331` reported JOB 5331 `BCCO0TWO`, JOB RESULT SUCCESS, highest RC=0000, **12/12 steps RC=0000** (five STG, three COMP, three CG and one RUN step), CPU 0.97 seconds, SRB 0.12 seconds, SYSOUT 800 records. The displayed JES result does not separately print the summary tool's shell return code; no such code is asserted.

**Classification:** INTERPRETED-MVS-TESTED for two alternating suspended workers preserving independent BCPL local accumulators across three calls apiece and ordinary successful deletion. No native execution, general descriptor safety, deep stack behavior, or ABI mapping is claimed. The original predicted oracle remains preserved above, and the candidate source is unchanged.
