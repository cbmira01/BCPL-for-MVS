# CO.4 — Inspection batch second-run native JES failure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Tested source revision:** `d1726d3cc3a829af679df671912677a9f3dc244b`  
**Local date:** 14 November 2026 (15 November UTC)  
**Classification:** **OWNER-REPORTED FAIL**, target JES step failure not yet isolated

## Distinct operator attempts

The earlier UTF-8 printer decoding failure at `bdd1c4716cc0012d0ae314576d35bd489f4765bb` remains recorded separately in [the first-attempt document](co4-inspection-batch-printer-decode-failure-20261114.md); local evidence: `workarea/co4-inspection-batch/20261115T025919Z-ypmhu6wh`.

The next owner-operated full `--run` at corrected revision `d1726d3cc3a829af679df671912677a9f3dc244b` reported:

```text
CO.3 first lifecycle FAIL: native JES summary unsuccessful or highest RC nonzero
CO.4 LIMITS FAIL
CO.4 inspection batch FAIL (0/3)
CO.4 inspection evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-inspection-batch/20261115T031327Z-vrkmkomg
CO.4 inspection batch RC=1
```

The report decoder no longer aborted on a high-bit printer byte. The inherited CO.3 `assess()` rejected the native JES summary *before* checking the `CO4LIM` output oracle. The precise failing step(s), JES job number and any IFOX/IEWL/GO diagnostics have **not** been furnished, so they cannot be inferred from this console output. No successful native LIMITS result is claimed; ACCOUNT and DENY were not attempted due to the deliberate fail-fast gate.

## Required next diagnostic

Inspect the **existing** owner-local `limits/*/result.json`, `job-summary.log` and `job-report.log` for the second attempt. Extract only job identity, per-step RC, ABEND/JCL diagnostics, relevant IFOX/IEWL messages and `CO4LIM` records. Do **not** repeat a native submission before identifying the actual failure. Preserve both failed receipt directories and any future corrected run separately.

Potential source areas to distinguish once the actual JES evidence is inspected: private `CO4PROB` IFOX assembly, `MEMSTAT` external availability in the resident `BOOT_OBJ(BCPLMEM)` object, IEWL symbol resolution, and runtime linkage/abend. None is established as the cause by the presently supplied evidence.

**Status:** CO.0–CO.3 CLOSED (qualified); CO.4 **IN PROGRESS**; CO.5 **NOT STARTED**. No ABI promotion, runtime installation, or release follows from this report.
