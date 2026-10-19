# 058 - WRITEF fixed-width octal formatting

This regression adds the historical `%On` path to the native WRITEF
bootstrap.

The surviving BLIB WRITEF routes `%O` through `WRITEOCT(ARG,N)`. The
surviving WRITEOCT body emits exactly `N` octal digits, high 3-bit group
first, using `0-7`. Values narrower than the field are therefore zero-filled.

Test 058 exercises width four with decimal value 42. The target format is
equivalent to:

```text
>%O4<
```

Expected output:

```text
>0052<
```

## Source shape

The format is now an ordinary BCPL string literal. Its earlier
TABLE encoding was a temporary source-lexing workaround, resolved by
the Cambridge bootstrap demotion fix and Test 059.

## Historical contract

The surviving BLIB implementation is:

```bcpl
AND WRITEOCT(N, D) BE
    FOR I = 3*(D-1) TO 0 BY -3 DO
       WRCH(((I>BITSPERWORD->0,N>>I)&7)+'0')
```

Test 058 therefore expects exactly four zero-filled octal digits.

## Acceptance criteria

A successful Test 058 must:

- compile an ordinary source format string and two-argument WRITEF call;
- pass 42 in R8;
- call G!76 through byte displacement 304;
- interpret `%O4` as exactly four octal digits;
- emit exactly `>0052<`;
- terminate normally through FINISH.

## Status

PASS — native run on 2026-10-08; emitted `>0052<`.
