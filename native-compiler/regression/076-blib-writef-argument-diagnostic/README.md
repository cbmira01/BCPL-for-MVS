# 076 — Diagnose historical BLIB WRITEF argument transport

## Motivation

Regression 075 exposed a real mismatch in TK5 JOB 2583:
`WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)` emitted
`C:Z S:HI N:2`, despite successful IFOX, IEWL and GO completion.
Its generated S/370 visibly puts the integer 42 into R10 before
calling G!76. This is not an accepted result.

## Diagnostic matrix

One GO runs three small calls, distinguishing conversion-sequence
side effects from positional argument loss:

- `WRITEF("A:%N", 42)`: a single integer argument
- `WRITEF("B:%N,%N,%N", 11,22,33)`: three successive numeric arguments
- `WRITEF("C:%S,%N", "HI",42)`: nested string output before integer output

Expected exact output:

```text
A:42 B:11,22,33 C:HI,42
```

Keep 075 failing until its original exact output is restored by an
evidenced correction. This test uses the persistent BLIB object,
without changing BLIB or BCPLMAIN.

## Status

**FAIL — JOB 2585 (2026-10-09 guest date).** All ASMAP, ASMRUN, LKED and GO steps RC=0000, but actual output was `A:42 B:11,22,2 C:HI,42`. The first two arguments are correct; the third argument of a single WRITEF call is replaced by `2` (33 -> 2, corroborating 075's 42 -> 2). A two-argument call after string output still succeeds. Generated caller sets R10 to 33; investigate how historical BLIB WRITEF creates and accesses its `@A` argument vector, and the CG370 procedure-entry register-save and workspace convention. Keep this regression failing as evidence.

## Validation after G!76 binding correction

**PASS** — user reran `tools/run-native-regression 75 76` after runtime commit `ab1d993`; the two tests passed, 0 failures. The originally observed third-argument truncation originated in BCPLMAIN's provisional `WRITEST` shadowing the imported historical BLIB G!76 binding. The corrected BCPLMAIN preserves BLIB's entry and uses bootstrap WRITEST only when G!76 remains unset. No CG370 or BLIB change was needed.
