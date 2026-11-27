# DR.5 — Independent reconstruction host verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Verified source revision:** `668fde85f696d7c238a656228448b059adbf2c5f`  
**Scope:** Independent, partial offline verification; no MVS execution.

## Actual test execution

Conventional Git access still fails with RC128 (could not resolve github.com). A public archive retrieval attempt also failed. Instead, the assistant reconstructed the following exact GitHub blobs in its own isolated workspace, verifying the Git blob identities before the consolidated run.

| File | Git blob |
| --- | --- |
| tools/checks/test_reconstruction_safety.py | c649df3becd057341a8bbbd0934789835dc16169 |
| tools/checks/reconstruction_fixtures.py | 1a7469839cb612bb19bc2e6767dd58e25e023d3b |
| tools/reconstruction/contract.py | c8d8850230701defd58190df60b27e10307d5aa2 |
| tools/checks/test_reconstruction_payload.py | 12c8a362f9a9e5dbf99e2da4729249318c8af9b1 |
| tools/reconstruction/verify.py | 6eaaeff43300628162eb7f0eee2a1cea3648585d |
| tools/reconstruction/run | 0fe8e1e16dbbfa019d4fbff63a89da9058dc7366 |
| tools/reconstruction/evidence.py | 2f1c098f5ed0e3b7f0874e794255d3854aaae487 |
| tools/reconstruction/coroutine_gate.py | 37249058f36a1be49d953357f4daa419dafb2aea |
| tools/reconstruction/live_entry.py | 0fe8cf22d5fc6fbe8c6d5403520c968a3b8348bb |
| tools/clean-workarea | 8369653e30175f2de5806eb1ce5157c7507cbcfa |
| tools/checks/test_reconstruction_run.py | 325bbf5de9fd60d443764601c20c1a134be2cfca |
| tools/reconstruction/plan | 0435d5a2a8f837424145529bbd5ee0549eb6042d |
| tools/reconstruction/authorize | d1a523222c97965f629faa7a695f181af0426ac4 |
| tools/checks/test_reconstruction_integration.py | b726d4b0423bd288ae5b8de9142e4587f02a1faa |

From the assistant workspace root, Python unittest discovery ran with pattern `test_reconstruction_*.py`, disabled bytecode writes, DEVNULL stdin, a 60-second bound, and TMPDIR directed beneath that workspace's workarea. Only the four copied test modules matched; this was not discovery against a complete repository.

| Module | PASS | FAIL | ERROR |
| --- | ---: | ---: | ---: |
| test_reconstruction_safety | 20 | 0 | 0 |
| test_reconstruction_payload | 16 | 0 | 0 |
| test_reconstruction_run | 16 | 0 | 0 |
| test_reconstruction_integration | 16 | 0 | 0 |
| **Total** | **68** | **0** | **0** |

Consolidated terminal receipt: 14/14 blob identities match; Ran 68 tests in 2.755s; OK; RC=0. All six formerly failing synthetic controller paths now execute to their intended success/failure oracle. The corrected operation inventory and list-only test pass; the actual cleanup CLI refuses noninteractive input in a disposable Git repository and preserves its sentinel. These are genuine Python test results, not live reconstruction or MVS acceptance.

The earlier [host reconciliation](dr5-host-test-reconciliation-20261127.md) records a separate actual MR10 coroutine-library parity test PASS and the remaining static checks. The older 954-test FAIL transcript remains historical evidence. No complete post-correction run of that suite is established.

## Focused DEBUGINT source inspection

Pinned GitHub comparison verifies that current BCPLMAIN assembler blob `061eb84cb3480bf804e66ed2ca8a24e3b3c7d369` differs from the original blob `8a4f02de4e6f2c4e02fdbbec16f53b51b53b2fa4` at commit `0fde1b7c8c7ab1e2d1f6a07e77869030f6c06a24` only by the approved LR 8,7 / LR 7,8 preservation around the minus-sign append. The six oracle records cover zero, positive 42, signed maximum, negative 1, negative 42 and signed minimum. This is source inspection, not actual execution of the DEBUGINT driver --check or native oracle.

## Remaining gates and responsibilities

The owner's explicit working instructions supersede the operator-side offline preflight assignment in [the earlier gate record](dr5-offline-verification-and-target-gates-20261127.md). The assistant owns offline verification, source changes and commits. The owner performs only necessary MVS-facing operations. Future operator evidence/logs must remain within the project root; preserve target receipts under mvs-state before destructive workarea cleanup. No workstation-only host verification is requested.

The full post-correction offline checker discovery, release tests, project coordinator check, bootstrap input check and DEBUGINT --check remain unverified. Do not represent partial results as completion of the full offline gate. The prior target sequence and no-retry write-marker requirements remain in force: focused DEBUGINT verification, review and preserve evidence, then separately authorized destructive routine reconstruction and consolidated eight-suite regression. No installed member or release artifact has been modified by this record. No new acceptance or march transition.
