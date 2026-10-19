# 08 - Local vector element store/load

This regression introduces the first native BCPL vector operation while
keeping allocation local to the current BCPL workspace.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET START () BE
$(1
    LET V = VEC 2

    V!0 := 42
    DEBUGINT(V!0)

    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Tests 05 through 07 established scalar observability, mutable local state,
and user global-vector state.

Test 08 introduces aggregate word storage without introducing dynamic
allocation:

```text
local VEC allocation
    -> form vector address
    -> store 42 into V!0
    -> load V!0
    -> pass loaded value to DEBUGINT
    -> observe 42
```

This is specifically a test of BCPL local-vector representation and indexed
word addressing.

## Important boundary

`VEC 2` here is a local vector created as part of the procedure workspace.
This test does not use library GETVEC and does not depend on heap allocation,
FREEVEC, or BLIB.

That distinction is intentional. The goal is to prove the compiler/runtime
pointer and vector-addressing model before introducing dynamic storage.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated S/370 that forms the local vector address;
- show an indexed/fullword store corresponding to `V!0 := 42`;
- show a later indexed/fullword load corresponding to `V!0` before
  DEBUGINT.

Generated-code inspection is part of the proof. Test 08 is intended to
establish real vector storage and retrieval, not merely the final output.

## Scope

This test does not introduce:

- GETVEC or FREEVEC;
- BLIB;
- nonzero vector subscripts;
- passing vectors between procedures;
- arithmetic beyond address/index formation emitted by CG370;
- general stream selection.

Those remain later regression steps.

## Status

PASS.

Job 980 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection satisfied the defining vector-addressing criteria:

```asm
LA 7,16(5)
SRL 7,2(0)
ST 7,12(5)

LA 8,42(0)
AR 7,7
ST 8,0(7,7)

L  7,12(5)
AR 7,7
L  7,0(7,7)

LA 15,28(5)
L  4,600(12)
BALR 6,4
```

The local vector begins at byte address `16(R5)`. CG370 converts that
native byte address to a BCPL word pointer with `SRL 7,2` and stores the
pointer in the local slot at `12(R5)`.

For `V!0`, `AR 7,7` doubles the word pointer and the System/370
base-plus-index address `0(7,7)` doubles it again. The resulting effective
address is therefore four times the BCPL word pointer: the original native
byte address of the vector.

The store and later load both use that reconstructed address. Job 980 then
observed decimal 42 through DEBUGINT.


### Contract established

Test 08 directly establishes that the generated native code correctly
supports:

- local vector allocation inside the BCPL procedure workspace;
- conversion of a native byte address to a BCPL word pointer;
- storage of that BCPL pointer in a local variable;
- conversion of the word pointer back to a native byte address for `!0`;
- fullword store through a vector reference;
- later fullword load through the same vector reference;
- reporting the loaded value through DEBUGINT.

The workspace layout is also visible. The vector starts at `16(R5)`, and
the next-workspace pointer is formed as `28(R5)`. Thus this `VEC 2`
occupies three target words, consistent with BCPL vector subscripts 0..2.

A nonzero subscript remains deliberately unproven by this test.
