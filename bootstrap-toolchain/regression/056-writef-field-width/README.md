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

The format is now an ordinary BCPL string literal. The earlier
TABLE encoding was a temporary workaround for the source-lexing problem
resolved by Test 059 and the Cambridge bootstrap demotion fix.

## WIP runtime rule

The bootstrap G!76 implementation now recognizes `%I` followed by one width
character. Test 056 establishes the decimal width digit `4`. The historical
A-F width-digit extension visible in BLIB is not yet implemented.

The signed decimal representation is right-justified in the requested field.
A minus sign, when present, counts toward the field width. A width smaller than
the rendered number produces the full number without truncation.

This remains bootstrap machinery, not a claim that historical BLIB WRITEF was
implemented in machine code.

## Acceptance criteria

A successful Test 056 must:

- compile an ordinary source format string and a two-argument WRITEF call;
- pass 42 in R8;
- call G!76 through byte displacement 304;
- interpret `%I4` as a width-four signed-decimal conversion;
- emit exactly `>  42<`;
- terminate normally through FINISH.

## Status

PASS — native run on 2026-10-08; emitted `>  42<`.
