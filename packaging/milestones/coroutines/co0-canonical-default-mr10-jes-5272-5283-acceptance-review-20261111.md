# CO.0 — Canonical-default MR10 regression review: JOBS 5272–5283

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Source revision verified before execution:** `226201834fe205139ef259338bfd8ff508bd8930`  
**Operator local date:** 11 November 2026; **MVS JES job-log date:** 12 November 2026, 00:20  
**Status:** **PASS — canonical-default MR10 Regression Panel**, observed from operator-supplied transcript and per-JOB JES summaries. This records a passed regression gate, **not CO.0 closure or native coroutine acceptance**.

## Reproducible execution and evidence

The operator ran `git pull --ff-only origin main`, verified the exact HEAD above (RC=0), and ran `git diff --check HEAD~3 HEAD` (RC=0). The canonical-equivalence host unit tests passed **3/3, RC=0**, including a generated-JCL verification of canonical ICLIB staging. Candidate-selection host unit tests passed **6/6, RC=0**.

The authorized MVS execution then invoked **`tools/mr10/run-regression-panel --verbose`**, without `--iclib`, without `--module-override`, and with the existing `mr10-kit-compiler/tests/00-regression-panel/manifest.tsv` and unchanged expected output. The runner identified `ICINT: mr10-kit-compiler/asm/icintv19.asm`, `Tests: 12`, and `ICLIB: canonical`.

Operator-preserved WSL evidence paths (workarea, not Git artifacts):

- `workarea/co0-canonical-regression/20261111T232037Z-855.log` — complete verbose regression transcript.
- `workarea/co0-canonical-regression/20261111T232037Z-855-jes-summaries.log` — job-summary output for all twelve payloads.

The operator pasted the complete 714-line combined execution transcript and job summaries. These paths are **local evidence locations**, not copies committed to Git. No raw SYSOUT or OCODE/INTCODE decks were independently archived in this Git document.

## Case and JES evidence

| JOB | Category / case | JES steps | Highest RC | Final interpreted RUN CODE | Golden comparison |
| ---: | --- | ---: | --- | ---: | --- |
| 5272 | data-movement/scalar-vector | 10 | 0000 | 0 | PASS |
| 5273 | data-movement/bytes | 10 | 0000 | 0 | PASS |
| 5274 | calculation/integer-arithmetic | 10 | 0000 | 0 | PASS |
| 5275 | control/branches-loops | 10 | 0000 | 0 | PASS |
| 5276 | calls/nested-recursion | 10 | 0000 | 0 | PASS |
| 5277 | modules/separate-module | 12 | 0000 | 0 | PASS |
| 5278 | standard-library/basic-library | 10 | 0000 | 0 | PASS |
| 5279 | standard-library/library-scalars | 16 | 0000 | 0 | PASS |
| 5280 | standard-library/library-strings | 16 | 0000 | 0 | PASS |
| 5281 | standard-library/library-line-io | 12 | 0000 | 0 | PASS |
| 5282 | storage/getvec-reuse | 12 | 0000 | 0 | PASS |
| 5283 | coroutines/basic-coroutine | 14 | 0000 | 0 | PASS |

All 12 job-summary reports explicitly reported `JOB RESULT: SUCCESS` and `HIGHEST RC: 0000`. The **142 listed JES steps** each returned `RC=0000`. Every job executed IFOX00 `ASM`, IEWL `LKED`, and the stage/compile/code-generation/GO steps applicable to that test.

The runner reported the expected program `RP:` records and `EXECUTION CYCLES = ..., CODE = 0` for each case, then:

```text
REGRESSION PANEL COMPLETE
PASS  12
FAIL  0
TOTAL 12
Canonical regression RC=0
```

In particular JOB **5283** ran the unmodified `coroutines/basic-coroutine` test with canonical `library/coroutines.bcpl`, printed `RP: COROUTINE 77 1`, returned interpreted `CODE=0`, and finished with 14/14 zero-RC JES steps.

## Interpretation and limitations

This is **INTERPRETED-MVS-TESTED** evidence of the corrected canonical MR10 `ICLIB` / `COROUTIN` implementation and unchanged 12-case regression oracle. It separately confirms the prior **candidate-aware** 12/12 panel, but does not establish that MVS resident `SOURCE(ICLIB)` or `LIBRARY(COROUTIN)` members were overwritten. The `compile-and-run` tool read canonical **Git host sources** and assembled/ran a job-specific `RUNMOD` under MVS; there is no asserted permanent resident replacement.

No native System/370 CHANGECO implementation is established by this interpreted panel. The CO.0 behavioral-contract and historical-source gaps remain, including complete negative-path semantics, full historical KM10 contract and first-activation structural reconciliation for all development probes.

**Disposition:** Canonical-default MR10 regression gate **PASSED**; **CO.0 IN PROGRESS**, CO.1–CO.5 NOT STARTED. No milestone closure or installed MVS promotion is implied.
