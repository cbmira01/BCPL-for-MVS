# 46 - multiply / divide / REM

This regression isolates native generation for BCPL multiplication, integer
division, and remainder.

Expected output:

```text
42
```

## Source shape

```bcpl
LET A = 6 * 7
LET B = 43 / 6
LET C = 43 REM 6

DEBUGINT(A + B - C - 6)
```

Earlier regressions already establish local scalars, addition/subtraction,
DEBUGINT, and FINISH. Test 46 adds:

- multiplication;
- integer division;
- remainder.

## Expected evaluation

```text
A = 6 * 7      = 42
B = 43 / 6     = 7
C = 43 REM 6   = 1

A + B - C - 6  = 42
```

The operands are deliberately small positive integers so this test isolates the
basic operator implementation rather than sign, overflow, or divide exception
semantics.

## Historical motivation

Multiply, divide, and REM are core BCPL arithmetic operators in the historical
language definition and are handled directly by the Cambridge code generator.

## What to inspect in generated assembler

The generated System/370 should reveal CG370's exact implementation strategy for:

- multiplication;
- integer quotient;
- remainder;
- any required register pairing or sign extension.

Particular attention should be paid to whether division uses the System/370
even/odd register-pair convention and whether quotient/remainder are selected
directly from the architectural result registers.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show native code corresponding to multiply, divide, and REM;
- require no new BCPLMAIN runtime service.

## Status

PENDING — ready for first native run.
