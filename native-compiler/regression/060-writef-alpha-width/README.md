# 060 - WRITEF alphabetic decimal field width

The surviving BLIB WRITEF recognizes width characters `0` through `9`
and `A` through `F`, with `A` meaning width 10 and `F` meaning width 15.

This regression establishes exactly one new contract: `%IA` produces a
right-justified signed decimal value in a ten-character field. It does
not extend hexadecimal or octal formatting.

## Source

```bcpl
WRITEF(">%IA<", 42)
```

Expected BCPL output (eight blanks precede 42):

```text
>        42<
```

## Acceptance criteria

- Compile the ordinary BCPL source literal through the resident Cambridge
  compiler and normal `SYSIN DD DATA` path.
- Call G!76 through byte displacement 304.
- Interpret `A` as field width 10 for `%I`.
- Preserve blank padding, argument consumption, and FINISH termination.
- Produce exactly the expected output.
- Existing Tests 000–059 remain passing.

The WIP machine-code WRITEF is provisional bootstrap machinery; the
alphabetic width rule is based on the surviving BLIB source.

## Status

**PENDING** — requires native MVS regression execution.
