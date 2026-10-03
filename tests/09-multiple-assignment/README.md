# Multiple-assignment regression test

This test records the multiple-assignment behavior of the historical MR10 compiler used by this reconstruction.

The source performs two assignments:

```text
A, B := B, A
```

starting from `A=1, B=2`, followed by:

```text
A, B := B, A REM B
```

starting from `A=1071, B=462`.

The MR10 translator implements these assignments sequentially. Its `ASSIGN` routine recursively processes comma-separated left- and right-hand-side lists, and for each scalar pair it loads the right-hand expression and stores the left-hand destination before proceeding to the next pair.

Accordingly, the expected output for this compiler is:

```text
SWAP BEFORE A=1 B=2
SWAP AFTER  A=2 B=2
EUCLID BEFORE A=1071 B=462
EUCLID AFTER  A=462 B=0
```

Run from the repository root with:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/09-multiple-assignment/multiple-assignment.bcpl
```

A run producing the expected output above records the historical MR10 behavior directly and reproducibly. The test is retained so that later compiler reconstruction work does not accidentally change that behavior without an explicit decision.

Programs that require simultaneous assignment semantics must use explicit temporaries when compiled by this MR10 translator.
