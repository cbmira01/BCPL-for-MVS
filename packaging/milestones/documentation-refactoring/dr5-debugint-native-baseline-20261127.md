# DR.5 — DEBUGINT native baseline reproduction and private link-edit failure

**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Target source revision:** `7720c820a425b59a8acc7474e3e4c61073d944db`  
**BCPLMAIN SHA-256:** `dfaaf6882ce42086cbcbbfccc9c43fe7296b186f54777ba849606b79db18e879`  
**Attempt:** `workarea/dr5-debugint/run-zo69cmat` (operator wrapper preserves a copy under `mvs-state/dr5-debugint/`).

## Actual owner-reported MVS results

Driver RC1, status FAIL, stage private-candidate. Compiler JOB 1305 completed successfully. Installed baseline JOB 1306 produced the following exact records:

```text
RP: DR5 DEBUGINT ZERO 0
RP: DR5 DEBUGINT POS 42
RP: DR5 DEBUGINT MAX 2147483647
RP: DR5 DEBUGINT NEG1 -680968
RP: DR5 DEBUGINT NEG42 -680968
RP: DR5 DEBUGINT MIN -680968
```

All positive/zero controls match the oracle. The three negative operands produce an identical erroneous value, consistent with the source-confirmed R7 clobber in DBGAPND. The driver reports semantic status FAIL (negative operand defect reproduced).

Private candidate RG906R JOB 1307: ASMAP IFOX00 RC0000; ASMNAT IFOX00 RC0000; LKED IEWL RC0008; no GO or application records reported. The reason is not yet established; the retained IEWL diagnostics are required. The driver stopped at private-candidate, before its source staging, writes-started marker creation or installed-object replacement path. This is a failed private link-edit, not a failed execution of the corrected DEBUGINT arithmetic.

## Next action

Inspect the retained JOB 1307 IEWL messages/map in candidate/RG906R-report.log. Do not replay the driver, modify the installed baseline, infer a successful private candidate, or begin clean-room reconstruction. The assistant will reconcile the actual IEWL evidence and test any correction before promotion. The previous all-five-gate offline PASS remains valid at its recorded tested revision. No additional product change or acceptance is made by this record.

## IEWL evidence and correction

The owner supplied the retained JOB 1307 diagnostic: IEW0132 NATIVEAD, unresolved external reference at application location 1B4, and IEW0432 SYSLIB, library cannot be opened (DD may be missing). The existing regression builder's --native option explicitly injects EXTRN NATIVEAD and a G!151 address entry into the generated application, intended for separate native-global routines. BCPLMAIN does not define NATIVEAD. The original DEBUGINT driver inadvertently invoked that option to assemble its private runtime replacement. The unresolved reference, and consequent library search, are consistent with IEWL's report. Adding SYSLIB or a dummy NATIVEAD would mask the actual deck defect and would change application linkage semantics.

The corrected driver builds the ordinary installed-object application deck without --native, then inserts a separately assembled private BCPLMAIN object in the SYSLIN concatenation, removing only INCLUDE OBJ(BCPLMAIN). All installed service selections, entry point and application cards remain unchanged. Both assembler steps and link-edit must succeed before GO. No production assembler, BCPL or historical generator behavior is changed. Assistant-local tests of the exact proposed private_cards function passed three test methods covering ordinary application preservation, absence of NATIVEAD, private concatenation, conditional execution, rejection of invalid source/deck and repeat transformation. Added regression tests invoke the real ordinary deck builder with synthetic configuration and the driver with mock transport; full hosted verification requested. The former MVS attempt remains preserved; no writes were reached. No new native acceptance is claimed until the corrected private candidate executes and the installed oracle passes.

## Post-correction offline gate and controlled retry

[GitHub Actions run 46068037762](https://github.com/cbmira01/BCPL-for-MVS/actions/runs/46068037762), job 140737998635, completed SUCCESS at `535f0de379d045b6f048a8befc5b4cab995ba972`. Actual log receipts: checker discovery ran 957 tests in 29.774 seconds, RC0; release discovery ran 38 tests in 0.987 seconds, RC0; coordinator check PASS RC0; bootstrap input check READY (18 paths), RC0; DEBUGINT check PASS (no MVS), RC0. OFFLINE GATE FAILURES: 0. This includes the three new private-runtime deck tests. The owner explicitly deferred Docker/MVS execution on GitHub Actions until after Documentation Refactoring; hosted verification remains offline only.

The owner authorized proceeding. The failed first attempt is reconciled at its reported pre-write stage, and one fresh corrected --rebuild-and-verify invocation may proceed only with the preserved run-zo69cmat result, no additional attempt directories in workarea or mvs-state, and no writes-started marker in either copy. The same six-record oracle and pre-write candidate gate remain in force. The shell wrapper preserves newly created evidence without overwriting the prior attempt. Assistant-workspace Bash syntax and synthetic success, driver-failure, prior-marker refusal, additional-attempt refusal and missing-prior-evidence refusal checks all passed. The retry may repeat the baseline to confirm the installed state before any write. Do not replay if it fails, and do not begin clean-room reconstruction before reviewing actual receipts. This evidence-only commit does not alter the verified driver, fixtures, tests or workflow.

## Corrected private and installed target verification — PASS

Owner-reported actual driver output at `af69764964303095b6d930c61ebd63aad593f6d5`, `workarea/dr5-debugint/run-c2qfuajf`, preserved by the wrapper under `mvs-state/dr5-debugint/run-c2qfuajf`: status PASS, stage complete, driver RC0. BCPLMAIN source SHA-256 `dfaaf6882ce42086cbcbbfccc9c43fe7296b186f54777ba849606b79db18e879`, unchanged from the first attempt. The accepted baseline JOB 1309 independently reproduced the same six records as JOB 1306, including the three erroneous -680968 values. Compiler JOB 1308 passed. Private JOB 1310 passed the IFOX/IEWL/GO gate and exact oracle. Guarded source staging and source read-back completed; installation JOB 1313 passed the driver-required ASMMN/PUTMN/RDMN/VFMN steps (IFOX, IEBGENER, IEBGENER, IEBCOMPR). Installed JOB 1314 passed the IFOX/IEWL/GO gate and the same independent oracle. Both private and installed records were exactly:

```text
RP: DR5 DEBUGINT ZERO 0
RP: DR5 DEBUGINT POS 42
RP: DR5 DEBUGINT MAX 2147483647
RP: DR5 DEBUGINT NEG1 -1
RP: DR5 DEBUGINT NEG42 -42
RP: DR5 DEBUGINT MIN -2147483648
```

Accept the focused two-card signed-operand correction at its tested scope under the prior owner authorization D. Do not claim generalized formatting, truncation handling, stream-selection behavior or additional register preservation from these six records. G!150 remains provisional, detailed DEBUGINT behavior remains outside the C normative transfer, and the historical FORMTREE:150 conflict remains unresolved. No new numbered regression is assigned. The manual's investigation status is updated to observed verification, not a new authority transfer. Raw private JES reports have not been independently reopened; the supplied driver receipt is the actual target evidence. Both attempts must be retained under mvs-state before workarea cleanup. Do not replay DEBUGINT after installation. The next gate is separately owner-authorized unattended clean-room reconstruction followed by device-opt-in eight-suite regression (219 PASS, one expected SKIP 083, no FAIL/BLOCKED). No release work or DR.6 transition is implied.
