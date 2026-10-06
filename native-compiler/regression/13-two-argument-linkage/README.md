# 13 - Two-argument BCPL linkage

This regression extends the native calling-convention evidence from one
argument to two arguments.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET SET(V,I) BE
$(1
    V!I := 42
$)1

LET START () BE
$(1
    LET V = VEC 2

    V!1 := 17
    SET(V,1)
    DEBUGINT(V!1)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 12 established write-through aliasing through the one-argument BCPL
procedure linkage.

Test 13 adds a second argument:

```text
START
    -> create local vector
    -> initialize V!1 = 17
    -> call SET(V,1)
SET
    -> receive V as argument 1
    -> receive I as argument 2
    -> compute V!I
    -> store 42 through the pointer
    -> return
START
    -> reload V!1
    -> DEBUGINT
    -> observe 42
```

The defining contract is that the first two BCPL arguments cross the
procedure boundary intact and can be used together by the callee.

## Expected linkage evidence

Based on the linkage already observed, the generated code is expected to use
R7 for argument 1 and R8 for argument 2. This is an expectation to be checked
against the generated S/370, not assumed as proof.

The callee should preserve/expose both incoming arguments sufficiently to
compute the runtime vector address for `V!I`.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show the caller placing V and I into the generated two-argument call state;
- show the callee receiving both arguments;
- show the callee combining V and I to compute the vector element address;
- show a fullword store of 42 through that computed address;
- show the caller independently reloading V!1 after return.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test is directly relevant to the linkage contract that machine-coded
BCPLMAIN/runtime primitives must obey. If the expected R7/R8 convention is
confirmed, native routines accepting two BCPL arguments must preserve and
interpret those registers consistently with CG370-generated calls.

## Scope

This test does not introduce:

- three-argument linkage;
- GETVEC or FREEVEC;
- BLIB;
- heap allocation.

Test 14 is intended to extend the evidence to three arguments.

## Status

PASS.

Job 990 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the two-argument register convention.

The caller prepares argument 2 in R8 and argument 1 in R7 immediately before
the call:

```asm
LA 8,1(0)
L  7,12(5)
LA 15,28(5)
L  4,0+L2-L4(4)
BALR 6,4
```

Thus, for `SET(V,1)`:

```text
R7 = V
R8 = I
```

The callee entry preserves through R8 and immediately combines the two
incoming arguments:

```asm
STM 4,8,0(15)
LR 5,15
AR 8,7
LA 9,42(0)
AR 8,8
ST 9,0(8,8)
BCR 15,11
```

After `AR 8,7`, R8 contains the BCPL word address V+I. Doubling R8 and
using `0(8,8)` converts that word address to its native byte address, where
the callee stores 42.

After return, START independently reloads V and reads V!1 before calling
DEBUGINT, confirming that both arguments were interpreted correctly and the
callee modified the intended element.


### Contract established

Test 13 establishes the first two BCPL argument registers for the native
CG370 calling convention:

```text
argument 1 -> R7
argument 2 -> R8
```

It also establishes that a generated two-argument callee preserves the
incoming argument set with `STM 4,8,0(15)` and can use R7 and R8 directly
on entry.

This is directly relevant to machine-coded BCPLMAIN/runtime primitives:
a native two-argument primitive must accept its first two BCPL arguments in
R7 and R8 and preserve the surrounding BCPL register/linkage contract.
