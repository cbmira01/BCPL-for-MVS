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

PASS.

Jobs 1006 and 1008 on 2026-10-06 both assembled, link-edited, and executed
successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the pointer store/reload contract.

V and W are each formed as BCPL word pointers from their native byte
addresses:

```asm
LA 7,16(5)
SRL 7,2(0)
ST 7,12(5)

LA 8,32(5)
SRL 8,2(0)
ST 8,28(5)
```

The program stores 42 in V!1, then stores pointer V as an ordinary fullword
value into W!0:

```asm
LA 9,42(0)
AR 7,7
ST 9,4(7,7)

L  7,12(5)
L  8,28(5)
AR 8,8
ST 7,0(8,8)
```

It later reloads the pointer value from W!0 and stores it in local P:

```asm
L  7,28(5)
AR 7,7
L  8,0(7,7)
ST 8,44(5)
```

Finally, it dereferences the reloaded pointer and reads P!1:

```asm
AR 8,8
L  7,4(8,8)
```

The loaded element reaches DEBUGINT and emits 42.


### Contract established

Test 21 establishes that BCPL pointers are ordinary 32-bit BCPL word values
for storage purposes:

- a vector pointer can be stored into another vector element;
- the pointer survives a fullword store/load round trip unchanged;
- the reloaded pointer can be assigned to a local scalar;
- the reloaded pointer remains valid for later vector dereference;
- no special pointer tagging or reconstruction is required beyond the normal
  BCPL word-pointer representation.

This is directly relevant to future runtime/library control structures that
store BCPL pointers in vectors, lists, tables, or allocation metadata.
