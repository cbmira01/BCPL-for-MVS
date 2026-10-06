# 21 - Pointer stored and reloaded

This regression proves that a BCPL pointer can be stored as an ordinary
word value, reloaded later, and still be dereferenced correctly.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET START () BE
$(1
    LET V = VEC 2
    LET W = VEC 2
    LET P = 0

    V!1 := 42
    W!0 := V
    P := W!0
    DEBUGINT(P!1)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 20 established pointer return through R7.

Test 21 proves that BCPL pointers are also ordinary storable/reloadable word
values:

```text
START
    -> create V and W
    -> store 42 in V!1
    -> store pointer V into W!0
    -> reload W!0 into P
    -> dereference P!1
    -> DEBUGINT
    -> observe 42
```

The defining contract is preservation of pointer identity and representation
through a fullword store/load round trip.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show V represented as a BCPL word pointer;
- show that pointer stored into W!0 as a fullword value;
- show the pointer reloaded from W!0;
- show the reloaded pointer used to address P!1;
- show the loaded value reaching DEBUGINT.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test strengthens the data-model contract needed by runtime/library
structures. BCPL pointers must be safe to store in vectors, tables, control
blocks, and returned data structures without conversion beyond the normal
word-pointer representation.

## Scope

This test does not introduce:

- GETVEC or FREEVEC;
- BLIB;
- dynamic allocation;
- pointer arithmetic beyond ordinary vector indexing.

Its purpose is strictly pointer storage/reload identity.

## Status

DEFINED. Not yet run.
