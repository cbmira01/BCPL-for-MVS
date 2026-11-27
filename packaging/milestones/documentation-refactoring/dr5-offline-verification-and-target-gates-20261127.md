# DR.5 — Offline verification and remaining target gates

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed source:** `395bdc4ced06692ddd22996b18a6f9e61fc2d5f9`  
**Disposition:** Scoped offline PASS; complete offline gate and target evidence pending.

The [BCX transfer](dr5-selection-macro-authority-transfer-acceptance-20261127.md) completes the planned public reference authority transfers, with retained qualifications. Owner directed offline verification followed by remaining MVS operations.

## Actual independent host execution

A fresh conventional Git remote inquiry failed RC128 (could not resolve github.com). No local full checkout, no existing GitHub Actions workflow, and no MVS connection. Retrieved exact source/test text through pinned GitHub reads, reconstructed only the following six files in a disposable independent workspace, verified each Git blob hash with git hash-object before running Python unittest discovery. All six matched:

| File under tools/checks | Git blob |
| --- | --- |
| check-r5-extension-report.py | 94a0abb2eadca4a5c878bfdf3cb3052e1e3b6ed7 |
| test_r5_time_absence.py | 275e9c1b559dde8df9f40b22c100f776eab19580 |
| check-asm-source.py | 7ca419e176a7e44190164e7e6369ffe2b8b25e0c |
| test_check_asm_source.py | d4c6d90dc4d6103a84c4a64a7919c2f341419a39 |
| check-bcpltime-t0-report.py | 2ca616dbaacc50c94261179c2594ede501be7c14 |
| test_check_bcpltime_t0_report.py | d926c04b2fa57152b88684af4dc2a82d10cda720 |

Actual command in that isolated six-file workspace: python3 -B -m unittest discover -p 'test_*.py' -v. **14 tests, all PASS**, including six assembler name-field tests, four TIME selected-link parser tests and four R.5 TIME-exclusion parser tests. These are actual checked-in test executions against byte-identical copies, not fresh MVS/IFOX/IEWL results or a full repository test run.

## Independent pinned inventory verification

Read all five native TSVs and paired coroutine manifest from the same Git revision and checked directory/runner/oracle path existence against the untruncated tree, IDs, profile strings, policy values and counts. 201 native rows, 201 distinct numeric IDs 00–200 inclusive, no missing IDs or directory lookup errors. Counts 150/17/4/17/13. Only nonstandard policies: 083 skip-installed, 175/176 device-opt-in. Both paired coroutine runner/oracle paths exist. This is independent static inspection, not execution of the official run-suite validator. Retain the earlier [manual navigation audit](dr5-documentation-navigation-and-reconciliation-audit-20261127.md), incomplete inbound dependency qualification and DR.4 transformation-test deferral.

## Remaining verification order

1. On the operator checkout, as a preflight to the authorized focused MVS operation, synchronize exact current main, require clean tracked state, run the [official host checker discovery](../../../tools/checks/README.md), [release offline tests](../../../tools/distribution/How-to-Create-a-Release-Candidate.md), [project manifest check](../../../tools/tests/README.md), bootstrap input check and DEBUGINT --check. Preserve logs outside workarea so a later clean-room cleanup cannot remove them. Stop on nonzero status; no claim of results until received.
2. Run the previously authorized [DEBUGINT verification driver](../../../tools/checks/run-dr5-debugint-verification.py) --rebuild-and-verify only if no prior write attempt requires reconciliation. Actual installed baseline, private candidate, guarded source/object staging and installed oracle must pass. Retain actual result.json and full logs, especially on failure. If an earlier write marker/result exists, review before another execution; no automatic retry. Six expected decimal records in the [fixture oracle](candidates/debugint-verification/expected.txt). No new MVS evidence obtained in this record.
3. After review/preservation of focused receipts, separately authorize destructive routine [clean-room reconstruction](../../../docs/project/How-to-Reconstruct-BCPL-from-Source.md) and device-opt-in consolidated eight-suite production regression. Expected 219 PASS, 0 FAIL/BLOCKED, one expected SKIP 083; do not add overlapping historical diagnostics. Retain complete actual receipts, verify revision and installed inventory. No release production or guarded-controller integration acceptance implied.

No new code, oracles, release bytes or MVS state changed. No DR.5 closure or DR.6 activation. Full checkout-dependent offline verification is not established by the scoped test results.
