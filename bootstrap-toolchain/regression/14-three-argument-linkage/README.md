# 14 - Three-argument BCPL linkage

This regression extends the native calling-convention evidence from two
arguments to three arguments.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET SET(V,I,X) BE
$(1
    V!I := X
$)1

LET START () BE
$(1
    LET V = VEC 2

    V!1 := 17
    SET(V,1,42)
    DEBUGINT(V!1)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 13 established the first two BCPL argument registers:

```text
argument 1 -> R7
argument 2 -> R8
```

Test 14 adds a third argument and requires all three values to participate
in the callee operation:

```text
START
    -> create local vector
    -> initialize V!1 = 17
    -> call SET(V,1,42)
SET
    -> receive V as argument 1
    -> receive I as argument 2
    -> receive X as argument 3
    -> compute V!I
    -> store X through the computed address
    -> return
START
    -> reload V!1
    -> DEBUGINT
    -> observe 42
```

The defining contract is that the first three BCPL arguments cross the
procedure boundary intact and are available to the callee in the generated
calling convention.

## Expected linkage evidence

Based on Tests 11 through 13, the expected register mapping is:

```text
argument 1 -> R7
argument 2 -> R8
argument 3 -> R9
```

R9 is an expectation to be verified from the generated S/370.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show the caller carrying V, I, and X in the generated three-argument call
  state;
- establish the register used for argument 3;
- show the callee using V and I to compute the target element address;
- show the callee storing the third argument X through that address;
- show the caller independently reloading V!1 after return.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test extends the machine-level calling convention relevant to native
BCPLMAIN/runtime primitives. Once verified, a native three-argument
primitive must accept the first three BCPL arguments in the same registers
used by CG370-generated calls while preserving the surrounding BCPL linkage
contract.

## Scope

This test does not introduce:

- four or more argument linkage;
- GETVEC or FREEVEC;
- BLIB;
- heap allocation.

The immediate purpose is to close the R7/R8/R9 argument-register evidence.

## Status

PASS.

Job 992 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the three-argument register convention.

The caller prepares all three arguments immediately before the call:

```asm
LA 9,42(0)
LA 8,1(0)
L  7,12(5)
LA 15,28(5)
L  4,0+L2-L4(4)
BALR 6,4
```

Thus, for `SET(V,1,42)`:

```text
R7 = V
R8 = I
R9 = X
```

The callee entry preserves through R9 and uses all three incoming arguments:

```asm
STM 4,9,0(15)
LR 5,15
AR 8,7
AR 8,8
ST 9,0(8,8)
BCR 15,11
```

R7 and R8 form the BCPL word address V+I. R8 is then doubled and used as
both base and index so that `0(8,8)` addresses the corresponding native
byte location. R9 is stored through that computed address.

After return, START independently reloads V!1 and observes 42 through
DEBUGINT, confirming all three arguments were interpreted correctly.


### Contract established

Test 14 establishes the first three BCPL argument registers for the native
CG370 calling convention:

```text
argument 1 -> R7
argument 2 -> R8
argument 3 -> R9
```

It also establishes that a generated three-argument callee preserves the
incoming argument set with `STM 4,9,0(15)` and can use R7, R8, and R9
directly on entry.

This is directly relevant to machine-coded BCPLMAIN/runtime primitives:
a native three-argument primitive must accept its first three BCPL arguments
in R7, R8, and R9 while preserving the surrounding BCPL linkage contract.
