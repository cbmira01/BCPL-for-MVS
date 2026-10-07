# 47 - multiple assignment

This regression isolates BCPL multiple assignment semantics.

Expected output:

```text
42
25
17
```

## Source shape

```bcpl
LET A = 17
LET B = 25

A,B := B,A

DEBUGINT(A + B)
DEBUGINT(A)
DEBUGINT(B)
```

Earlier regressions already establish local scalar variables, ordinary
assignment, addition, DEBUGINT, and FINISH. Test 47 adds only multiple
assignment.

## Why a swap

A swap is the strongest minimal discriminator for simultaneous assignment.

If the compiler incorrectly lowers:

```bcpl
A,B := B,A
```

as sequential stores, then assigning A first would destroy the original value
needed for B. Correct BCPL semantics require all right-hand-side values to be
captured before any left-hand-side destination is overwritten.

Starting from:

```text
A = 17
B = 25
```

the correct result is:

```text
A = 25
B = 17
```

The first DEBUGINT emits the invariant sum 42; the following two outputs prove
that an actual swap occurred rather than merely preserving the sum.

## Historical motivation

Multiple assignment is part of the historical BCPL language definition and is
used in systems-oriented BCPL programming where compact state updates are
common. This is documentation-driven core-language coverage.

## What to inspect in generated assembler

The generated System/370 should reveal how CG370 preserves all source values
before performing destination stores. Possible strategies include:

- loading both RHS values into registers before either store;
- using temporary workspace cells;
- a mixed register/workspace strategy.

The key property is semantic simultaneity, not a specific instruction pattern.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly:

  ```text
  42
  25
  17
  ```

- demonstrate that both RHS values are preserved before the swap stores;
- require no new BCPLMAIN runtime service.

## Status

PENDING — ready for first native run.
