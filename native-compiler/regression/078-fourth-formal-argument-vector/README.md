# 078 — Fourth formal parameter and argument-vector boundary

## Motivation

JOB 2583 (075) gave `C:Z S:HI N:2` instead of third data
argument 42. JOB 2585 (076) gave `A:42 B:11,22,2 C:HI,42`:
the third *data* argument failed, whereas the first and second
worked. Regression 077 passed `CHECK(A,B,C)` using `@A`, but
only exercised R7/R8/R9.

Historical `WRITEF(FORMAT,A,B,C,D,...)` has a leading format
parameter, so data argument C is *formal #4*, passed in R10.
We must test the fourth-formal register-to-workspace home
separately before attributing the failure to nested formatting.

## Probe

A local four-formal procedure `CHECK(FORMAT,A,B,C)` receives
`(0,11,22,33)`. It accesses `@A` as `T`, prints
`T!0`, `T!1`, `T!2`, and also prints direct formal `C`.
Expected exact output: `11 22 33 33`.

If `T!2` differs from directly referencing C, the
compiler's argument-home representation is implicated.
If both are corrupted, inspect fourth-formal transport
R10 and callee prologue. If both pass, examine historical
WRITEF's longer 12-argument prologue and workspace layout.

Uses independent application/BCPLMAIN/BLIB object linkage.
No correction or historical BLIB modification is made.

## Status

PENDING TK5 execution. 075 and 076 remain failing evidence.
