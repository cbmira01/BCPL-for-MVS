# 06 - Mutable local state readback

This regression proves that a BCPL local can be changed after initialization
and that the changed value can subsequently be observed through the native
diagnostic channel.

The source deliberately avoids arithmetic, vectors, library formatting, and
other new facilities:

```bcpl
LET X = 17

X := 42
WRCH('X')
DEBUGINT(X)
```

Expected output:

```text
X42
```

## Purpose

Test 05 established that a scalar value can reach DEBUGINT, but its value may
have remained live in R7 from the code that created it.

Test 06 closes that gap. It requires:

```text
local initialization
    -> local mutation
    -> intervening global call using R7
    -> read current X
    -> pass X to DEBUGINT
    -> observable output
```

The intervening `WRCH('X')` call is intentional. It consumes the normal
first BCPL argument register before `DEBUGINT(X)`, making the subsequent
value of X a meaningful readback test rather than merely observing an
unchanged argument register.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `X42`;
- show, on inspection of the generated S/370, that the value supplied to
  DEBUGINT is obtained after the intervening WRCH call rather than simply
  relying on the old value formerly held in R7.

The final generated-code inspection is part of the regression evidence
because this test exists specifically to distinguish stored mutable state
from a still-live register value.

## Scope

This test does not introduce:

- arithmetic;
- vector allocation or indexing;
- BLIB;
- WRITEN or WRITEF;
- general stream selection.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
