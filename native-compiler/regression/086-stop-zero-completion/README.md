# 86 — Canonical STOP(0) termination

Status: **PENDING TK5 production rerun**.

START writes `S` and executes `STOP(0)` via G!30.
The canonical `asm/bcplmain-wip.asm` now installs G!30 as STOPENT.
No test-only STOP assembler insertion is used.

STOP stores its requested step completion code in static STOPRC, then
shares FINISH's buffered-output PUT, QSAM CLOSE, RELMEM, MVS register
restore and return sequence.

Expected BCPL output: `S`; expected GO RC=0000.
Regression 087 uses the runner's narrowly-scoped expected nonzero
completion rule, which requires normal ASM/LKED and matching output.

The historical return-code contract is documented in Richards'
*The BCPL Programming Manual* (November 1974), section 2.8.2:
STOP(N) terminates the job step returning completion code N.

The earlier test-local version of 86 passed under TK5; this is NOT
evidence that the newly promoted production version has passed.
Negative or out-of-range N remains outside the tested scope.
