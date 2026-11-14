# CO.2 — Repeated continuations: JOB 5378/5379 native PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation — IN PROGRESS  
**Date:** 14 November 2026 (Louisville local time)  
**Tested source:** GitHub `main` at `5f941bb34cc70649f0325bd73f42eeb67397c5d6`  
**Evidence class:** OWNER-REPORTED NATIVE-MVS-TESTED — PASS

## Operator-reported result

The owner executed `tools/coroutines/run-co2-native-continuations.py --run` after applying the arithmetic-oracle repair. The complete operator-provided console result is:

```text
CO.2 BCPL PASS: compiler JOB 5378, GO JOB 5379; IFOX 3, IEWL 1, GO 1; X1 Y1 X2 Y2 X3 R1 Y3 R2 PASS
CO.2 BCPL evidence: workarea/co2-native-continuations/20261114T161730Z-1a8_w7bf
CO.2 continuations runner RC=0
```

| Stage | JOB | Evidence and acceptance |
| --- | --- | --- |
| Cambridge compiler | 5378 | Driver completed, submitted/generated /CN native BCPL source |
| IFOX ASMA / ASMM / ASMS | 5379 | Three assembler steps accepted at RC=0000 by strict runner |
| IEWL LKED | 5379 | One link step accepted at RC=0000 by strict runner |
| Native GO | 5379 | One execution step accepted at RC=0000 by strict runner |
| Native BCPL output | 5379 | Exact ordered `X1 Y1 X2 Y2 X3 R1 Y3 R2 PASS` |
| End-to-end runner | — | Exit status 0 |

The native runner checks completed job identity, all five named JES steps
with RC=0000, the overall highest RC=0000 and the complete ordered BCPL
records. It assembles temporary candidate objects, builds a temporary
load module, and references the installed `BOOT_OBJ` library with
`DISP=SHR`; it does not install a new resident `BCPLCO` object.

The full compiler, generated source, JCL and JES evidence are retained by
the owner in `workarea/co2-native-continuations/20261114T161730Z-1a8_w7bf`.
The assistant did not directly examine those detailed files; the
PASS is **owner-reported**, not independently replayed.

## Behavioral scope

The two workers use independent `GETVEC(1087)` stack allocations and
nested `DEEP1(4)` / `DEEP2(5)` checked BCPL call chains. A hands
111 to B, B hands 211 to A, A hands 112 to B, and B hands 212 to A.
Each worker validates its nested local and published stack boundaries
after both resumes. A returns 31 naturally to the root; the root later
resumes B with 313; B returns 42 naturally. Root stack boundaries and
known-terminated-worker refusal are checked by the BCPL fixture.

This extends [CO.2 JOB 5374/5375](co2-native-changeco-jes-5374-5375-pass-20261114.md)
without changing `bootstrap-toolchain/asm/bcplco.asm`.
A prior run at `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5`
[failed](co2-native-continuations-failed-oracle-20261114.md)
with `X1 Y1 X2 Y2 X3 FVALUE`; the fixture incorrectly compared
recursive results against 17/22 instead of 23/32. That first run remains
**FAIL**. This is a new PASS at the corrected revision, not a
retroactive rewrite of prior evidence.

## Explicit exclusions and disposition

These runs do not independently validate the entire condition-code/PSW
context, arbitrary invalid or freed pointers, safe stack reclamation,
multiple parent chains, concurrent tasks, public-global registration or
complete coroutine lifecycle. `STKLIM` and `APLIMIT` are set by the
IFOX candidate but are not independently read in this BCPL fixture;
G54/G55 checks and checked-entry success are indirect boundary evidence.

**Conclusion:** This is a second native PASS supporting the focused
CO.2 implementation gate. CO.2 remains **IN PROGRESS** pending a separate
owner acceptance decision; CO.3–CO.5 remain NOT STARTED.
No production install, regression renumbering or public API promotion.
