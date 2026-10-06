# 19 - Local scalar preservation across calls

This regression proves that several live local scalar values survive an
intervening BCPL function call and remain correct afterward.

The program is deliberately simple:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET ID(X) = X

LET START () BE
$(1
    LET A = 11
    LET B = 13
    LET C = 15
    LET D = ID(3)

    DEBUGINT(A+B+C+D)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Tests 16-18 established function results, nested calls, and recursion.

Test 19 focuses on caller-local scalar lifetime across a call:

```text
START
    -> establish A=11, B=13, C=15
    -> call ID(3)
    -> receive D=3
    -> use A, B, C, and D after the call
    -> compute 42
    -> DEBUGINT
```

The defining contract is that local values live across the call are
preserved correctly, whether CG370 keeps them in safe registers or spills
and reloads them from the BCPL workspace.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show A, B, and C established before the call to ID;
- show an ordinary call to ID and a returned value for D;
- show A, B, and C still participating in the arithmetic after the call;
- reveal how CG370 preserves or reloads those live local values.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test does not add a new BCPLMAIN entry convention, but it strengthens
confidence that the generated caller workspace/register discipline around
runtime calls preserves live BCPL scalar state. Machine-coded runtime
entries must not violate the already-established preserved-register and
workspace assumptions.

## Scope

This test does not introduce:

- pointer returns;
- GETVEC or FREEVEC;
- BLIB;
- unusual arithmetic operators.

Its purpose is strictly caller-local scalar lifetime across a call.

## Status

DEFINED. Not yet run.
