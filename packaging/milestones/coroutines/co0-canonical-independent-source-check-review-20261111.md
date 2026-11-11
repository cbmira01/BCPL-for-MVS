# CO.0 — Independent canonical MR10 source verification checkpoint

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Date:** 11 November 2026  
**Verified GitHub `main` HEAD:** `b5cabba8b620aba1c266b211dd1489a1f8972829`  
**Status:** **13 independent source-content assertions PASS**; Python unit tests and canonical-default JES regression not executed by this checkpoint.

## Scope and method

The assistant fetched nine tracked files directly from authoritative GitHub `main` and evaluated 13 assertions against the returned file contents, independently of the operator's WSL workspace. This is an **offline source/static verification**, not compilation of BCPL, invocation of Python unit tests, or execution of JCL under MVS.

The reviewed inputs were:

- `mr10-kit-compiler/source/iclib.int`
- `mr10-kit-compiler/source/iclib-co0-candidate.int`
- `mr10-kit-compiler/library/coroutines.bcpl`
- `mr10-kit-compiler/library/coroutines-co0-candidate.bcpl`
- `tools/mr10/compile-and-run-core.py`
- `tools/mr10/run-regression-panel`
- `tools/checks/test_mr10_candidate_selection.py`
- `tools/checks/test_mr10_canonical_coroutine_promotion.py`
- `mr10-kit-compiler/tests/00-regression-panel/manifest.tsv`

## Executed source-content assertions

| # | Assertion | Outcome |
| ---: | --- | --- |
| 1 | Canonical ICLIB text equals candidate ICLIB with only standalone `//` lines removed | PASS |
| 2 | Canonical BCPL coroutine library equals candidate with four candidate-only introductory lines removed | PASS |
| 3 | Canonical INTCODE records do not exceed 80 characters | PASS |
| 4 | Canonical BCPL source records do not exceed 80 characters | PASS |
| 5 | Canonical INTCODE retains terminal `Z` marker | PASS |
| 6 | Canonical BCPL library includes `COBOOT`, `P!0 := P`, `P!1 := COBOOT`, and `RESULTIS CHANGECO(0, C)` | PASS |
| 7 | INTCODE staging helper source excludes standalone `//` comment records | PASS |
| 8 | SYNI/TRNI/CGI/BLIBI/ICLIB are all routed through the INTCODE staging helper | PASS |
| 9 | BCPL source staging still uses the regular ASCII record reader | PASS |
| 10 | Panel source defaults to no runtime or module override | PASS |
| 11 | Canonical-equivalence test file includes both planned test methods | PASS |
| 12 | Candidate-selection test file includes comment-filter and generated-JCL test methods | PASS |
| 13 | Existing MR10 panel manifest contains 12 non-comment test records | PASS |

**Total:** 13 PASS, 0 FAIL. These checks compare GitHub source text and inspect program structure. Presence of Python test methods was checked; their execution was **not** claimed.

## Distinct prior MVS evidence

The operator previously reported a 12/12 PASS and runner RC=0 from the **candidate-aware** MR10 Regression Panel using `--iclib` and `--module-override`, recorded at [candidate panel review](co0-mr10-candidate-panel-12of12-review-20261111.md). Earlier candidate JOBS 5238, 5240, 5244, 5246 and pilot JOB 5259 are separately documented. None of those results establishes **canonical-default post-promotion** execution.

## Pending acceptance gates

1. Execute repository Python tests `test_mr10_canonical_coroutine_promotion.py` and `test_mr10_candidate_selection.py` in a suitable Python environment and capture their actual results; source inspection is not test execution.
2. Run the unmodified canonical-default `tools/mr10/run-regression-panel` with explicit JES authorization and record all 12 case results, final runner RC, payload JOB identifiers and available JES evidence.
3. Preserve the source/machine evidence-class distinction and continue the CO.0 behavioral contract and unknowns. No MVS PDS overwrite, canonical resident member replacement, or native runtime acceptance is authorized by this record.

**Disposition:** Source-level verified, **canonical MVS acceptance PENDING**. CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**.
