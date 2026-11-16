# CO.6 — nested parent-chain and reuse paired candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Evidence status:** OFFLINE-TESTED; MVS UNVERIFIED

This is the second independent paired BCPL behavioral oracle. It must not
replace the first, already MVS-tested `co6-pair` fixture or the historical
MR10 fixed-stack negative case.

The two separately compiled BCPL applications are `mr10.bcpl` (kit compiler,
INTCODE/ICINT19) and `native.bcpl` (bootstrap Cambridge compiler, generated
System/370, IFOX/IEWL/GO). They use their respective valid creation/first-
activation conventions, runtime globals, coroutine descriptors and stack
capacities; no common machine representation is asserted.

Both programs exercise one root and two simultaneously live workers, nested
recursive call frames in both workers, explicit busy-`RESUMECO` rejection
without losing the parent chain, a valid worker-to-worker `RESUMECO` parent
handoff, alternating `CALLCO`/`COWAIT` argument delivery, preserved locals,
ordinary return from both workers, root-side deletion, and creation/return/
deletion of a new worker after resources are reclaimed. Resource use never
exceeds the native accepted root-plus-two-workers, 1024-word checked-stack
boundary. The negative fixture remains unchanged and genuinely failing.

The 18 exact output records, in order, are:

```
CO6NEST MADE
CO6NEST A1
CO6NEST B1
CO6NEST A2
CO6NEST B2
CO6NEST R1
CO6NEST A3
CO6NEST R2
CO6NEST B3
CO6NEST R3
CO6NEST A4
CO6NEST R4
CO6NEST DELA
CO6NEST DELB
CO6NEST C1
CO6NEST RC
CO6NEST DELC
CO6NEST PASS
```

The isolated `tools/coroutines/run-co6-nested.py` delegates directly to
the existing first-pair MVS runner, substituting only the source fixture,
output oracle/parser and evidence location. It retains all prior Cambridge,
IFOX, IEWL, JES, zero-ICINT-phase and exact-output verification gates. The
initial preflight rechecks the original pair and accepted CO.3 source hashes
before verifying this second source contract. The original shared driver
still uses its `CO6MPAIR` job name; the evidence directory and `CO6NEST`
output prefix distinguish this second test.

Use `--check` for host-only source/oracle validation; `--run` for both
independent MVS paths; `--run-mr10` and `--run-native` for isolated diagnosis.
The full outputs and result JSON are retained under `workarea/co6-nested/`.
No persistent MVS installation or source mutation is authorized. A complete
MVS PASS has not yet been reported. The runner must return nonzero if either
execution path fails.
