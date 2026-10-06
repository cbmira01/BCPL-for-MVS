# 07 - Global-vector state and visibility

This regression proves that user BCPL global state is stored through the
global vector and remains visible across an ordinary BCPL procedure call.

The program is deliberately small:

```bcpl
GLOBAL $( START:1; DEBUGINT:150; X:151 $)

LET SHOWX () BE
$(1
    DEBUGINT(X)
$)1

LET START () BE
$(1
    X := 42
    SHOWX()
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Tests 05 and 06 established scalar diagnostic output and mutable local
workspace state.

Test 07 moves the state into the BCPL global vector and observes it from a
different BCPL procedure:

```text
START
    -> store 42 in global X
    -> call SHOWX
SHOWX
    -> read global X through G
    -> pass X to DEBUGINT
    -> observe 42
```

This is the first regression whose defining contract is user global-vector
state rather than local workspace state.

## Global assignment

G!150 is already reserved provisionally for DEBUGINT instrumentation.

For this regression, X is assigned G!151 so it is adjacent to, but distinct
from, the diagnostic hook. The purpose is not to claim a historical global
number for X; it is a private regression-program global chosen outside the
recovered library assignments used so far.

At four bytes per global, generated code should reference X at displacement
604 from R12.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated S/370 that stores X through R12/global-vector addressing;
- show generated S/370 in SHOWX that reloads X through R12 before calling
  DEBUGINT.

The generated-code inspection is part of the proof. The test is intended to
establish actual global-vector state and cross-procedure visibility, not just
an output coincidence.

## Scope

This test does not introduce:

- vectors;
- arithmetic;
- BLIB;
- WRITEN or WRITEF;
- dynamic loading;
- general stream selection.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
