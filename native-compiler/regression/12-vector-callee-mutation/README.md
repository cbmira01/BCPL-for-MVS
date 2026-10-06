# 12 - Callee mutation through a vector pointer

This regression proves write-through aliasing across an ordinary BCPL
procedure-call boundary.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET SETVALUE(V) BE
$(1
    V!1 := 42
$)1

LET START () BE
$(1
    LET V = VEC 2

    V!1 := 17
    SETVALUE(V)
    DEBUGINT(V!1)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 11 established that a vector pointer can be passed to a callee and
dereferenced there.

Test 12 extends that contract from read access to shared mutable storage:

```text
START
    -> create local vector
    -> store 17 in V!1
    -> pass V to SETVALUE
SETVALUE
    -> receive V
    -> store 42 through V!1
    -> return
START
    -> reload V!1
    -> pass the reloaded value to DEBUGINT
    -> observe 42
```

The defining contract is that the caller and callee refer to the same
underlying vector storage through the passed BCPL word pointer.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show START passing the BCPL vector word pointer as an ordinary argument;
- show SETVALUE storing 42 through the received vector pointer;
- show START independently reloading V and dereferencing V!1 after the
  procedure returns;
- show that the observed value comes from the post-call reload.

Generated-code inspection is part of the proof.

## Linkage relevance

This test still uses only the already-proven one-argument BCPL procedure
linkage through R7. Its new contribution is pointer aliasing and write-through
semantics, not a wider argument-register contract.

Tests 13 and 14 are expected to extend the linkage evidence to two and three
arguments respectively.

## Scope

This test does not introduce:

- two-argument or three-argument linkage;
- variable vector subscripts;
- GETVEC or FREEVEC;
- BLIB;
- heap allocation.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
