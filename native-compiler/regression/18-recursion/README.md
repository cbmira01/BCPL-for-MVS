# 18 - Recursion

This regression proves repeated recursive BCPL call/return behavior with
real frame stacking and result propagation during unwind.

The program is deliberately small but non-tail-recursive:

```bcpl
GLOBAL $( START:1; DEBUGINT:150 $)

LET DEPTH(N) = N=0 -> 37, DEPTH(N-1)+1

LET START () BE
$(1
    LET X = DEPTH(5)

    DEBUGINT(X)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Test 17 established an ordinary two-level nested call chain.

Test 18 exercises repeated calls to the same generated function:

```text
DEPTH(5)
  -> DEPTH(4)
    -> DEPTH(3)
      -> DEPTH(2)
        -> DEPTH(1)
          -> DEPTH(0) = 37
        <- +1
      <- +1
    <- +1
  <- +1
<- +1 = 42
```

The expression is intentionally non-tail-recursive. Each recursive caller
must still use the returned value after the recursive call, so successful
execution requires real call-frame creation and unwinding.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated recursive code calling DEPTH from inside DEPTH;
- show a new workspace pointer being formed for the recursive call;
- show the recursive result returning in R7;
- show post-return arithmetic performed by each caller before its own return;
- demonstrate successful unwind through all recursive frames.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test directly stresses the R5/R6/R15 workspace/linkage contract and the
system-vector return path repeatedly. It is independent of the historical
factorial milestone and gives a purpose-built regression for ordinary
recursive generated code.

## Scope

This test does not introduce:

- pointer returns;
- GETVEC or FREEVEC;
- BLIB;
- dynamic stack allocation.

The current static WIP workspace is sufficient for this shallow recursion.

## Status

DEFINED. Not yet run.
