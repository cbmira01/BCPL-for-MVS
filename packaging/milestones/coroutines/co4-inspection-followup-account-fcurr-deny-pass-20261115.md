# CO.4 — ACCOUNT `FCURR` and independently accepted DENY native PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Tested GitHub `main`:** `491f4acaa44a37eb4e63ff7e3bc75693c96211c7`
**Reported:** 15 November 2026
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED** —
ACCOUNT **FAIL**; DENY **PASS**. Underlying raw JES receipts not
independently inspected by the assistant.

## Operator output and retained local evidence

```text
CO.3 first lifecycle FAIL: wrong ordered BCPL records: ['FCURR', 'FAIL']
CO.4 ACCOUNT FAIL
CO.4 followup: continue after zero-RC oracle mismatch
CO.4 DENY PASS
CO.4 followup FAIL (1/2 PASS)
CO.4 followup evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-inspection-followup/20261115T140823Z-zg8lgr_p
CO.4 followup RC=1
```

`DENY` satisfied the unchanged strict native oracle under the
existing multi-stage compiler/IFOX/IEWL/GO/JES coordinator. `ACCOUNT`
produced only a failure-specific marker followed by `FAIL`; it
reached the oracle comparison after the inherited JES-success gate,
but did **not** pass its expected eight-record native behavior.
The earlier independently passing `LIMITS` test is recorded separately.
No previous failed or successful evidence is reclassified or overwritten.

## Source-grounded diagnosis

The recorded `FCURR` marker is unique to `SNAP(N,B)` and is emitted
when the test-only observer's machine `CURPTR` (vector `P!4`)
differs from the BCPL global `CO3CURR`. The source executes that
check **before** `CO4MEM INIT`, immediately after `CO3INIT()` and
before any `CREATECO()`:

- `CO3INIT()` allocates the root descriptor and sets `CO3ROOT` and
  `CO3CURR` to it; it does **not** enter the machine bridge.
- `BCPLCO.CURPTR` is assembled as `DC F'0'`; `CO2INIT()` sets it
  to the root descriptor during registration of the first worker.
- The test therefore compared a zero **unregistered** machine cursor
  with a nonzero **initialized** BCPL root pointer. Their inequality
  at this point is expected by the accepted implementation.

The diagnosis is supported by the committed source and exact error
marker. No direct memory dump of `CURPTR` from this run was supplied;
the expected values are inferred from the source transition contract.

## Candidate-local test repair and validation

ACCOUNT now calls `BOOTSNAP(N,B)` **only twice, before the first worker**,
checking `P!4=0`, initialized/consistent root globals, empty worker
list, exact vector count, exact bytes and nondecreasing peaks. Once
the first `CREATECO()` executes `CO2INIT()`, the existing `SNAP`
continues to demand exact machine/global current-coroutine equality
and the same allocator accounting. The successful `CO4MEM` eight-token
oracle and all existing worker churn and cleanup operations remain intact.

The already passing DENY source is **unchanged**. The runner adds
`--run --case account` selection with separate receipts; default
`--run` still selects both. `--check` remains offline for both.
Host-only validation covers successful and intentionally drifted
bootstrap contracts, fail-fast behavior, and exact single-case
selection. **A new native ACCOUNT PASS is still required.**

No public ABI, source compiler, core runtime object, installed
`BOOT_OBJ`, private coroutine limit implementation, or acceptance
status changes with this test-only repair. CO.4 remains IN PROGRESS;
CO.5 remains NOT STARTED.

## Host acceptance of the repair candidate

Assistant-operated isolated workspace:

- **16/16** `test_run_co4_inspection_followup.py` host unit tests PASS,
  including single-case execution, original two-case execution,
  fail-fast/JES protections, missing pre-registration check and missing
  bootstrap diagnostic rejection.
- ACCOUNT ASCII and 80-column BCPL source-card validation: PASS.
- Unique success and failure diagnostic markers: PASS.
- Python syntax validation: PASS.
- Revised inspection source validator separately checks the expected
  two ACCOUNT snapshot helpers, exactly two bootstrap accounting
  checkpoints and the retained strict post-registration checkpoint.

This is HOST-CHECKED only. Owner-native MVS result is still pending.
