# 056 - WRITEF field-width formatting

This regression adds the first historical field-width path to the native
WRITEF bootstrap.

The surviving BLIB implementation distinguishes `%I` from `%N`:

- `%N` calls `WRITED(ARG,0)`;
- `%I` consumes one additional format character, converts it to a numeric
  width, and calls `WRITED(ARG,N)`.

Test 056 exercises `%I4` with the value 42. To make the two leading blanks
observable, the format includes literal delimiters and is equivalent to:

```text
>%I4<
```

Expected output:

```text
>  42<
```

## Source shape

The format is constructed as target-resident TABLE data:

```bcpl
LET F = TABLE #X056E6CC9, #XF44C0000
WRITEF(F, 42)
```

The bytes encode a BCPL string of length 5 containing EBCDIC:

```text
6E 6C C9 F4 4C
 >  %  I  4  <
```

This avoids conflating field-width behavior with the separate inline-SYSIN
format-string transport issue encountered during Test 055.

## WIP runtime rule

The bootstrap G!76 implementation now recognizes `%I` followed by one width
character. The width character is interpreted with the historical hexadecimal-
style digit convention used by BLIB. Test 056 covers the decimal digit `4`.

The signed decimal representation is right-justified in the requested field.
A minus sign, when present, counts toward the field width. A width smaller than
the rendered number produces the full number without truncation.

This remains bootstrap machinery, not a claim that historical BLIB WRITEF was
implemented in machine code.

## Acceptance criteria

A successful Test 056 must:

- compile the target-format TABLE and a two-argument WRITEF call;
- pass 42 in R8;
- call G!76 through byte displacement 304;
- interpret `%I4` as a width-four signed-decimal conversion;
- emit exactly `>  42<`;
- terminate normally through FINISH.

## Status

Pending native run.
