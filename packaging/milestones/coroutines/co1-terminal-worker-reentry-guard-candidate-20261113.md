# CO.1 — Terminated-worker re-entry guard candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026 (Louisville local date)  
**Evidence:** SOURCE-OBSERVED + ASSISTANT HOST-TESTED; native MVS result PENDING  
**Baseline:** GitHub `main` `fab2a36c2288c80da28f6098b787d30aba1ed2f6`

## Purpose and scope

JOB 5364/5365 passed the direct worker A → B → A transfer, checked
suspension/resumption and natural returns on native MVS. However, the
validated `CO1CHG` still ends a returned worker at `CO1BAD B CO1BAD`,
with no rejection of a subsequent attempt to resume that worker. Such
a transition would enter a non-returning loop. Before treating the
candidate as production-ready, test the narrowly defined behavior of
**resuming a known-live descriptor after natural termination**.

This is an isolated experimental IFOX/BCPL variant, **not** a new public
`CHANGECO` ABI or an approved lifetime state machine. The owner must
review production state, deletion, and diagnostic decisions separately.

## Candidate-specific native change

`candidates/co1-bcpl-terminal-guard/co1change.asm` copies the verified
candidate source without changing the original fixture or installed
`BOOT_OBJ`. Only the following actions are new:

1. At `CO1WDONE` following normal generated-BCPL worker return, read the
   current descriptor from `CURPTR`, then set descriptor word 0 to **3**
   (candidate-only TERMINATED) **before** forwarding R7 to the root.
2. At `CO1SW` entry, after saving R0–R15 to private `CO1SREG` and before
   changing the outgoing descriptor or stack limits, read the target's
   state word from its known-live descriptor. If it equals 3, branch to
   `CO1TERM`. Other state values retain the old switch path.
3. At `CO1TERM`, build the normal three-word BCPL `RETIMPL` frame in the
   compiler-supplied call workspace, return fullword **−1 in R7**, and
   restore the original caller R0/R2/R10. The caller's R4/R5/R6 are
   restored through `RETIMPL`; `CURPTR`, `STKLIM`, `APLIMIT`, G54 and G55
   are unchanged on the rejected transfer.

The guard is intentionally **not** a general pointer verifier: it
assumes an addressable, live 24-word descriptor supplied by the trusted
fixture. It does not dereference stale or unallocated storage safely,
reject an already-active target, prove reentrancy or specify cleanup.
The original `CO1SREG` static buffer still limits the candidate to
single-MVS-task cooperative execution.

## Test-only BCPL sequence

The BCPL fixture uses two separate `GETVEC(1087)` worker allocations,
24-word descriptors, and temporary globals G!297–299. Both workers
first yield to root, retaining independent local sentinels. Then:

1. Root resumes worker A with 11; it returns 31 naturally. Root checks
   A's state word is 3 and its return value is 31.
2. Root calls `CHANGECO(777,A)` and requires immediate return **−1**, with
   root's sentinel intact and A's state unchanged. Worker B is still
   suspended during this rejection.
3. Root resumes worker B with 22; it returns 42 naturally. Root verifies
   B's state word is 3 and the returned value is 42.
4. Root attempts `CHANGECO(888,B)` and requires immediate **−1** without
   a context change. Only then does it print `PASS` and finish.

The strict existing native output oracle remains the five records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

Failure paths print the established `FALLOC`, `FINIT`, `FVALUE`,
`FLOCAL` or `FSECOND` records, which the inherited runner rejects.
A lost continuation, unexpected natural-return state or non-returning
branch cannot satisfy that oracle.

## Reproducibility, evidence, and gates

`tools/coroutines/run-co1-bcpl-terminal-guard.py --run` uses the existing
`run-co1-bcpl-switch.py` for real Cambridge compilation and the same
three IFOX, one IEWL and one native GO JES steps. It substitutes only
this BCPL source, isolated IFOX source, and a dedicated evidence path
`workarea/co1-bcpl-terminal-guard/<UTC>/`. The compiler `/CN` control
and all accepted `BOOT_OBJ` members are reused read-only, with only
`&&` temporary MVS object/load datasets.

**Assistant-side checks:** 13/13 focused Python tests passed in an
isolated workspace, including fixed-format IFOX cards, state mutation
order, pre-snapshot terminal check, the 12-byte return frame, R0/R2/R10
restoration, root/other-worker continuation, distinct stacks and both
negative return checks. Python syntax and Git blob checks also passed.
These are host checks, **not** actual IFOX/IEWL/GO evidence.

The next gate is a real MVS run from the committed candidate. Record
exact compiler/GO jobs, five JES step RCs and the ordered native BCPL
records. A failure must drive diagnosis of the retained JES report;
no installed object is to be promoted automatically.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
