# CO.0 — U08 repeated suspension within nested activation frames

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source baseline:** `5cd2906763ea7c416417cc13835d1e673e70ee1e`  
**Status:** SOURCE-OBSERVED candidate and host-checked oracle; MVS UNVERIFIED

## Evidence gap

Accepted JOB 5331 proved interleaved persistent local state in two workers.
Accepted JOB 5332 proved a single suspension and resumption per nested LEAF,
followed by return through MIDDLE and the worker. Neither test proved that
two nested LEAF frames could each suspend **twice at distinct continuations**
while other contexts run, retaining a local value from the first resume
until the second resume.

The new source is
`mr10-kit-compiler/tests/10-coroutines/co0-nested-double-yield-candidate.bcpl`.
It alternates A/B six times: first WAIT1, then GOT1/second COWAIT,
then GOT2/nested return/worker COWAIT. Each LEAF keeps SAVED and FIRST;
each MIDDLE keeps ANCHOR. The oracle uses observable behavior only and
makes no assertions about descriptor fields or storage addresses.

## Predicted exact program records — unaccepted

    LEAF 1 WAIT1 33
    ROOT A1 33
    LEAF 2 WAIT1 43
    ROOT B1 43
    LEAF 1 GOT1 7
    ROOT A2 40
    LEAF 2 GOT1 8
    ROOT B2 51
    LEAF 1 GOT2 11
    MID 1 GOT 111
    A RESULT 111
    ROOT A3 112
    LEAF 2 GOT2 12
    MID 2 GOT 143
    B RESULT 143
    ROOT B3 144
    DELETE A -1
    DELETE B -1

A: SAVED=33, ANCHOR=60, FIRST=7, SECOND=11; final
value 11+7+33+60=111, followed by yield 112.
B: SAVED=43, ANCHOR=80, FIRST=8, SECOND=12; final
value 12+8+43+80=143, followed by yield 144.

## Checks, verification, and boundaries

Host-side independent checks established balanced BCPL block delimiters,
80-column source-line limit, six root CALLCO sites, two CREATECO and
DELETECO sites, four COWAIT call sites (LEAF twice; workers once each),
and the eighteen source-predicted output lines through independent arithmetic.
These are structural and symbolic checks, **not** a BCPL compilation or an
ICINT19/MVS execution. The existing canonical coroutine and allocator modules
are used without modification.

Require actual MVS compilation using installed canonical ICINT19/ICLIB,
separate GETVEC/FREEVEC and COROUTIN units, all 18 exact ordered records,
final interpreted CODE=0, runner RC=0, and independent
`tools/mvs/job-summary JOBNUMBER` reporting all JES steps RC=0000.
Capture the complete output log and source SHA. Promote only after that
separate verification.

The scenario does **not** establish native S/370 execution, stack overflow
protection, native register liveness, ABI/global assignment, malformed
coroutine descriptors, exceptional termination, or historical KM10.COMAIN.
No regression manifest or golden is revised; CO.0 remains IN PROGRESS;
CO.1–CO.5 are NOT STARTED.
