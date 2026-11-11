# CO.0 — Canonical-default MR10 regression verification procedure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Status:** PROCEDURE COMMITTED; **canonical-default execution pending**

## Purpose

Verify the paired canonical Git source promotion at `mr10-kit-compiler/source/iclib.int` and `mr10-kit-compiler/library/coroutines.bcpl` by executing the existing 12-case MR10 Regression Panel **without** `--iclib` or `--module-override`. This is a distinct gate from the 12/12 candidate-aware panel already observed and recorded.

## Guarded operator procedure

Run from the project repository root after updating GitHub `main` to the exact procedure commit. Do not enable shell fail-fast; record command return codes and skip the JES submission when any preliminary gate fails.

1. `git pull --ff-only origin main` and verify `git rev-parse HEAD` matches the current published commit.
2. `git diff --check HEAD~5 HEAD`; require RC=0.
3. `python3 -B -m unittest discover -s tools/checks -p 'test_mr10_canonical_coroutine_promotion.py' -v`; require three passing tests (including real canonical ICLIB JCL-deck generation) and RC=0.
4. `python3 -B -m unittest discover -s tools/checks -p 'test_mr10_candidate_selection.py' -v`; require six passing tests and RC=0.
5. With separately approved MVS/JES execution, `tools/mr10/run-regression-panel --verbose`; capture the full `--verbose` transcript in a unique `workarea/` log, preserving the pipeline's runner RC with Bash `PIPESTATUS[0]`. Extract each printed `JOB` ID and run `tools/mvs/job-summary` for every reported payload on success or failure; retain the full printer data and avoid inferring missing IDs.
6. On any failure or BLOCKED outcome, preserve the printer evidence and do not claim acceptance. On 12/12 PASS with runner RC=0, record the output for review. No resident `MR10KIT.SOURCE(ICLIB)` or `MR10KIT.LIBRARY(COROUTIN)` overwrite is authorized by this procedure.

## Acceptance boundaries

The expected panel is **12 PASS, 0 FAIL, RC=0** against the existing goldens and canonical sources, with no candidate selection options. This expectation is not a recorded outcome. The canonical Git promotion did not install or overwrite any MVS PDS members. The previous candidate panel and JOB 5259 remain valid separate evidence, not substitutes for this run.

CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**.
