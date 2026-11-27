# DR.5 — Host test reconciliation

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026  
**Failed offline campaign revision:** `7c8586eff1387292877699e167b8461d1ba709f6`  
**Test-only correction revision:** `3801d800ac02caf1c87568b5ae3b99d45cf3b388`

## Observed campaign

The owner supplied the complete host unittest transcript: 954 tests in 22.237 seconds, 12 failure reports and 7 errors. The unit-test gate stopped the subsequent release, coordinator, bootstrap-input and DEBUGINT preflight gates. No new native acceptance is inferred. Preserve the failing transcript; the subsequent correction is not a replacement receipt.

## Reconciliation

| Affected module | Reports | Correction |
| --- | ---: | --- |
| test_co2_native_changeco | 1 | Stage the exact tracked BCPLCO bridge in the synthetic driver's disposable root. |
| test_co5_production_coroutines | 1 | Compare every non-comment assembler card against the accepted CO.3 merge; retain card width and unique entry checks. |
| test_mr10_canonical_coroutine_promotion | 1 | Require the exact later owner-approved RESUMECO check-before-clear repair and preserved candidate equality. |
| test_project_regressions_mr10_probes | 1 | Require exact inventory membership and isolation, distinct from the CLI's explicit SUITES execution order. |
| test_q2_numbered_regression | 5 | Expand fixture parity and deck checks to cases 198–200 in private-diagnostic mode, and reject missing evidence and wrong modes. |
| test_r5_install_jcl_member | 1 | Inspect the authoritative reconstruction manual and preserve individual resident submission/readback and obsolete-path exclusions. |
| test_reconstruction_integration | 6 | Supply the exact observed ICINT19 scalar/vector result and CODE=0 in the synthetic controller fixture. |
| test_reconstruction_run | 2 | Include the two coroutine build jobs; directly assert that list mode never invokes execution, authorization, JES guard or subprocesses. |
| test_reconstruction_safety | 1 | Require the 31-operation manifest, six coroutine stages and absence of regression/release operations. |
| **Total** | **19** | |

The nine changes are exclusively host test modules; no BCPL, assembler, JCL, release artifact, installed-object, runner, or historical candidate bytes were modified. The native bridge comparison against the CO.6 tested revision `216b6707c404a91c796ed8f1419a99ef172b184a` confirms that both bridge files differ only in full-card comments. The MR10 canonical/candidate changes are exactly the owner-approved reorder in `723c3887b3b732dfa457c169c82e9849b9400b24`, and both sources match the CO.6 tested revision.

## Verification actually completed

- Assistant-side connector inspection: exact native non-comment CO.3 merge parity; exact MR10 repair parity; 31 canonical operations and both coroutine payload mappings; list dispatch returns before live execution; coordinator executes in SUITES order; authoritative manual commands and obsolete-path exclusions; all 17 BCPLQSAM canonical source blob identities, required fixture presence, and independent reader source parity for 168.
- Assistant workspace: the corrected MR10 coroutine-library parity unittest ran and passed (1 test). Its complete test module and three BCPL source files were independently reconstructed in the assistant's workspace and matched the four Git blob identities at the correction revision before execution.
- Full local checkout and complete Python suite remain unverified: conventional Git access from the assistant workspace fails DNS resolution. GitHub connector access is available, but a full local repository could not be obtained. No claim that the 954-test suite passes or that all downstream synthetic integration checks have executed.

## Gates remaining

The assistant owns offline verification; the owner performs only MVS-facing operations. Do not delegate offline tests, host edits or patching to the owner. This note does not grant new MVS mutation or clean-room approval. The prior [offline verification and target gates](dr5-offline-verification-and-target-gates-20261127.md) remain in force. No DEBUGINT staging, clean-room reconstruction or full native campaign was attempted by these corrections. DR.5 remains IN PROGRESS; DR.6 remains NOT STARTED.
