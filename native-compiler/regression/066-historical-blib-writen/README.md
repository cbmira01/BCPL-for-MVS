# 066 — Historical Cambridge BLIB WRITEN and WRITED

## Objective

Compile the actual historical BLIB `WRITED` and `WRITEN` procedure
bodies in an independent BCPL unit, then exercise signed decimal
formatting natively. The bodies are copied from
`richards-bcpltape/bcplib/bcpl/blib` without changes.

```bcpl
LET WRITED(N, D) BE

$(1 LET T = VEC 20
    AND I, K = 0, -N
    IF N<0 DO D, K := D-1, N
    T!I, K, I := -(K REM 10), K/10, I+1    REPEATUNTIL K=0
    FOR J = I+1 TO D DO WRCH('*S')
    IF N<0 DO WRCH('-')
    FOR J = I-1 TO 0 BY -1 DO WRCH(T!J+'0')  $)1

AND WRITEN(N) BE WRITED(N, 0)
```

## Linkage and dependencies

- G!62 `WRITEN` — historical BLIB export
- G!68 `WRITED` — historical BLIB export
- G!14 `WRCH` — existing machine-dependent native primitive
- G!1 `START` — application export

The program runs `WRITEN(42)`, `WRITEN(-17)`, and
`WRITEN(0)`, separated by literal vertical bars using `WRCH`.

Expected output:

```text
42|-17|0
```

The existing Test 025 static combiner merges the separately compiled
application and historical BLIB library exports; this is not yet
unchanged native multi-section linkage. No BCPLMAIN or CG370 changes
are required for this test.

## Status

**PENDING** — native MVS regression not yet executed.
