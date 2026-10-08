# 072 — Historical BLIB WRITED width and sign

## Objective

Call the actual historical BLIB `WRITED(N,D)` (G!68) from the
persistent object-library member. The original implementation builds
the decimal digits in a local vector and prints leading blanks to
reach width D, reserving one position for a negative sign.

The test emits `WRITED(42,4)` and `WRITED(-17,6)` with explicit
delimiters, so the number of spaces is observable.

Expected output (two spaces in first field, three in second):

```text
>  42< >   -17<
```

This is independent-object assembly and linkage via `object-blib.txt`,
not the static assembler combiner or BCPLMAIN's bootstrap WRITEF.

## Status

PENDING first TK5 execution.
