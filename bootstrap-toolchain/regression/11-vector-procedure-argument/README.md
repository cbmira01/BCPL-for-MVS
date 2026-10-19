# 11 - Pass a vector to another procedure

This regression proves that a BCPL vector pointer can cross an ordinary
procedure-call boundary and still be dereferenced correctly by the callee.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET SHOW(V) BE
$(1
    DEBUGINT(V!1)
$)1

LET START () BE
$(1
    LET V = VEC 2

    V!1 := 42
    SHOW(V)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Tests 08 through 10 established local vector representation and indexing
inside one procedure.

Test 11 moves the vector pointer across a BCPL call boundary:

```text
START
    -> allocate local VEC
    -> store 42 in V!1
    -> pass V as an argument
SHOW
    -> receive V
    -> dereference V!1
    -> pass loaded value to DEBUGINT
    -> observe 42
```

The new contract is pointer argument passing plus dereference in the callee.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated S/370 in START that passes the BCPL vector word pointer as
  an ordinary procedure argument;
- show generated S/370 in SHOW that receives or reloads that pointer from
  the callee workspace/argument state;
- show SHOW dereferencing `V!1` through the received pointer before
  DEBUGINT.

Generated-code inspection is part of the proof.

## Scope

This test does not introduce:

- GETVEC or FREEVEC;
- BLIB;
- heap allocation;
- returning vectors from procedures;
- mutation of the vector in the callee.

Those remain later regression steps.

## Status

PASS.

Job 986 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection satisfied the defining pointer-argument criterion.

The caller forms and stores the local BCPL vector word pointer, stores 42 in
V!1, reloads V into R7, and calls SHOW:

```asm
LA 7,16(5)
SRL 7,2(0)
ST 7,12(5)
LA 8,42(0)
AR 7,7
ST 8,4(7,7)
L  7,12(5)
LA 15,28(5)
L  4,0+L2-L4(4)
BALR 6,4
```

SHOW receives V in R7. Its entry saves R4..R7 into the new workspace, then
dereferences V!1 directly from the received BCPL word pointer:

```asm
STM 4,7,0(15)
LR 5,15
AR 7,7
L  7,4(7,7)
LA 15,16(5)
L  4,600(12)
BALR 6,4
BCR 15,11
```

After doubling R7, `4(7,7)` reconstructs four times the BCPL word pointer
plus one target word, which is the native byte address of V!1.

This proves that the vector pointer crosses the BCPL call boundary as an
ordinary argument and remains valid for callee-side dereference.


### Contract established

Test 11 directly establishes that generated native BCPL correctly supports:

- passing a BCPL vector word pointer as argument 1 in R7;
- preserving the argument across procedure entry;
- dereferencing the received pointer in the callee;
- reading a nonzero vector element in the callee;
- passing the loaded value onward to DEBUGINT;
- returning through the ordinary BCPL procedure-return path.

This extends the vector progression from same-procedure access to
cross-procedure pointer visibility without introducing GETVEC, FREEVEC, or
BLIB.
