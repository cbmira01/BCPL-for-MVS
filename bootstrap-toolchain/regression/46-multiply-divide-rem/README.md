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

## Observed generated convention

The first native run passed with output `42`.

CG370 emitted multiplication directly with `MH`:

```asm
 LA 7,7(0)
 MH 7,0+L997-L1(4)
 ST 7,12(5)
```

with the halfword constant pool containing 6.

For integer division, CG370 loaded the dividend into R6, sign-extended it across
the even/odd pair R6:R7 with `SRDA 6,32(0)`, then divided by the fullword
constant 6:

```asm
 LA 6,43(0)
 SRDA 6,32(0)
 D  6,0+L996-L1(4)
 ST 7,16(5)
```

After System/370 `D`, the quotient is in the odd register R7 and the remainder
is in the even register R6. The quotient path therefore stores R7.

REM uses the same divide sequence but stores R6 instead:

```asm
 LA 6,43(0)
 SRDA 6,32(0)
 D  6,0+L996-L1(4)
 ST 6,20(5)
```

The final expression reuses the live remainder in R6:

```asm
 L  7,16(5)
 A  7,12(5)
 SR 7,6
 AH 7,2+L997-L1(4)
```

where the halfword constant pool contains `-6`.

No BCPLMAIN runtime support was required.

## Status

PASS — emitted `42` on 2026-10-07.
