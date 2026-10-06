# 16 - Function return value

This regression proves the native BCPL function-result convention.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET ADD(A,B) = A+B

LET START () BE
$(1
    LET X = ADD(17,25)

    DEBUGINT(X)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Tests 13 through 15 established BCPL argument registers R7-R10.

CGHDR also identifies R7 as the function-result register. Test 16 verifies
that live call/return behavior directly:

```text
START
    -> call ADD(17,25)
ADD
    -> receive A and B
    -> compute A+B
    -> return the result
START
    -> consume the returned value
    -> DEBUGINT
    -> observe 42
```

The defining contract is that an ordinary BCPL function returns its result in
the register/state expected by generated caller code.

## Expected linkage evidence

Based on CGHDR, the expected result convention is:

```text
function result -> R7
```

This is an expectation to be verified from generated S/370.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show ADD receiving A and B through the established argument convention;
- show ADD placing the computed result in R7 before ordinary BCPL return;
- show START consuming the returned R7 value after the call;
- show that value being passed to DEBUGINT.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test establishes the return-value side of the native BCPL calling
convention. Machine-coded runtime functions that return a BCPL value must
place that value in R7 before returning through the ordinary BCPL linkage.

## Scope

This test does not introduce:

- nested calls from inside ADD;
- recursion;
- pointer returns;
- GETVEC or FREEVEC;
- BLIB.

Those remain later regression steps.

## Status

PASS.

Job 996 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the function-result convention.

ADD receives A in R7 and B in R8, computes the sum in R8, then explicitly
moves the function result into R7 before returning:

```asm
STM 4,8,0(15)
LR 5,15
AR 8,7
LR 7,8
BCR 15,11
```

The caller prepares the two arguments, calls ADD, and immediately stores the
returned R7 value into local X:

```asm
LA 8,25(0)
LA 7,17(0)
LA 15,12(5)
L  4,0+L2-L4(4)
BALR 6,4
ST 7,12(5)
```

START then passes that saved result to DEBUGINT, which emits 42.


### Contract established

Test 16 establishes the function-result side of the native CG370 calling
convention:

```text
function result -> R7
```

Together with Tests 13-15, R7 is now proven to serve both as argument 1 on
function entry and as the returned BCPL value on function exit.

This is directly relevant to machine-coded BCPLMAIN/runtime functions:
a native routine returning a BCPL value must place that value in R7 before
returning through the ordinary BCPL linkage.
