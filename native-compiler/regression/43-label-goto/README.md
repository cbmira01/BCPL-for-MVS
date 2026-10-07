# 43 - label / GOTO

This regression isolates native label and GOTO generation.

Expected output:

```text
42
```

## Source shape

```bcpl
LET X = 17

GOTO ADD25

X := 99

ADD25:
X := X + 25
```

The assignment `X := 99` is deliberately unreachable if GOTO transfers to the
named label correctly.

Earlier regressions already establish local variables, assignment, integer
addition, DEBUGINT, and FINISH. Test 43 adds only explicit label/GOTO control
transfer.

## Historical motivation

The Cambridge compiler corpus uses GOTO heavily, especially in SYN/LEX and
CG370. The historical BCPL language definition also includes GOTO and labels as
core control constructs.

## Contract under test

The compiler must:

- bind the source label ADD25;
- generate an unconditional transfer to that label;
- skip the intervening assignment to 99;
- resume normal generated execution at the target label; and
- ultimately emit 42.

The assembler dump should reveal CG370's exact representation of source labels
and GOTO branches, including whether the branch is emitted as R4-relative code.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show an unconditional generated branch corresponding to `GOTO ADD25`;
- show the unreachable `X := 99` code present or optimized away without being
  executed; and
- show a concrete generated label target for ADD25.

## Status

PENDING — ready for first native run.
