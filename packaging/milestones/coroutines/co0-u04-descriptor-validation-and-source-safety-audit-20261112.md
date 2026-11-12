# CO.0 — Descriptor validation and source-safety audit

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**GitHub source checkpoint:** `63146b91fe3dd903d40e1b3484497fba541a94bb`  
**Classification:** SOURCE-OBSERVED analysis and proposed verification gates; **not** a native ABI or safety policy.

## Source basis

The canonical interpreted MR10 implementation is
[`coroutines.bcpl`](../../../mr10-kit-compiler/library/coroutines.bcpl),
using [`getvec-freevec.bcpl`](../../../mr10-kit-compiler/library/getvec-freevec.bcpl).
These modules use reconstruction-local globals, not the approved native
System/370 global registry. Historical `KM10.COMAIN` remains unrecovered.
This audit does not assign behavior to that historical code.

The accepted bounded interpreted negative-path oracle is
[`co0-valid-descriptor-rejections-candidate.bcpl`](../../../mr10-kit-compiler/tests/10-coroutines/co0-valid-descriptor-rejections-candidate.bcpl),
reviewed as JOB 5325 in the
[CO.0 behavior ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md).
Do not extrapolate that success to malformed pointers.

## Control-flow analysis

| Routine and input | Observed source sequence | Classification and practical boundary |
| --- | --- | --- |
| `DELETECO(0)` | Returns FALSE before dereferencing C | SOURCE-OBSERVED; bounded interpreted execution in JOB 5325 |
| `DELETECO(CURRCO)` | Returns FALSE before dereferencing C | SOURCE-OBSERVED; bounded interpreted execution in JOB 5325 |
| `DELETECO(valid inactive live C)` | Reads `C!1`, then checks head or scans `COLIST`; only matched member is passed to FREEVEC | SOURCE-OBSERVED; ordinary valid-member paths tested by JOBS 5329, 5331–5333 |
| `DELETECO(nonmember pointer)` | Reads `C!1` **before** membership scan; scan itself reads list `P!2` | **UNVERIFIED and potentially unsafe**: no arbitrary-pointer guarantee |
| `DELETECO(previously freed C)` | Reads stale `C!1` before membership validation; freed block may have allocator metadata or have been reused | **UNVERIFIED and potentially unsafe**: no double-delete experiment authorized |
| `CALLCO(valid busy target)` | Tests `CPTR!1 != 0`, returns -999 without switching | SOURCE-OBSERVED; bounded busy-root behavior exercised by JOB 5325 |
| `RESUMECO(valid busy target)` | Tests `CPTR!1 != 0`, returns -998 before clearing the current parent | SOURCE-OBSERVED; accepted CO0-U03 and bounded JOB 5325 behavior |
| `CALLCO(0)` or `RESUMECO(0)` | Dereferences `CPTR!1` with **no preceding zero check** | **UNVERIFIED and potentially unsafe**; do not run as a routine negative test |
| `CALLCO(nonmember/stale C)` or `RESUMECO(nonmember/stale C)` | Reads `CPTR!1` without list membership verification, then may write that field and invoke `CHANGECO` | **UNVERIFIED and potentially unsafe**: valid-looking memory is not sufficient |
| `COWAIT` without an established parent | Reads and clears `CURRCO!1`, then calls `CHANGECO` with that saved target | SOURCE-OBSERVED; **no** defined orphaned-context rejection |

The interpreted `GETVEC` arena allocator checks negative N, but
`CREATECO(FN,SIZE)` computes `GETVEC(SIZE+9)` and writes a fixed
synthetic first-activation frame. Accepted JOB 5330 guards only
`SIZE=-10` and `SIZE=-20`; `SIZE=-9..-1` can allocate insufficient
payload for the unconditional frame writes. This is an **additional**
storage-safety concern, not evidence that arbitrary pointers are safe.

## Owner decision required before CO.1 design

The future native implementation should explicitly choose between:

1. **Precondition contract:** The caller supplies a valid live descriptor;
   null/stale/nonmember inputs are outside the API's supported domain,
   with selected, documented safe rejections only.
2. **Validated-handle contract:** The runtime checks membership and
   lifecycle/generation before accessing user-controlled descriptor memory.
   This requires an actual native handle/registry and ownership design;
   a membership scan **after** dereferencing C does not suffice.

These are alternatives for owner review, **not** accepted design
decisions. In particular, native validation cannot reliably promise
safe handling of arbitrary unreadable System/370 addresses without a
separately designed address/ownership validation boundary.

## Safe evidence progression

- Retain accepted JOB 5325 for null/current deletion and valid busy-root
  call/resume rejection, with successful ordinary worker liveness.
- Use only **known live, valid descriptors** in further interpreted
  behavioral tests; do not probe null CALLCO/RESUMECO, stale objects,
  fabricated descriptors, orphaned COWAIT, or double-free in the canonical
  interpreter.
- Before native negative testing, decide ownership/lifecycle, supported
  inputs, rejection codes, cleanup invariants and recovery semantics
  under CO.1. Then create bounded native IFOX/IEWL/GO/JES tests.
- Preserve native abort, abend and stack-check results separately from
  interpreted `CODE=0` and from compiled BCPL program output.

## 12 November — independent JOBS 5331–5333 JES recheck

At Git `main` revision
`63146b91fe3dd903d40e1b3484497fba541a94bb`, the owner
re-executed `tools/mvs/job-summary` individually for JOBS 5331,
5332 and 5333. All three returned shell **RC=0**, reported
**JOB RESULT SUCCESS**, highest **RC=0000**, and **12/12 JES
steps RC=0000** for each (**36/36** across the three).

This **revalidates the JES receipts** for the already accepted
40/40 interpreted program records; it is **not** another execution
of the BCPL programs and does not upgrade their classification to
NATIVE-MVS-TESTED.

**Disposition:** CO0-U04's supported-valid-input boundary is
documented; arbitrary/stale descriptor safety remains **OPEN**.
CO.0 remains IN PROGRESS; CO.1–CO.5 NOT STARTED. No change to
runtime source, regression manifests, native ABI or installed MVS
datasets is implied.
