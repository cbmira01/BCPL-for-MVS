# 057 - WRITEF fixed-width hexadecimal formatting

This regression adds the historical `%Xn` path to the native WRITEF
bootstrap.

The surviving BLIB WRITEF routes `%X` through `WRITEHEX(ARG,N)`. The
surviving WRITEHEX body emits exactly `N` hexadecimal digits, from high
nibble to low nibble, using `0-9,A-F`. Values narrower than the field are
therefore zero-filled rather than blank-padded.

Test 057 exercises width four with decimal value 42. The target format is
equivalent to:

```text
>%X4<
```

Expected output:

```text
>002A<
```

## Source shape

The format is now an ordinary BCPL string literal. Its earlier
TABLE encoding was a temporary source-lexing workaround, resolved by
the Cambridge bootstrap demotion fix and Test 059.

## Historical contract

The surviving BLIB implementation is:

```bcpl
AND WRITEHEX(N, D) BE
    FOR I = 4*(D-1) TO 0 BY -4 DO
        WRCH(GETBYTE(
          (TABLE #XF0F1F2F3, #XF4F5F6F7, #XF8F9C1C2, #XC3C4C5C6),
          (I>BITSPERWORD->0,N>>I)&#XF))
```

Test 057 therefore expects fixed-width, zero-filled output, not the blank
padding used by `WRITED` for `%I`.

## Acceptance criteria

A successful Test 057 must:

- compile an ordinary source format string and two-argument WRITEF call;
- pass 42 in R8;
- call G!76 through byte displacement 304;
- interpret `%X4` as exactly four hexadecimal digits;
- emit exactly `>002A<`;
- terminate normally through FINISH.

## Status

PASS — native run on 2026-10-08; emitted `>002A<`.
