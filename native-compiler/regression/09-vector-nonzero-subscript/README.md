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

PASS.

Job 982 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection satisfied the defining nonzero-index criterion:

```asm
LA 7,16(5)
SRL 7,2(0)
ST 7,12(5)

LA 8,42(0)
AR 7,7
ST 8,4(7,7)

L  7,12(5)
AR 7,7
L  7,4(7,7)

LA 15,28(5)
L  4,600(12)
BALR 6,4
```

As in Test 08, the local vector begins at byte address `16(R5)`, and CG370
stores its BCPL word pointer after shifting the byte address right by two.

For `V!1`, the effective address uses `4(7,7)`. After `AR 7,7`, the
base-plus-index pair contributes four times the BCPL word pointer, while the
explicit displacement contributes one target word, four bytes. This is the
native byte address of vector element 1.

The later load uses the same nonzero displacement, proving both store and
reload of `V!1`.


### Contract established

Test 09 directly establishes that generated native BCPL correctly supports:

- a nonzero constant vector subscript;
- conversion of that word subscript to the correct byte displacement;
- fullword store into `V!1`;
- later fullword load from `V!1`;
- observation of the loaded value through DEBUGINT.

The generated-code difference from Test 08 is precise:

```text
V!0  -> 0(7,7)
V!1  -> 4(7,7)
```

This is exactly the expected four-byte stride for 32-bit BCPL target words.

Variable subscripts remain deliberately unproven by this test.
