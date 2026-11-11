# CO.0 — Paired canonical MR10 coroutine source promotion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Status:** **Canonical Git source promotion committed; post-promotion MVS regression pending**.

## Authorization and scope

After review of the [promotion staging inventory](co0-mr10-canonical-promotion-staging-review-20261111.md), the owner directed **“OK proceed”**. This authorized promotion of the paired reconstructed MR10 sources in GitHub `main`. No resident MVS PDS overwrite, JES submission, accepted native object promotion, release or CO.0 closure is claimed.

The preceding [candidate-aware MR10 Regression Panel](co0-mr10-candidate-panel-12of12-review-20261111.md) showed **12 PASS / 0 FAIL, runner RC=0**, against the isolated `ICLIBC` and `COCAND` implementations; separate JOBS 5238/5240/5244/5246 established the selected coroutine continuation, fixed-stack, RESUMECO and lifecycle oracles. These are **candidate INTERPRETED-MVS-TESTED** results, not a post-promotion canonical-default acceptance run.

## Coordinated Git source changes

| Canonical Git file | Promoted behavior | Source of verified candidate |
| --- | --- | --- |
| `mr10-kit-compiler/source/iclib.int` | Save the outgoing CHANGECO call-frame pointer; recover the incoming frame and its distinct continuation | `source/iclib-co0-candidate.int` |
| `mr10-kit-compiler/library/coroutines.bcpl` | Create a synthetic startup frame with `P!0=P`, `P!1=COBOOT`; run `COBOOT` on first activation | `library/coroutines-co0-candidate.bcpl` |

The canonical INTCODE source uses the exact candidate executable records with its four candidate-only `//` introductory comments omitted. The canonical BCPL source uses the candidate implementation with its four candidate-only introductory comments omitted. Existing public MR10-local global assignments and the three-word descriptor are retained.

Promotion commits: `90adfb13b300fd060cf4fb08d56bdc0f906d939e` (ICLIB), `ccdbafb129c06c4abe7c02bf8897c602a550a3c6` (BCPL library), followed by a host-only equivalence test at `tools/checks/test_mr10_canonical_coroutine_promotion.py`. The candidate files remain tracked and unmodified. Prior canonical behavior and the JOB 5231 divergence are preserved through Git history and the historical evidence records.

## Required verification; not yet accepted

1. On WSL, fast-forward `main`, check the exact HEAD and run both `test_mr10_candidate_selection.py` and `test_mr10_canonical_coroutine_promotion.py` with `python3 -B -m unittest discover`, plus a whitespace check.
2. Run the canonical-default `tools/mr10/run-regression-panel` **without** `--iclib` or `--module-override` only after separately authorized JES execution. Capture all 12 named tests, runner RC, payload JOB IDs and JES summaries; compare complete goldens. Do not substitute the preceding 12/12 candidate panel for this gate.
3. Review the previously accepted `10-coroutines/` development probes against the promoted pair, especially static first-activation source differences and saved OCODE/INTCODE structural oracles.
4. Before updating resident `MR10_SOURCE(ICLIB)` or `MR10_LIBRARY(COROUTIN)`, request separate explicit MVS dataset-staging authorization and verify Git/MVS inputs and rollback.
5. Complete the evidence-classified CO.0 behavioral contract and open questions before asking for march closure or starting CO.1.

**Disposition:** Git source promotion only. **CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED.**
