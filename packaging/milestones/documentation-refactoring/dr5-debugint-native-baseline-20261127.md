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
