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

PASS.

Job 984 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection satisfied the defining runtime-index criterion:

```asm
LA 7,16(5)
SRL 7,2(0)
ST 7,12(5)

LA 8,1(0)
ST 8,28(5)

AR 8,7
LA 9,42(0)
AR 8,8
ST 9,0(8,8)

L  7,28(5)
A  7,12(5)
AR 7,7
L  7,0(7,7)

LA 15,32(5)
L  4,600(12)
BALR 6,4
```

The store path keeps I in R8 and adds the BCPL vector word pointer in R7,
forming the BCPL word address V+I.  It then doubles that value and uses the
same register as both base and index in `0(8,8)`, yielding four times the
word address: the native byte address of V!I.

The load path independently reloads I from `28(R5)`, adds V from
`12(R5)`, and performs the same conversion before loading the fullword.
This proves runtime subscript evaluation rather than constant folding.


### Contract established

Test 10 directly establishes that generated native BCPL correctly supports:

- a vector subscript held in a mutable local variable;
- runtime addition of that subscript to a BCPL word pointer;
- conversion of the resulting BCPL word address to a native byte address;
- fullword store through the computed address;
- independent reload of both I and V for the later fullword load;
- observation of the loaded value through DEBUGINT.

The generated-code progression is now:

```text
Test 08: V!0  -> fixed zero displacement
Test 09: V!1  -> fixed four-byte displacement
Test 10: V!I  -> runtime word-address computation
```

The workspace layout also remains coherent: VEC 2 occupies three target
words beginning at 16(R5), local I is at 28(R5), and the next workspace
pointer is 32(R5).
