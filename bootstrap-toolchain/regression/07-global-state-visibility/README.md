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

PASS.

Job 978 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

The regression runner reported:

```text
=== Regression result ===
TEST:        07-global-state-visibility
OBJECTIVE:   PASS
TERMINATION: NORMAL
RESULT:      PASS
```

Generated-code inspection had already established the defining global-vector
operations for X = G!151:

```asm
ST 7,604(12)
...
L  7,604(12)
```

The store occurs in START. The load occurs in SHOWX before the DEBUGINT call.
Therefore the observed 42 is direct evidence of user global-vector state
remaining visible across an ordinary BCPL procedure call.


### Job 976 startup diagnosis

The first native run assembled and link-edited cleanly but GO returned
RC=0016 before START executed.

The generated module was correct for the intended test:

```asm
L  7,604(12)
...
ST 7,604(12)
```

G!151 is byte displacement 604 from R12. The generated module trailer also
advertised 604 as its maximum global displacement.

BCPLMAIN, however, still limited its static bootstrap global vector to
G!0..G!150 and rejected any module whose maximum global displacement exceeded
600 bytes. Test 07 therefore took the deliberate GTOOBIG startup exit and
returned 16.

The regression was not weakened by moving X to a lower global. Instead, the
bootstrap global-vector allocation was extended to G!0..G!200 so that user
globals beyond FIRSTFREEGLOBAL can be exercised while dynamic global-vector
sizing remains unreconstructed.

Test 07's BCPL source remains unchanged.


### Contract established

Test 07 provides direct evidence that generated native BCPL correctly
supports:

- writing a user-defined global through R12/global-vector addressing;
- preserving that global state across an ordinary BCPL procedure call;
- reading the same global from another BCPL procedure;
- passing the reloaded global value through the ordinary first-argument
  convention;
- observing the value through DEBUGINT.

For X = G!151, the expected byte displacement is 4*151 = 604, and the
generated S/370 uses that exact displacement for both store and load.

The first run, Job 976, also exposed a bootstrap-runtime capacity defect:
BCPLMAIN still allocated only G!0..G!150 and rejected the module through
GTOOBIG. Extending the provisional static global vector through G!200 allowed
the unchanged Test 07 source to execute successfully in Job 978.

Dynamic global-vector sizing remains future BCPLMAIN reconstruction work.
