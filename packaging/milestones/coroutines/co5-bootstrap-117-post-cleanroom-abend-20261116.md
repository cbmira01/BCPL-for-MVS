# CO.5 — First post-clean-room Bootstrap 117 JES failure

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** CO.5 — Integration, Regression, and Release
**Date:** 16 November 2026 (MVS/JES)
**Source revision:** `172d5c1486a69ae427e167df22f075590d7d1654` (reported run)
**Status:** FAILURE CONFIRMED; abend code and root cause not yet established
**Evidence class:** OWNER-REPORTED native runner output, not independent JES spool inspection

## Original failure, retained verbatim in the operator's evidence

The six-suite post-clean-room coordinator stopped at Bootstrap after
MR10 12 PASS. Bootstrap recorded 144 PASS, one genuine FAIL,
and the expected SKIP 083. Failure identity:

- **Case:** `117-independent-input-eof`
- **Case runner log:** `workarea/test-suites/20261116T010101Z-74571-bootstrap-production-0gtnfbor/case-117/runner.log`
- **Native case log:** `workarea/test-suites/20261116T010101Z-74571-bootstrap-production-0gtnfbor/case-117/native-logs/117-independent-input-eof.log`
- **Compiler:** JOB **6744**, System/370 assembler saved
- **Native test:** JOB **6745**, name `RG117R`
- **Observed:** `ASMAP IFOX00 RC=0000`, assembler flagged 0,
  severity 0. The job summary reported `JOB RESULT: FAILURE`,
  `HIGHEST RC: 0000`, `ABEND: detected`, `BYPASSED: one or more steps`.
- **Runner:** `record-check: link-edit authorization boundary missing`,
  native result **FAIL**, termination **ABNORMAL**.

The source for case 117 checks independent EOF state across two
named input streams (`BCPIN` and `BCPINB`). Its application was **not
observed running**: the required link-edit completion boundary and
`GO` were absent. No actual input/EOF output comparison is established
by this run. Do not recategorize the case as PASS or SKIP.

## Technical interpretation and next gate

The summary is consistent with an operational JES failure after the
application assembler step, but **does not identify the failing step,
MVS completion code or underlying cause**. It does not, by itself,
prove a BCPL source/compiler/runtime defect or a transient resource
failure.

Next, inspect the *existing* JES printer report for JOB 6745,
particularly `IEF450I`, `IEF472I`, `IEA995I`, the program/step name
and any accompanying `IEC`, `IKJ` or allocation diagnostics.
Preserve the full evidence in the operator's MVS log. Do not rerun
the 146-case Bootstrap suite or modify accepted tests before the
failure class is understood.

CO.5 clean-room reconstruction and installed coroutine GO remain PASS.
The current post-rebuild regression gate remains FAIL, and later
selected suites are NOT RUN under coordinator fail-stop. **CO.5
remains IN PROGRESS.**
