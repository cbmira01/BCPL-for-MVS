# CO.1 — Bounded descriptor registry native PASS: JOB 5368/5369

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026, Louisville local date (UTC evidence dated 14 November)  
**Classification:** **OWNER-REPORTED NATIVE-MVS-TESTED**; bounded experimental negative and positive paths  
**Disposition:** Candidate native execution PASS; production ABI/design gate OPEN; CO.2–CO.5 NOT STARTED.

## Exact revision and operator receipt

The owner's WSL checkout fast-forwarded to GitHub `main` at
`4aa5b15d768d97654d469aae18f457be5de1c96f`, and the owner ran
`tools/coroutines/run-co1-bcpl-registry-guard.py --run`.

The reported output was:

```text
Git pull RC=0
HEAD=4aa5b15d768d97654d469aae18f457be5de1c96f
CO.1 BCPL PASS: compiler JOB 5368, GO JOB 5369; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-registry-guard/20261114T014228Z-3sc0ya0d
CO.1 registry-guard native runner RC=0
```

The strict inherited MVS driver accepts only successful Cambridge
compilation, a completed `CO1BGO` native job at highest RC=0000,
individual `ASMA`, `ASMM`, `ASMS`, `LKED`, `GO` at RC=0000, and
exactly the following ordered GO records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The full generated assembler, JES reports, and machine-readable
result are preserved in the owner's WSL evidence directory.
They have not been independently provided to or reviewed by the
assistant; native results are classified from the owner's terminal
output and the runner's acceptance criteria, not invented JES data.

## Behavior established for this isolated candidate

The experimental `CO1CHG` assembler maintains a module-private
registry of one root and two distinct worker descriptor byte
addresses. Its `CO1SW` compares a requested target address against
those registered addresses **before the first target-state load**.
The candidate BCPL fixture requires:

- Two valid worker initializations; rejection of a third worker
  registration with test-only return `-2`, without painting the
  rejected worker's stack.
- Both workers entering normally, yielding values 101 and 202,
  while retaining separate stack allocations and local sentinels.
- Rejection of a null target, an unregistered `-1` word pointer, and
  the active root descriptor, with test-only `CHANGECO` result
  `-1` and intact root state.
- Successful resumption of worker 1 (return 31) and worker 2
  (return 42), each acquiring state 3 on natural termination.
- Rejection of their subsequent resume attempts, and another
  active-root rejection, with the same `-1` outcome before
  final `PASS`.

Because the runner's oracle includes the final `PASS` produced only
after these checks, the owner-reported MVS execution supplies target-native
evidence for the tested membership guard, two-worker capacity limit,
continued successful switching after errors, and known-live
terminated-state rejection. The source-level ordering establishes
that the guard checks membership before target memory dereference;
this is not a blanket proof for all invalid machine pointers.

## Safety qualifications and disposition

The registry is **bounded, static and test-only**. Once an address
is registered, this implementation does not unregister it, maintain
generations, or verify that its allocated memory is still live.
It also does not guard every invalid `CO1INIT` operand, provide
production recovery from arbitrarily hostile or inaccessible
addresses, support more than two workers, or offer reentrant/MVS
subtask-safe operation. The accepted test-only `-1` and `-2`
results and 24-word descriptor are not approved public ABI.

The runner uses separately assembled experimental sources and
temporary MVS object/load datasets with accepted `BOOT_OBJ`
members read-only. No production runtime, permanent global allocation,
numbered regression, release asset, or final ABI was installed or
promoted by this test.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
Next engineering gate: owner-reviewed production descriptor ownership,
allocation liveness, safe deletion/reuse, stack and lifecycle
semantics before CO.2.
