# CO.0 — U08 two-coroutine local-state oracle candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source baseline:** `362026463d5c060e88cc90f4eca406df04852f5e`  
**Status:** SOURCE-OBSERVED design; candidate NOT MVS-TESTED

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

**Predicted eight records; NOT an accepted golden:**

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
The predicted output remains **UNVERIFIED** until MVS execution and JES
confirmation; do not enroll it in accepted regression manifests yet.

## Explicit exclusions

No arbitrary descriptors, forced stack overflow, exotic SIZE, recursive
coroutine entry, worker exceptional termination, automatic cleanup, or
native System/370 operation is tested. A matching interpreted result is
an oracle for later native comparison, not native acceptance.
