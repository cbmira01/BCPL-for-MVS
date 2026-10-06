# 10 - Variable vector subscript

This regression extends the local-vector contract from a constant subscript
to a runtime subscript held in a BCPL local variable.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET START () BE
$(1
    LET V = VEC 2
    LET I = 1

    V!I := 42
    DEBUGINT(V!I)

    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 09 established a constant nonzero subscript, where CG370 could encode
the one-word offset directly as a four-byte displacement.

Test 10 requires the subscript to be obtained at runtime from local variable
`I`:

```text
local VEC allocation
    -> initialize I = 1
    -> compute address of V!I at runtime
    -> store 42
    -> reload V!I using runtime index computation
    -> pass loaded value to DEBUGINT
    -> observe 42
```

The new contract is runtime scaling and combination of a BCPL word index with
the vector's BCPL word pointer.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated S/370 that loads or otherwise obtains local variable `I`;
- show runtime address/index arithmetic for `V!I` rather than a fixed
  four-byte displacement;
- show equivalent runtime index handling for the later load before DEBUGINT.

Generated-code inspection is part of the proof.

## Scope

This test does not introduce:

- passing vectors between procedures;
- mutation of I between store and load;
- GETVEC or FREEVEC;
- BLIB;
- heap allocation.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
