# 084 — FINISH explicit QSAM CLOSE probe

Status: **PENDING TK5**. Baseline: 84/84 native regressions passed.

## Objective

Isolate explicit CLOSE of the output DCB after FINISH flushes the last
buffered output record, but before common RELMEM storage teardown.
The historical WIP source reports a previous CLOSE attempt looping
until S322 (Job 956). This is a diagnostic experiment, not a
production runtime change.

The test-only `instrument-close.py` modifies the combined generated
assembler copy and inserts:

```asm
FINRETN  CLOSE (BCPOUT)
         BAL   14,RELMEM
```

The canonical `asm/bcplmain-wip.asm` remains untouched.

START writes one character (`A`) via WRCH and executes FINISH.
Expected runtime output is exactly `A` and normal GO completion
(RC=0000). If CLOSE hangs, ABENDs, or fails assembly, retain the
IFOX listing and job report. Visible `A` without normal GO
completion does not qualify as success.

The standard regression runner limits GO to one minute. Investigate
any hang rather than running the full panel.

## Evidence limits

A pass establishes that this explicit CLOSE sequence returned normally
under TK5; it does not establish general I/O error handling, stream
closure semantics, or historical STOP behavior.
