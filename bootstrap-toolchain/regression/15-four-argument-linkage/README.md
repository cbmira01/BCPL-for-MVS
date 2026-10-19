# 15 - Four-argument BCPL linkage

This regression completes the basic A1-A4 calling-convention evidence by
extending the native linkage from three arguments to four.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET SET4(V,I,X,Y) BE
$(1
    V!I := X+Y
$)1

LET START () BE
$(1
    LET V = VEC 2

    V!1 := 17
    SET4(V,1,40,2)
    DEBUGINT(V!1)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 14 established:

```text
argument 1 -> R7
argument 2 -> R8
argument 3 -> R9
```

CGHDR names R10 as A4. Test 15 is intended to prove that live call-time
mapping directly:

```text
START
    -> create local vector
    -> initialize V!1 = 17
    -> call SET4(V,1,40,2)
SET4
    -> receive V as argument 1
    -> receive I as argument 2
    -> receive X as argument 3
    -> receive Y as argument 4
    -> compute X+Y
    -> compute V!I
    -> store the sum through the computed address
    -> return
START
    -> reload V!1
    -> DEBUGINT
    -> observe 42
```

The defining contract is that all four BCPL arguments cross the procedure
boundary intact and are available to generated callee code.

## Expected linkage evidence

Based on CGHDR and the previous regressions, the expected register mapping is:

```text
argument 1 -> R7
argument 2 -> R8
argument 3 -> R9
argument 4 -> R10
```

R10 is an expectation to be verified from generated S/370.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show the caller carrying V, I, X, and Y in the generated four-argument
  call state;
- establish the register used for argument 4;
- show the callee using X and Y to produce the stored value;
- show the callee using V and I to compute the target element address;
- show the caller independently reloading V!1 after return.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test is directly relevant to the native runtime calling convention.
If R10 is confirmed as argument 4, machine-coded BCPLMAIN/runtime entries
that accept four BCPL arguments must interpret R7-R10 as A1-A4 while
preserving the surrounding BCPL linkage contract.

## Scope

This test does not introduce:

- five or more argument linkage;
- function return values;
- GETVEC or FREEVEC;
- BLIB;
- heap allocation.

The immediate purpose is to close the A1-A4 argument-register evidence.

## Status

PASS.

Job 994 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the four-argument register convention.

The caller prepares all four arguments immediately before the call:

```asm
LA 10,2(0)
LA 9,40(0)
LA 8,1(0)
L  7,12(5)
LA 15,28(5)
L  4,0+L2-L4(4)
BALR 6,4
```

Thus, for `SET4(V,1,40,2)`:

```text
R7  = V
R8  = I
R9  = X
R10 = Y
```

The callee entry preserves through R10 and uses all four incoming arguments:

```asm
STM 4,10,0(15)
LR 5,15
AR 10,9
AR 8,7
AR 8,8
ST 10,0(8,8)
BCR 15,11
```

R10+R9 computes Y+X = 42.  R8+R7 forms the BCPL word address V+I;
doubling R8 and using `0(8,8)` converts that word address to the native
byte address.  The callee stores the computed value from R10 through that
address.

After return, START independently reloads V!1 and observes 42 through
DEBUGINT, confirming all four arguments were interpreted correctly.


### Contract established

Test 15 completes the basic A1-A4 argument-register evidence for the native
CG370 calling convention:

```text
argument 1 -> R7
argument 2 -> R8
argument 3 -> R9
argument 4 -> R10
```

A generated four-argument callee preserves the incoming argument set with
`STM 4,10,0(15)` and may use R7-R10 directly on entry.

This is directly relevant to machine-coded BCPLMAIN/runtime primitives:
a native four-argument primitive must interpret R7-R10 as A1-A4 while
preserving the surrounding BCPL linkage contract.
