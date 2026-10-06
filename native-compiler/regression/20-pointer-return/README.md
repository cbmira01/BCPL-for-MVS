# 20 - Pointer return

This regression proves that a BCPL pointer value can be returned from an
ordinary function and then dereferenced correctly by the caller.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET IDPTR(V) = V

LET START () BE
$(1
    LET V = VEC 2
    LET P = 0

    V!1 := 42
    P := IDPTR(V)
    DEBUGINT(P!1)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 16 established that ordinary function results return in R7.

Test 20 applies that result convention specifically to a BCPL pointer value:

```text
START
    -> create local VEC
    -> store 42 in V!1
    -> call IDPTR(V)
IDPTR
    -> receive V
    -> return the same BCPL word pointer
START
    -> store returned pointer in P
    -> dereference P!1
    -> DEBUGINT
    -> observe 42
```

The defining contract is that pointer values are returned unchanged through
the ordinary function-result path and remain valid for later dereference.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show the caller passing V to IDPTR;
- show IDPTR returning that pointer as its function result;
- show the caller storing or otherwise preserving the returned pointer;
- show a later dereference through the returned pointer;
- show the loaded value reaching DEBUGINT.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test is important groundwork for pointer-returning runtime functions.
A future GETVEC implementation, for example, will need to return a BCPL word
pointer through the same R7 function-result convention.

## Scope

This test does not introduce:

- dynamic allocation;
- GETVEC or FREEVEC;
- BLIB;
- pointer-to-pointer storage.

The pointer returned here refers to caller-owned local vector storage.

## Status

DEFINED. Not yet run.
