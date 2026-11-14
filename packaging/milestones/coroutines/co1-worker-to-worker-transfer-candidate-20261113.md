# CO.1 — Direct worker-to-worker native transfer candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026 (Louisville local date)  
**Evidence:** SOURCE-OBSERVED and ASSISTANT HOST-TESTED; native MVS result PENDING  
**Source baseline:** GitHub `main` at `793c0ecdff3cc6151ad4190bd971867a47181eca`

## Reason for this probe

The owner-reported real MVS PASS for Cambridge compiler JOB 5362 and native
JOB 5363 established two simultaneously live worker stacks, each yielding
to the root and later returning normally. It did **not** establish direct
worker-to-worker transfer, preserved continuations across such a transfer,
or the distinction between a descriptor's creation parent and the active
context-switch source. No broad production interface is approved.

The tested `CO1SW` uses the caller's R8 to locate the target context,
module-private `CO1SREG` to capture incoming machine registers, and
`CURPTR` to identify the context to suspend. Its parent descriptor word
(1) is initialized in `CO1INIT` and is **not modified by `CO1SW`**.
The candidate therefore tests direct transfer *without changing a
worker's creation-parent relation*. It does not implement dynamic parent
chains, `CALLCO` or `RESUMECO` semantics.

## Candidate behavior and exact oracle

New BCPL source: `candidates/co1-bcpl-worker-hop/source.bcpl`.
Test-local globals `PEER1:295`, `PEER2:296`, `ROOTCTX:297`,
`CO1INIT:298`, and `CHANGECO:299` are fixture-only declarations,
not production Global Number Registry reservations.

The root allocates two distinct `GETVEC(1087)` stacks, one 24-word
root descriptor, and two 24-word worker descriptors. It initializes
both workers while the root is active, and verifies both workers still
have the root as their original creation parent at first entry.

The deterministic switch sequence is:

1. Root → A with 7. A checks its creation parent, initializes a local
   sentinel 3101, prints `A1`, then switches **directly** to B with 17.
2. B checks its creation parent, initializes sentinel 4202, prints
   `R1`, and switches **directly back** to A with 23.
3. A resumes at its outstanding `CHANGECO` call; it verifies return 23
   and its sentinel, prints `A2`, then yields 33 to the root.
4. Root checks 33 and its own sentinel 2718, prints `R2`, and resumes
   B with 55. B verifies its sentinel and return 55 and exits naturally
   with 42; root checks that result.
5. Root resumes A with 44. A verifies its sentinel and return 44 and
   exits naturally with 31. Root checks that result and prints `PASS`.

`R1` is printed by **worker B** to preserve the established compact
five-marker oracle; it does not imply root was active at that point.
The runner requires the exact ordered records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

Any incorrect value, creation-parent check, local sentinel, allocation
or return emits one of the existing tracked failure records, or ends
without the exact output oracle. This source does not intentionally
switch into terminated descriptors.

## Execution path, verification, and limits

`tools/coroutines/run-co1-bcpl-worker-hop.py --run` selects only the
new BCPL source and evidence directory
`workarea/co1-bcpl-worker-hop/<UTC>/`. It reuses the original
`run-co1-bcpl-switch.py` MVS driver, its `/CN` option, the independently
verified `co1change.asm`, private `BCPLMAIN` assembly/export, and the
same strict job/result assessment.

A real PASS requires resident Cambridge compilation (one job), three
IFOX steps RC=0000, IEWL RC=0000, native GO RC=0000, and the exact
five records above (second job). Only temporary native object/load
datasets are created; accepted `BOOT_OBJ` members are read-only.

**Host verification:** 13/13 focused standalone Python tests passed in
the assistant workspace, covering source/card shape, call graph,
parent/descriptor values, private stacks, local sentinels, ordered
trace, fail-closed diagnostics, fixture isolation, simulated runner
wiring and negative CLI/oracle checks. Python syntax checks also
passed. These are **HOST-TESTED** rather than compiler or MVS evidence.

A future native PASS would prove direct A → B → A transfer and the
checked return/continuation behaviors **for this bounded two-worker
case**, not arbitrary parent-chain mutation, deletion/reuse, worker
reentry after termination, invalid pointers, all registers/PSW flags,
subtask reentrancy, near-limit stack safety or production ABI readiness.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
