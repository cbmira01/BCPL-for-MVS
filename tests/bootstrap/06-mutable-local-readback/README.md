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

PASS.

Job 974 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
X42
```

The regression runner reported:

```text
=== Regression result ===
TEST:        06-mutable-local-readback
OBJECTIVE:   PASS
TERMINATION: NORMAL
RESULT:      PASS
```

Generated-code inspection also satisfied the defining acceptance criterion.
The relevant sequence is:

```asm
LA 7,17(0)
ST 7,12(5)
LA 8,42(0)
ST 8,12(5)
LA 7,231(0)
LA 15,16(5)
L  4,56(12)
BALR 6,4
L  7,12(5)
LA 15,16(5)
L  4,600(12)
BALR 6,4
```

This establishes the intended state transition:

```text
initialize X
    -> mutate X to 42
    -> call WRCH using R7
    -> reload X from local workspace
    -> pass reloaded X to DEBUGINT
    -> observe X42
```

The load `L 7,12(5)` occurs after the WRCH call and immediately before the
DEBUGINT call sequence. Therefore the value printed by DEBUGINT is a real
readback of mutable local storage, not a stale value left live in R7.


### Contract established

Test 06 provides direct evidence that the generated native code correctly
supports:

- initialization of a BCPL local in the current workspace;
- assignment of a new value to that local;
- preservation of the local across an intervening BCPL global call;
- reloading the local from workspace memory;
- passing the reloaded value through the normal first-argument convention;
- reporting that value through the native diagnostic channel.

This closes the specific observability gap left by Test 05.
