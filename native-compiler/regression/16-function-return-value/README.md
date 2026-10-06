# 16 - Function return value

This regression proves the native BCPL function-result convention.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET ADD(A,B) = A+B

LET START () BE
$(1
    LET X = ADD(17,25)

    DEBUGINT(X)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Tests 13 through 15 established BCPL argument registers R7-R10.

CGHDR also identifies R7 as the function-result register. Test 16 verifies
that live call/return behavior directly:

```text
START
    -> call ADD(17,25)
ADD
    -> receive A and B
    -> compute A+B
    -> return the result
START
    -> consume the returned value
    -> DEBUGINT
    -> observe 42
```

The defining contract is that an ordinary BCPL function returns its result in
the register/state expected by generated caller code.

## Expected linkage evidence

Based on CGHDR, the expected result convention is:

```text
function result -> R7
```

This is an expectation to be verified from generated S/370.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show ADD receiving A and B through the established argument convention;
- show ADD placing the computed result in R7 before ordinary BCPL return;
- show START consuming the returned R7 value after the call;
- show that value being passed to DEBUGINT.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test establishes the return-value side of the native BCPL calling
convention. Machine-coded runtime functions that return a BCPL value must
place that value in R7 before returning through the ordinary BCPL linkage.

## Scope

This test does not introduce:

- nested calls from inside ADD;
- recursion;
- pointer returns;
- GETVEC or FREEVEC;
- BLIB.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
