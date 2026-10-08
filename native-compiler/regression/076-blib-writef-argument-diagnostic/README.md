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

PENDING TK5 diagnostic execution.
