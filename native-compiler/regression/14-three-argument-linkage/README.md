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

DEFINED. Not yet run.
