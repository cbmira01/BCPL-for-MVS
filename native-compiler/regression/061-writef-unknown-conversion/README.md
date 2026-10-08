# 061 - WRITEF unknown conversion

The historical IBM System/370 BLIB WRITEF branch for an unrecognized
conversion uses `WRCH(TYPE)`, emitting the type letter without the
preceding percent sign. Unlike a recognized conversion, this branch
does not increment the formatting argument pointer.

This regression isolates the default conversion branch; it does not
exercise any unsupported numeric width or unrelated runtime behavior.

## Source

```bcpl
WRITEF("A%QB")
```

Expected output:

```text
AQB
```

## Acceptance criteria

- Compile the ordinary source string through resident Cambridge SYN/LEX/TRN.
- Call G!76 through byte displacement 304.
- Emit the unknown type `Q` but not its preceding percent sign.
- Emit the surrounding literal characters in order.
- Exit normally through FINISH.
- Preserve all established Tests 000–060.

The behavior is supported by the surviving
`richards-bcpltape/bcplib/bcpl/blib` default WRITEF branch.
BCPLMAIN remains a provisional native bootstrap runtime.

## Status

**PENDING** — native execution has not yet been performed.
