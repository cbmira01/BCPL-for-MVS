# DR.5 — Offline verification and remaining target gates

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed source:** `395bdc4ced06692ddd22996b18a6f9e61fc2d5f9`  
**Disposition:** Final offline PASS (see final section); remaining target evidence pending.

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

## Interrupted offline attempt and correction — 27 November 2026

At `3056c4e12f2ca37b78a5383b74684f4a28f51014` the operator preflight completed git pull RC0, then hung in unit discovery for approximately one hour. Operator interrupted with Ctrl+C; log ~/dr5-verify.hKmsR1ll/unit-tests.log identifies test_reconstruction_run.RunnerTests.test_clean_workarea_standalone_requires_terminal blocked in subprocess.communicate. Process listing after interruption contained no matching surviving unittest/tool process other than grep. No successful full offline result or DEBUGINT invocation was reported. Preserve the original log. The test inherited terminal stdin despite captured stdout/stderr; it was invoking the real workarea cleaner against the checkout and could prompt for DELETE. Never supply that confirmation to a test. This is a host test isolation defect, not a target defect.

Corrected the cleanup test to use a valid disposable Git repository with real cleaner/contract copies, a tracked marker, a sentinel, DEVNULL stdin, explicit 30-second subprocess bounds, exact RC2/interactive-terminal diagnostic and sentinel preservation checks. Related reconstruction CLI tests explicitly disconnect input for noninteractive cases and bound subprocesses (30 seconds, 60 for mocked rebuild workflows); intentional synthetic PTY tests still receive their scripted answers. No production tool behavior or MVS code changed. Local independent guard smoke used the exact cleaner blob 8369653e30175f2de5806eb1ce5157c7507cbcfa, verified by git hash-object, in a temporary Git repository with scope/deletion functions replaced by assertion-raising stubs: observed RC2, expected refusal and sentinel unchanged. This is not execution of the complete changed test modules. Local DNS still blocks full checkout. Retry only offline preflight with stdin disconnected, verbose log, visible progress and bounded timeout; proceed to DEBUGINT only after all gates pass and no prior write marker. No destructive reconstruction before receipt review.


## Final offline verification after BLIBBLD correction — 27 November 2026 EST

**Verified tested revision:** `c5b56cef0e2f9aa830a9b49631868cbc5d380b02`.  
**Evidence:** [GitHub Actions run 46087048256](https://github.com/cbmira01/BCPL-for-MVS/actions/runs/46087048256), [offline job 140798947580](https://github.com/cbmira01/BCPL-for-MVS/actions/runs/46087048256/job/140798947580). The assistant independently retrieved the completed successful job and its logs; checkout and test revision agree. Execution at 00:17 UTC on 28 November corresponds to 19:17 EST on 27 November.

| Gate | Actual result | Process RC |
| --- | --- | --- |
| Checker unit tests | 963 tests, OK | 0 |
| Release unit tests | 38 tests, OK | 0 |
| Project regression inventory | PROJECT SUITE CHECK: PASS | 0 |
| Bootstrap inputs | READY: 18 repository input paths present; no files written | 0 |
| DEBUGINT preflight | DR.5 DEBUGINT CHECK PASS (no MVS) | 0 |

Actual final summary: OFFLINE GATE FAILURES: 0. The runner also emitted a checkout-action Node.js deprecation warning; it did not fail any gate. This supersedes the earlier incomplete offline status and operator-side offline test assignment. GitHub Actions remains approved for offline verification only; hosted Docker/Hercules/MVS testing is deferred until Documentation Refactoring closes.

The [first clean-room attempt and BLIB correction record](dr5-clean-room-first-attempt-20261127.md) establishes the target failure and owner-approved correction scope. Reviewed the committed [private BLIB verification driver](../../../tools/checks/run-dr5-blib-build-verification.py) and [production BLIBBLD JCL](../../../bootstrap-toolchain/jcl/blibbld.jcl). The driver substitutes a temporary FB80 object destination (NEW,DELETE), checks the six all-prior-step zero guards, and requires compiler-report validation before RAW OPEN. DR5BLPOS uses P2000 and requires all seven steps RC0, interpreted CODE0 and two zero IFOX severity records. DR5BLNEG uses P30000 and requires interpreted CODE8 with COMP RC0, FIXASM RC8, both subsequent steps explicitly flushed, no ABEND, and one zero IFOX severity record. These are acceptance requirements, not observed target results.

Next execute the private driver once on the dedicated target, preserve complete private receipts outside workarea (authenticated decks may contain credentials), and reconcile any failure before retry. No installed object replacement is authorized. DEBUGINT native verification is already accepted at the six-record scope. After successful BLIB verification, obtain fresh destructive reconstruction authorization and conduct three distinct gates in order: unattended batch clean-room reconstruction, independent installed BOOT_OBJ/EXT_OBJ inventories, and consolidated eight-suite production regression with explicit device authorization (219 PASS, one expected SKIP 083, zero FAIL/BLOCKED). Review each gate before the next. Preserve the original failed reconstruction evidence. No DR.5 closure, DR.6 activation, new release, or native acceptance of the BLIB gate is claimed.
