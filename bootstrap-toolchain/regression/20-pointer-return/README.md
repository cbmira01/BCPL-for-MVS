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

PASS.

Job 1004 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the pointer-return contract.

IDPTR receives V in R7 and returns immediately without altering R7:

```asm
STM 4,7,0(15)
LR 5,15
BCR 15,11
```

Because R7 is both argument 1 and the function-result register, the incoming
BCPL word pointer becomes the returned pointer unchanged.

The caller then stores that returned R7 value in local P:

```asm
L  7,12(5)
LA 15,32(5)
L  4,0+L2-L4(4)
BALR 6,4
ST 7,28(5)
```

It then dereferences the returned pointer directly:

```asm
AR 7,7
L  7,4(7,7)
```

The loaded vector element reaches DEBUGINT and emits 42.


### Contract established

Test 20 establishes that BCPL pointer values use the ordinary function-result
path without translation:

- a BCPL word pointer is passed to a function in R7;
- the function returns the pointer in R7;
- the caller stores the returned pointer as an ordinary local scalar;
- the returned pointer remains valid for later vector dereference;
- pointer identity and representation survive the call/return boundary.

This is direct groundwork for pointer-returning runtime services such as
GETVEC.
