# 09 - Nonzero vector subscript

This regression extends the local-vector contract by using a nonzero
subscript.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET START () BE
$(1
    LET V = VEC 2

    V!1 := 42
    DEBUGINT(V!1)

    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 08 established local vector formation and word store/load through
`V!0`.

Test 09 proves that CG370 correctly incorporates a nonzero word index:

```text
local VEC allocation
    -> form BCPL word pointer
    -> address element V!1
    -> store 42
    -> reload V!1
    -> pass loaded value to DEBUGINT
    -> observe 42
```

The new contract is the one-word offset beyond the vector base.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated S/370 that forms the local vector address;
- show the nonzero subscript contributing one target word to the effective
  address for the store;
- show the same nonzero subscript behavior for the later load before
  DEBUGINT.

Generated-code inspection is part of the proof.

## Scope

This test does not introduce:

- variable subscripts;
- passing vectors between procedures;
- GETVEC or FREEVEC;
- BLIB;
- heap allocation.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
