# Multiple-assignment regression test

This test isolates BCPL multiple assignment so that compiler/interpreter semantics can be checked independently of a larger algorithm.

The source performs two assignments:

```text
A, B := B, A
```

starting from `A=1, B=2`, followed by:

```text
A, B := B, A REM B
```

starting from `A=1071, B=462`.

If BCPL multiple assignment evaluates all right-hand-side expressions before storing any left-hand-side result, the expected output is:

```text
SWAP BEFORE A=1 B=2
SWAP AFTER  A=2 B=1
EUCLID BEFORE A=1071 B=462
EUCLID AFTER  A=462 B=147
```

Run from the repository root with:

```text
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/09-multiple-assignment/multiple-assignment.bcpl
```

A different result establishes a focused semantic regression without depending on the GCD demo.
