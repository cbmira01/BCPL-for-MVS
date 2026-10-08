# 077 — Address-of-formal argument vector diagnostic

## Motivation

075 actual `C:Z S:HI N:2` instead of `...N:42` (JOB 2583).
076 actual `A:42 B:11,22,2 C:HI,42` instead of
`A:42 B:11,22,33 C:HI,42` (JOB 2585).
Generated callers correctly load the third variadic value into R10.
The historical BLIB formatter uses `LET T=@A` and reads
`T!0`, `T!1`, `T!2`, etc. Suspect address-of-formal
and contiguous argument-home semantics.

## Probe

A separately compiled local procedure `CHECK(A,B,C)` computes
`T=@A`, then prints `T!0`, `T!1`, `T!2` by direct
historical BLIB `WRITEN` calls. Caller passes (11,22,33).

Expected exact output: `11 22 33`.

If the third item is `2`, the issue is demonstrable without BLIB
WRITEF's format parser and implicates generic procedure argument homes
or CG370. If it succeeds, inspect BLIB WRITEF's entry/register save
and workspace layout instead.

Uses persistent BLIB object and unmodified canonical BCPLMAIN.

## Status

**PASS** — user-executed `tools/run-native-regression 77` on TK5 (2026-10-08 local), exact output `11 22 33`; 1 PASS, 0 FAIL. This establishes three contiguous formal-argument words under `@A` for this separately compiled CHECK procedure. It does not correct or explain 075/076, which remain failing.
