# 22 - Signed arithmetic

This regression proves basic signed integer arithmetic in generated native
code without relying on DEBUGINT's negative-number formatting path.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET START () BE
$(1
    LET A = 17
    LET B = 25

    A := -A
    DEBUGINT(B-A)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Earlier tests used positive integer arithmetic, but they did not isolate
runtime signed negation.

Test 22 requires:

```text
A = 17
A := -A        -> -17
B = 25
B - A          -> 25 - (-17) = 42
```

The key point is that A is first established as a positive local and only
then negated. This is intended to force generated runtime signed arithmetic
rather than merely encoding a negative literal.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show A established as positive 17;
- show generated runtime code negating A;
- show subsequent arithmetic using the negative value to compute 42;
- show the final value reaching DEBUGINT.

Generated-code inspection is part of the proof.

## Diagnostic note

This test deliberately emits a positive final value. DEBUGINT's negative
formatting path is provisional and has not yet been established as correct.
A later dedicated diagnostic test can exercise negative decimal output
without conflating that implementation with CG370 signed arithmetic.

## Scope

This test covers:

- signed unary negation;
- signed addition/subtraction behavior involving a negative operand.

It does not yet attempt to cover:

- signed comparisons;
- multiplication or division;
- overflow behavior;
- negative DEBUGINT output.

Those remain separate regression targets.

## Status

PASS.

Job 1010 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the signed-arithmetic behavior directly.

START establishes A=17 and B=25 as ordinary positive locals:

```asm
LA 7,17(0)
ST 7,12(5)
LA 8,25(0)
ST 8,16(5)
```

CG370 then negates A at runtime with the signed two's-complement instruction:

```asm
LCR 7,7
ST 7,12(5)
```

R7 therefore becomes -17.

The subsequent subtraction is:

```asm
SR 8,7
LR 7,8
```

With R8=25 and R7=-17, `SR 8,7` computes 25-(-17)=42.  The result is moved
to R7 and passed to DEBUGINT.


### Contract established

Test 22 establishes basic signed integer arithmetic in generated native code:

- unary negation of a runtime value uses signed two's-complement semantics;
- the generated code uses `LCR` to form -A;
- subtraction uses ordinary 32-bit signed register arithmetic;
- a negative operand participates correctly in later arithmetic;
- the resulting positive value is returned through the ordinary R7 value
  path to DEBUGINT.

This test deliberately does not prove negative decimal formatting in
DEBUGINT; that remains a separate diagnostic-runtime concern.
