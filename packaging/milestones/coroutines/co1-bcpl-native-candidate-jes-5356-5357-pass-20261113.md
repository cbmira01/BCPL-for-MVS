# CO.1 — Native BCPL coroutine transfer: JOB 5356/5357 PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED** (candidate positive path)  
**Acceptance:** Candidate run PASS; **production CO.1 design gate remains OPEN**; CO.2–CO.5 NOT STARTED

## Provenance

The owner ran the guarded command from the WSL checkout with GitHub `main` pinned to:

`edb8b765b204903b0cbb9688e066319bbb15bb20`

The resulting console evidence is:

```text
Git pull RC=0
HEAD=edb8b765b204903b0cbb9688e066319bbb15bb20
CO.1 BCPL PASS: compiler JOB 5356, GO JOB 5357; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-switch/20261113T202938Z-lyrcwk18
CO.1 native BCPL runner RC=0
```

The full printer, compiler and JES logs remain on the owner's WSL filesystem; **their underlying individual listings were not independently supplied to the assistant**. The runner's existing positive oracle is documented in `tools/coroutines/run-co1-bcpl-switch.py`. It requires:

1. The real resident Cambridge compiler complete successfully, yielding System/370 source and a compiler JOB number.
2. The native job summary identify the correct CO1BGO job, report `JOB RESULT: SUCCESS` and `HIGHEST RC: 0000`.
3. Exactly five JES steps ASMA, ASMM, ASMS, LKED and GO, each RC=0000 (three IFOX00 assemblies; one IEWL link; native GO).
4. The recovered GO report produce precisely `CO1BCPL A1`, `CO1BCPL R1`, `CO1BCPL A2`, `CO1BCPL R2`, `CO1BCPL PASS`, with no missing, extra or out-of-order marker.

The observed PASS is therefore evidence of a fully executed, correctly linked, native System/370 BCPL coroutine **candidate** under MVS 3.8J, rather than a compiler-only or synthetic host test.

## Behavior demonstrated

- The real Cambridge Compiler compiled BCPL procedures and ordinary checked-entry calls under `/CN`.
- A compiler-generated BCPL `START` allocated a private worker stack via `GETVEC`, passed four arguments to separately assembled `CO1INIT`, and accepted its zero result.
- The native switch entered the generated BCPL `WORKER` procedure using the separate worker stack, transferred an initial argument, and reached the `A1` print.
- `WORKER` yielded to the root and returned a value that allowed the root to print `R1`.
- The root resumed `WORKER` with its expected argument; `WORKER` retained a checked local variable across suspension, printed `A2`, and returned naturally.
- Root observed the worker's result, printed `R2`, and finished with `PASS`.

The previous `FINIT` behavioral failure and the correction of `CO1INIT`'s R0 preservation are documented in [the source-level diagnosis](co1-bcpl-finit-r0-correction-20261113.md). This run is the first target-native verification of that correction and the entire candidate's positive path.

## Candidate isolation and limits

The candidate uses test-local G!297, G!298 and G!299; the 24-word descriptor and privately exported `STKLIM` are **not approved production interfaces**. It privately assembles a tracked `BCPLMAIN` copy and links existing accepted `BOOT_OBJ` members read-only. No installed MVS objects or canonical global assignments were modified.

This successful positive case does **not** prove arbitrary-depth recursion, multiple worker contexts, all register/condition-code cases, nested calls close to the stack limit, exhaustion/overflow handling, invalid/stale descriptors, reentrancy, deletion or resource reuse, worker reactivation after termination, or the public `CREATECO`/`CALLCO`/`RESUMECO` lifecycle library.

The immediate next work in **CO.1** is to turn the observed native ABI behavior into an owner-reviewed production design: descriptor and register-save contract, active-stack limit and guard policy, module/global allocation, worker lifetime, error handling and first-entry/exit rules. **Do not mark CO.1 CLOSED or open CO.2 without owner approval.** No new MVS run is required merely to record this PASS.
