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

The format is carried as target-resident TABLE data:

```bcpl
LET F = TABLE #X056E6CE7, #XF44C0000
WRITEF(F, 42)
```

The bytes encode a BCPL string of length 5 containing EBCDIC:

```text
6E 6C E7 F4 4C
 >  %  X  4  <
```

As in Tests 055-056, this avoids conflating WRITEF behavior with the separate
inline-SYSIN format-string transport problem.

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

- compile the target-format TABLE and two-argument WRITEF call;
- pass 42 in R8;
- call G!76 through byte displacement 304;
- interpret `%X4` as exactly four hexadecimal digits;
- emit exactly `>002A<`;
- terminate normally through FINISH.

## Status

PASS — native run on 2026-10-08; emitted `>002A<`.
