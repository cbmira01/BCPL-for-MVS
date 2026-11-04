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

PASS.

Job 1000 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms genuine non-tail recursion.

DEPTH establishes its frame, tests N, and on the recursive path computes
N-1, advances the new-workspace pointer to 16(R5), and calls itself:

```asm
STM 4,7,0(15)
LR 5,15
CR 7,0
BC 7,0+L5-L1(4)
...
L5 EQU *
LH 7,0+L997-L1(4)
A  7,12(5)
LA 15,16(5)
L  4,0+L2-L1(4)
BALR 6,4
```

After the recursive call returns, the caller performs additional work on
the returned R7 value:

```asm
AH 7,2+L997-L1(4)
ST 7,16(5)
...
L  7,16(5)
BCR 15,11
```

The halfword constants are -1 and +1, so each recursive frame decrements N
before the call and increments the returned result during unwind.

Because the post-call increment occurs in every frame, this is not a tail
call. Successful output 42 therefore proves repeated frame creation and
ordinary recursive unwind through the BCPL linkage.


### Contract established

Test 18 establishes purpose-built recursive generated-call behavior:

- DEPTH calls itself through ordinary BCPL linkage;
- each recursive level advances W to a distinct new workspace;
- each frame preserves the state required for return;
- the recursive result returns in R7;
- each caller performs post-return arithmetic before returning itself;
- the system-vector return path successfully unwinds all recursive frames.

This independently validates the R5/R6/R15 workspace/linkage contract for
recursion, rather than relying on the earlier factorial milestone.
