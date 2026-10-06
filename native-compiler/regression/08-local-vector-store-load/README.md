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

DEFINED. Not yet run.
