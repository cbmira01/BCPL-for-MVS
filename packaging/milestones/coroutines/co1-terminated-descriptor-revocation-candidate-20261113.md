# CO.1 — Terminated descriptor revocation before MVS storage release

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026 (Louisville local date)  
**Status:** SOURCE-OBSERVED + ASSISTANT HOST-TESTED; native MVS result PENDING  
**Verified baseline:** GitHub `main` `9f66a691749953f786b258e888a32a8e5e371f6c`

## Native evidence and design question

Owner-reported Cambridge compiler JOB 5368 and native JOB 5369 passed the
bounded descriptor registry experiment under MVS 3.8J: all three IFOX,
IEWL and GO steps RC=0000, and strict `A1 R1 A2 R2 PASS`. That candidate
rejects unknown target addresses *before dereference*, but does **not**
remove registered addresses after a worker terminates. `FREEVEC` of such
a descriptor would leave an unsafe registered, dangling pointer.

The new experiment tests a two-phase protocol for a *known-live*
terminated worker: **revoke registry membership, then FREEVEC its stack
and descriptor**. This is an architecture probe, not approval of the
production coroutine library, public lifecycle or global ABI.

## Exact candidate

- `candidates/co1-bcpl-revocation/co1change.asm` derives from the
  tested bounded-registry IFOX module. Existing `CO1INIT`, `CO1SW`,
  checked stack switching and `CO1SREG` remain unchanged. One separate
  IFOX `ENTRY CO1DROP` is added.
- `candidates/co1-bcpl-revocation/source.bcpl` declares test-local
  `CO1DROP:296`, `ROOTCTX:297`, `CO1INIT:298`, `CHANGECO:299`, alongside
  historical `GETVEC:87` and `FREEVEC:88`.
- `tools/coroutines/run-co1-bcpl-revocation.py --run` reuses the
  established compiler/IFOX/IEWL/GO runner. A fail-closed, test-only
  trailer adapter adds `G!296 -> CO1DROP` to its already proven
  `G!298/G!299` registrations; no common runner, historical compiler,
  public global registry or installed object is modified.
- `tools/checks/test_co1_bcpl_revocation.py` exercises the exact
  source/card invariants, trailer layout, failure handling and
  command opt-in without submitting any MVS job.

`CO1DROP(worker)` receives a BCPL word pointer in R7 and returns through
standard `RETIMPL`. It first compares the byte-address form against
`REGW1`/`REGW2`, **before reading the descriptor**. It refuses a null,
unknown, already-revoked, active or non-terminated worker with `R7=-2`.
For a registered inactive worker in state 3 (`TERMINATED`), it writes
candidate-only state 4 (`REVOKED`), zeros that registry slot, and
returns `R7=0`. On rejection it writes neither descriptor nor registry,
nor changes `CURPTR`, `STKLIM`, `APLIMIT`, G54 or G55. Original R0 and
R10 are restored; R4/R5/R6 use the existing three-word BCPL return
frame saved by `STM 4,10,0(15)` (28-byte call workspace).

**Important restriction:** `REGCNT` remains a lifetime admission count;
revoked slots are **never re-registered** in this candidate. In
particular, it does not solve the ABA hazard of a freed address being
reused by a later worker with the same bare pointer. Production reuse
requires a stronger identity/generation/lifetime contract, and possibly
a separate opaque handle. Nor does this experiment make arbitrary
`CO1INIT` operands safe, establish general task reentrancy, or permit
cancellation of suspended workers.

## Exact native test plan

The fixture allocates two `GETVEC(23)` descriptor vectors and two
independent `GETVEC(1087)` worker stacks. The root descriptor lives
on the root stack. Both workers start, yield 101 and 202, and keep
independent local sentinels. The root verifies:

1. `CO1DROP` rejects the root, an unregistered address, and a new or
   suspended worker with `-2` without disturbing successful transfers.
2. Worker A resumes with 11 and returns 31 normally in state 3. A
   successful `CO1DROP(A)` changes state 3 to 4 and returns 0; only
   **then** does the root call `FREEVEC` on A's stack and descriptor.
3. A saved *stale* A word pointer is rejected by both `CHANGECO`
   (`-1`) and `CO1DROP` (`-2`) after `FREEVEC`. Worker B remains
   suspended and must resume normally after these rejections.
4. Worker B resumes with 22, returns 42, then undergoes the same
   verified revoke-before-free and stale-pointer rejection sequence.
5. No `GETVEC` or `CO1INIT` is called after revocation; no registry
   address is reused or re-registered during this test.

The inherited strict MVS success oracle remains exactly:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

An unexpected result follows an existing recognized `FALLOC`, `FINIT`,
`FVALUE`, `FSECOND` or `FLOCAL` path or fails the five-record oracle.
The candidate driver uses one resident Cambridge compilation job and a
native job with three IFOX, one IEWL and one GO step, all requiring
RC=0000. It links candidate objects into `&&` temporary MVS datasets,
reads accepted `BOOT_OBJ` members without modification, and retains
full evidence under `workarea/co1-bcpl-revocation/<UTC>/`.

## Host verification and boundary

**21/21** targeted host tests passed in the assistant's separate
workspace, plus Python compilation checks, 71-column IFOX limits,
eight-character label checks, 80-column BCPL source records and exact
source blob hashing. Simulated driver tests verify correct binding of
`G!296`, rejection of a colliding global and required `--run` opt-in.
No actual BCPL compiler, IFOX, IEWL or MVS execution has yet occurred
for this candidate. Host checks do not establish a production memory
safety proof, particularly when addresses can be reused.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
No public ABI or production runtime promotion is authorized by this
candidate alone. The CO.1 production descriptor and lifecycle contract
remains subject to owner review.
