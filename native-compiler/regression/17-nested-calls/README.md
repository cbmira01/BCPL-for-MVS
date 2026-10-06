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

PASS.

Job 998 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the nested call/return behavior.

DOUBLE receives X in R7, establishes its own workspace, copies X into R8 so
that ADD receives two equal arguments, advances the new-workspace pointer,
and performs the nested call:

```asm
STM 4,7,0(15)
LR 5,15
LR 8,7
LA 15,16(5)
L  4,0+L2-L4(4)
BALR 6,4
BCR 15,11
```

ADD then receives A/B in R7/R8, computes the sum, places the result in R7,
and returns through the ordinary BCPL return path:

```asm
STM 4,8,0(15)
LR 5,15
AR 8,7
LR 7,8
BCR 15,11
```

DOUBLE performs no extra result move after the nested BALR; the R7 result
returned by ADD remains the value returned by DOUBLE. START then stores that
R7 result and passes it to DEBUGINT.

This proves that nested generated calls preserve the workspace/linkage state
needed to return correctly through two call boundaries.


### Contract established

Test 17 establishes ordinary nested generated-call behavior:

```text
START -> DOUBLE -> ADD -> DOUBLE -> START
```

Specifically, it proves:

- each callee establishes its own P from the caller-supplied W;
- DOUBLE advances W before making its nested call;
- the nested call uses the same R6 linkage convention;
- ADD returns its function result in R7;
- DOUBLE can propagate that R7 result directly to its caller;
- the ordinary system-vector return path unwinds both generated frames.

This strengthens the evidence for the R5/R6/R15 workspace/linkage contract
before recursion and library integration.
