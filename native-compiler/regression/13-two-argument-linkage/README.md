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

DEFINED. Not yet run.
