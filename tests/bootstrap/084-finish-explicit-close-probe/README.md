# 084 — Canonical FINISH flush and explicit CLOSE

Status: **PENDING TK5 rerun after production promotion**.

Regression 084 first passed under TK5 as a test-only insertion of
`CLOSE (BCPOUT)`, with output `A`. The successful probe justified
promoting that sequence to `asm/bcplmain-wip.asm`.

084 now exercises **canonical** FINIMPL with no injected assembler.
START calls WRCH('A'), then FINISH. The runtime must PUT the pending
record, CLOSE BCPOUT, reclaim its storage, and return to MVS.
Expected output: `A`, with normal GO completion.

Compare 085, which exercises FINISH with no pending output.

The original isolated instrumenter `instrument-close.py` is retained
as historical diagnostic evidence, but is no longer invoked by the
regression runner. Never inject a second CLOSE into canonical code.

S322 or abnormal GO completion is a failure for 084.
