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

PASS.

Job 1002 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection shows exactly how CG370 preserves the live caller
locals across the call.

Before calling ID, START stores A, B, and C into its workspace:

```asm
LA 7,11(0)
ST 7,12(5)
LA 8,13(0)
ST 8,16(5)
LA 9,15(0)
ST 9,20(5)
```

It then calls ID(3), and saves the returned R7 value as D:

```asm
LA 7,3(0)
LA 15,24(5)
L  4,0+L2-L4(4)
BALR 6,4
ST 7,24(5)
```

After the call, START reloads the pre-call locals from its workspace and
combines them with the still-live returned value in R7:

```asm
L  8,16(5)
A  8,12(5)
A  8,20(5)
AR 8,7
LR 7,8
```

Thus A, B, and C survive the call through workspace spill/reload, while D is
returned in R7 and also stored to its local slot.


### Contract established

Test 19 establishes caller-local scalar lifetime across an ordinary BCPL
function call.

Specifically:

- live locals A, B, and C are stored in the caller workspace before the
  call;
- the callee uses its own workspace;
- the caller's R5 workspace remains valid after return;
- the returned function value arrives in R7;
- the caller reloads its pre-call locals from workspace and combines them
  with the returned value correctly.

This strengthens the evidence that machine-coded runtime calls must preserve
the BCPL workspace/linkage contract so generated callers can safely reload
live state after return.
