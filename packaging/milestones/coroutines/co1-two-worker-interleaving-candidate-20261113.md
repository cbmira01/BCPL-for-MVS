# CO.1 — Two independent native BCPL worker contexts: candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026  
**Evidence:** SOURCE-OBSERVED + ASSISTANT HOST-TESTED; native MVS result PENDING  
**GitHub baseline:** `e76912cec0058d08132ef6d7358b3b0f9e3451a4`

## Why this test follows JOB 5360/5361

The owner-reported nested-frame native pass used one independently
allocated worker stack with six live checked BCPL frames. The exact
ordered `A1 R1 A2 R2 PASS` output and zero-RC compiler/three-IFOX/IEWL/GO
steps are recorded separately in
[the JOB 5360/5361 evidence](co1-nested-frames-jes-5360-5361-pass-20261113.md).
The case did **not** test retaining two different suspended worker
contexts simultaneously. The next CO.1 uncertainty is whether the
current candidate `CO1INIT` and `CO1SW` singleton bookkeeping can
manage two *live* descriptors without destroying either register
snapshot or stack-limit association.

## Bounded candidate contract

The new test-only BCPL file
`candidates/co1-bcpl-two-workers/source.bcpl` declares the same
**test-local** G!297–G!299 numbers as the existing CO.1 candidates.
It allocates two distinct live `GETVEC(1087)` stacks and two 24-word
worker descriptors, plus one root descriptor. It makes the following
ordered actions only when the root is active:

1. `CO1INIT(ROOT,PEER1,STACK1,WORK1)`; start worker 1 with value 7.
   Worker 1 saves a local sentinel (3101), prints `A1`, and yields
   value 101 to the root.
2. Root checks return 101 and its own sentinel (2718), then prints `R1`.
3. While worker 1 remains **suspended**, root initializes a *second*
   worker using `CO1INIT(ROOT,PEER2,STACK2,WORK2)` and starts it with 8.
   Worker 2 saves independent local sentinel 4202, prints `A2`, and
   yields 202 to root.
4. Root checks 202 and its sentinel, then prints `R2`.
5. Root resumes worker 1 with 11. Worker 1 checks both its incoming
   value and local sentinel, returns **31 naturally**, and root checks
   that result.
6. Root resumes worker 2 with 22. Worker 2 independently checks its
   value and sentinel, returns **42 naturally**, and root checks it.
   Root then prints `PASS` and finishes.

Any incorrect root result, initialization, allocation, preserved local
value or natural worker return produces a failure record already
recognized by the existing strict runner (`FALLOC`, `FINIT`, `FVALUE`,
`FSECOND`, or `FLOCAL`) or terminates without the complete PASS oracle.

The experiment exercises **exactly two independent workers**, not
arbitrary creation, deletion, reinstatement of finished descriptors,
multiple MVS subtasks, or unconstrained invalid pointers. The second
`CO1INIT` is invoked only while the root is active. Its implementation
currently resets `ROOTPTR` and `CURPTR` and overwrites `WORKPTR`;
`CO1SW` uses `CURPTR` and the supplied target descriptor for transfers.
Although the unused `WORKPTR` replacement looks compatible with this
bounded scenario on source inspection, only real MVS execution can
verify the complete sequence.

## Reproducible MVS execution

`tools/coroutines/run-co1-bcpl-two-workers.py --run` reuses the existing
`run-co1-bcpl-switch.py` compiler/JES workflow and its strict oracle.
It selects **only** this new BCPL source and a separate evidence path
`workarea/co1-bcpl-two-workers/<UTC>/`. The proven `CO1CHG` IFOX module,
private `BCPLMAIN` candidate export, `/CN` compiler control, and seven
read-only installed `BOOT_OBJ` members remain unchanged.

The actual MVS run requires successful Cambridge compilation, three
IFOX RC=0000, IEWL RC=0000, GO RC=0000, and exactly these records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

JCL uses temporary object and load datasets only. No installed MVS
objects, public global assignments, historical MR10 source, numbered
regressions, or production runtime components are modified.

## Assistant checks and interpretation gate

The standalone workspace test file
`tools/checks/test_co1_bcpl_two_workers.py` passed **11/11 host tests**;
Python source syntax also checked. Host tests verify source card widths,
globals, separate buffers/descriptors, root-only initialization,
ordered switches, sentinel/result checks, exact output markers,
fixture isolation, synthetic runner path, altered-oracle rejection, and
explicit `--run`. These checks do **not** provide native BCPL or JES
execution evidence, which remains pending.

A PASS would establish a two-worker cooperative positive-path under
MVS, including preserved contexts across creation of another worker.
It would not prove a reentrant initializer, general lifecycle,
invalid/stale descriptor handling, cleanup/reuse, comprehensive
register or condition-code policy, stack boundary safety, or a final
public API. Unexpected compiler/IFOX/IEWL/GO outcomes must be
investigated from the new retained MVS evidence before changes.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
