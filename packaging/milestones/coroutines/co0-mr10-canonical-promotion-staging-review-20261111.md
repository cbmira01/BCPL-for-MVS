# CO.0 — MR10 canonical repair promotion: staged review inventory

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Status:** **STAGED FOR REVIEW IN GIT ONLY**. No canonical source replacement, resident MVS dataset staging, native implementation or march closure performed.

## Decision boundary

The [approved-in-principle MR10 repair decision](co0-mr10-iclib-repair-design-decision-20261111.md) prefers correcting the canonical reconstructed interpreter-hosted coroutine bridge after candidate evidence, rather than keeping two permanent implementations. Candidate tests now include JOBS **5238**, **5240**, **5244**, **5246**, the **5259** scalar/vector pilot, and the [full 12/12 MR10 Regression Panel](co0-mr10-candidate-panel-12of12-review-20261111.md) (runner RC=0). These are **INTERPRETED-MVS-TESTED**, not native S/370, outcomes.

This record stages the exact candidate inputs and proposed destination mapping for **review**. It is not approval to edit canonical files or MVS `SOURCE(ICLIB)` / `LIBRARY(COROUTIN)`, and it does not turn the candidate panel into a post-promotion canonical regression.

## Tracked source inventory and proposed mappings

| Git canonical destination (unchanged) | Candidate source (unchanged) | What must change if promoted |
| --- | --- | --- |
| `mr10-kit-compiler/source/iclib.int` | `mr10-kit-compiler/source/iclib-co0-candidate.int` | Save outgoing CHANGECO call-frame pointer, restore incoming frame and continuation together; preserve existing INTCODE entry names/operators |
| `mr10-kit-compiler/library/coroutines.bcpl` | `mr10-kit-compiler/library/coroutines-co0-candidate.bcpl` | Use an explicit `COBOOT` first-activation continuation and matching synthetic frame; retain existing callable globals, library lifecycle entry points and three-word descriptor |

Canonical `ICLIB` currently has `6 LIP2 SG9 LIP1 SG10 LIP0 SIG7 ...`; candidate `ICLIBC` instead begins `6 LIP2 SG9 LP0 SIG7 LIP3 SG7 ...` and uses the incoming descriptor's saved call frame to derive the return continuation. Canonical `CREATECO` builds `P!0=0`, `P!1=0` and executes the startup code after `CHANGECO`; candidate `CREATECO` builds `P!0=P`, `P!1=COBOOT` and returns the `CHANGECO` result. The candidate adds `COBOOT` while retaining `CALLCO`, `COWAIT`, `RESUMECO`, `DELETECO` and MR10-local globals.

These are source-observed details, **not** an assertion that blind copying is the correct final promotion procedure. Candidate-only comments saying “not canonical” must be reconciled before canonical source edits. Historical and prior canonical behavior remains traceable through Git and [JOB 5231's failure](co0-changeco-continuation-divergence-jes-5231-review-20261111.md).

## Review gates before canonical replacement

1. Reverify WSL checkout HEAD, clean tracked working tree, exact candidate paths and the 6 host-only candidate-selection checks. A successful earlier panel does not substitute for this.
2. Verify whether all five accepted `10-coroutines/` development probes, including compiler/frame-layout artifact oracles and the **static-stack variant**, have been reproduced with the intended paired candidate implementation. The prior candidate static-stack JOB 5240 uses `T10FIXC`, not an unchanged canonical `T10FIX` source.
3. Complete the CO.0 behavior table and open-question ledger: initial activation, call/yield/result and resume/parent relation, natural return/re-entry, allocation/deletion/reuse, active/stale/invalid inputs and unverified historical boundaries. Explicitly label untested error behavior.
4. Review whether canonical `ICLIB` and coroutine library should be changed together as a single source-controlled promotion; preserve original counterexample, its failing JOB 5231 evidence, original golden identities and candidate regression inputs.
5. Request distinct approval for canonical Git source replacement, then independently verify canonical-default (no candidate options) host checks and full MR10 regression. Changing installed MVS members or promoting any objects requires **separate explicit authorization** and a rollback path.
6. Preserve CO.0 status until the owner accepts the evidence-classified behavioral contract. No CO.1 design/implementation begins automatically.

## Staging disposition

The existing `ICLIBC` and `COCAND` files remain available as the **isolated promotion candidates**. This document is the review-stage artifact; it creates **no new resident MVS member**, modifies no canonical source or test fixture, and authorizes no JCL submission.

**CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED.**
