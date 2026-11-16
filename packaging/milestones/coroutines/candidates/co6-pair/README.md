# CO.6 — Paired observable coroutine contract candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Status:** OFFLINE-TESTED, MVS UNVERIFIED

These are two **real BCPL** applications with one exact program-output
oracle, not a demand for identical compiled code or descriptor layouts.

- `mr10.bcpl`: MR10 kit compiler → INTCODE → ICINT19; uses
  `getvec-freevec.bcpl`, canonical `coroutines.bcpl`, a bounded local
  heap and reconstructed MR10 globals.
- `native.bcpl`: Cambridge Compiler → S/370 IFOX → IEWL → native GO;
  uses separately compiled CO.3 lifecycle BCPL and isolated `BCPLCO`
  adapter, with the accepted 1024-word native worker-stack requirement.
- `expected.txt`: eleven complete `CO6PAIR` records used verbatim
  by both independent executors.

Both execute: root creates one worker; delivers arguments **11, 31,
51, 71** across four `CALLCO` calls; worker yields **21, 41, 61,
81**; worker's local **717** survives two `COWAIT` suspensions;
the worker function returns **61** naturally, then is re-entered with
**71** on the fourth call; root deletes the inactive known-live worker
and prints PASS. Both initialize through their own supported startup
contracts. Only valid calls and live handles are tested.

The order of program-visible records is:

```text
CO6PAIR MADE
CO6PAIR W1
CO6PAIR R1
CO6PAIR W2
CO6PAIR R2
CO6PAIR W3
CO6PAIR R3
CO6PAIR W4
CO6PAIR R4
CO6PAIR DEL
CO6PAIR PASS
```

The runner `tools/coroutines/run-co6-pair.py` offers `--check` with
no MVS work; `--run` to execute both engines independently;
`--run-mr10` or `--run-native` for isolated diagnosis.
The interpreted path requires one complete 14-step JES job, seven
zero-valued ICINT phases and the exact program oracle. The native path
requires two Cambridge compiler jobs, four IFOX assembly steps, IEWL,
GO and an exact native JES program oracle. The native candidate stages
only under `workarea/`, pins all three accepted CO.3 adapter inputs by
their Git blob hashes, and leaves installed BOOT_OBJ untouched.

**Evidence status:** Eight host-only unit tests passed in an isolated
assistant workspace. Neither new BCPL application has yet been
compiled or executed on MVS. An actual MVS PASS or FAIL takes precedence
over source assumptions. Never convert the original separate fixed-stack
legacy FAIL into PASS or SKIP based on this candidate.
