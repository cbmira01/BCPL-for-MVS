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

DEFINED. Not yet run.
