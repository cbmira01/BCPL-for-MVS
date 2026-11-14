# CO.2 — Repeated native continuations: first MVS FAIL and source correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation (IN PROGRESS)  
**Date:** 14 November 2026  
**Tested GitHub revision:** `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5`  
**Classification:** OWNER-REPORTED NATIVE-MVS-TESTED — FAIL, source-oracle defect identified

## Actual reported result

The owner executed `tools/coroutines/run-co2-native-continuations.py --run` and received:

```text
CO.2 BCPL FAIL: native BCPL records differ: ['X1', 'Y1', 'X2', 'Y2', 'X3', 'FVALUE']
CO.2 BCPL evidence: workarea/co2-native-continuations/20261114T150923Z-c6yyrdvw
CO.2 continuations runner RC=1
```

This result **must remain FAIL**; it is not replaced by the earlier successful
CO.2 baseline JOB 5374/5375, and no new successful native run is claimed.
The provided output identifies no compiler or native JES job numbers and does
not individually establish the IFOX, IEWL or GO completion codes. Complete
local reports are retained in the reported workarea path but were not supplied
for independent review.

## Reproducible source finding

The submitted fixture has incorrect expected values for the recursive BCPL
`DEEP1` and `DEEP2` return expressions:

| Worker | Base case | Recurrence | Requested depth | Actual arithmetic result | Previously expected |
| --- | ---: | --- | ---: | ---: | ---: |
| `DEEP1` | 13 | `R+N` | 4 | 23 | 17 |
| `DEEP2` | 17 | `R+N` | 5 | 32 | 22 |

`WORK1` therefore returns its BCPL test-local failure value 98 after the
`X3` marker instead of naturally returning 31; the root's first
`CHANGECO(7,P1)` checks for 31 and reports `FVALUE`. This is a
source-grounded explanation consistent with the observed marker sequence,
not direct inspection of the worker's register R7 or the private JES report.
The second incorrect assertion in `WORK2` would likewise prevent its normal
42 return if execution progressed that far.

## Repair and verification boundary

Only these assertions in
`candidates/co2-native-continuations/source.bcpl` change:

```bcpl
  IF DEEP1(4) \=23 RESULTIS 98
  IF DEEP2(5) \=32 RESULTIS 98
```

The source-level unit test now independently extracts the two base cases and
checks the `R+N` recursion against the worker's numeric oracle. Offline
validation also established that the regression rejects the original
incorrect fixture and accepts the corrected one. No assembly or compiler
changes are justified by this failure. `BCPLCO`, the existing `BOOT_OBJ`
members, test-local globals and temporary-JCL linkage remain unchanged.

**Disposition:** corrected candidate prepared for a **new** MVS run; no
previous failed result is reclassified. CO.2 remains IN PROGRESS, awaiting
separate native IFOX/IEWL/GO evidence and owner acceptance. CO.3–CO.5 remain
NOT STARTED.
