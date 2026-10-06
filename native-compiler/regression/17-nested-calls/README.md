# 17 - Nested calls

This regression proves ordinary nested BCPL call/return behavior.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET ADD(A,B) = A+B

LET DOUBLE(X) = ADD(X,X)

LET START () BE
$(1
    LET X = DOUBLE(21)

    DEBUGINT(X)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 16 established the ordinary function-result convention in R7.

Test 17 adds one more call level:

```text
START
    -> call DOUBLE(21)
DOUBLE
    -> receive X
    -> call ADD(X,X)
ADD
    -> compute X+X
    -> return 42
DOUBLE
    -> return the nested result
START
    -> consume the returned value
    -> DEBUGINT
    -> observe 42
```

The defining contract is that nested generated calls correctly preserve and
restore BCPL workspace, linkage, branch-base, and result state across two
successive call boundaries.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show START calling DOUBLE through ordinary BCPL linkage;
- show DOUBLE establishing its own workspace and making a nested call to ADD;
- show ADD returning its result through R7;
- show DOUBLE propagating that result to its caller;
- show START consuming the final returned value.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test exercises repeated use of the generated workspace and linkage
conventions that BCPLMAIN's return trampoline and machine-coded runtime
entries must coexist with. It is specifically intended to validate ordinary
nested generated calls before recursion and library integration.

## Scope

This test does not introduce:

- recursion;
- pointer returns;
- GETVEC or FREEVEC;
- BLIB.

Those remain later regression steps.

## Status

DEFINED. Not yet run.
