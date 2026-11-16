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

## MVS JES completion-code follow-up: SB2D

The owner obtained a focused extract from existing JOB 6745 JES SYSOUT,
confirming the failing step and completion code:

```text
RG117R ASMAP IFOX00 RC= 0000
IEC999I IFG0TC0A,IFG0TC0B,RG117R,LKED,DEB ADDR=99B494
IEC999I IFG0TC0A,IFG0TC0B,RG117R,LKED,DEB ADDR=99B030
IEC999I IFG0TC0A,IFG0TC0B,RG117R,LKED,DEB ADDR=99B50C
IEC999I IFG0TC0A,IFG0TC0B,RG117R,LKED,DEB ADDR=99B2D0
IEF450I RG117R LKED - ABEND SB2D U0000
RG117R LKED IEWL AB SB2D
RG117R GO PGM=*.DD *FLUSH*
IEF472I RG117R LKED - COMPLETION CODE - SYSTEM=B2D USER=0000
IEF272I RG117R GO - STEP WAS NOT EXECUTED.
```

IBM's *OS/VS Message Library: VS2 System Codes*, GC38-1008-9
(December 1984), defines **B2D** as a program check during FETCH
ESTAE processing when loading a segment of an overlay program.
Reference: https://manualzz.com/doc/22379714/ibm-vs2-system-codes-os-vs-message-library-manual
The `IEC999I IFG0TC0A/IFG0TC0B` messages correspond to OPEN/CLOSE/EOV
or task-close processing (see IBM's `IEC999I` reference:
https://www.ibm.com/docs/en/zos/2.5.0?topic=messages-iec999i).
The messages alone do not establish whether the initial cause was
a damaged overlay, an intermittent MVS FETCH issue, or another
system condition.

**Disposition:** The test's BCPL EOF logic was never executed;
the system abend occurred in IEWL before GO. This is a real FAIL
of the complete regression attempt, but not a demonstrated BCPL
behavioral defect. A **single focused MVS rerun of case 117**
is justified as the next discriminating test. If SB2D repeats,
investigate the IEWL overlay load and environment using the
new job report; do not alter BCPL code or expected output.

## Technical interpretation and next gate

The summary is consistent with an operational JES failure after the
application assembler step, but **does not identify the failing step,
MVS completion code or underlying cause**. It does not, by itself,
prove a BCPL source/compiler/runtime defect or a transient resource
failure.

The original failed JES report has now been examined far enough to
identify the B2D overlay FETCH abend at `LKED`. Obtain a focused
case-117 repeat using `tools/tests/run-suite bootstrap --run --profile
production --case 117`. Preserve any new JES report and distinguish
PASS after retry from the original irreversible FAIL. Do not rerun
all 146 Bootstrap cases or modify expected outputs on speculation.

CO.5 clean-room reconstruction and installed coroutine GO remain PASS.
The current post-rebuild regression gate remains FAIL, and later
selected suites are NOT RUN under coordinator fail-stop. **CO.5
remains IN PROGRESS.**
