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

DEFINED. Not yet run.
