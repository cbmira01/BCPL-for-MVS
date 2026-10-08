# 067 — Complete historical BLIB compile/link/execute

## Objective

Compile the **entire surviving Cambridge BLIB**, link its generated
code with the application and current BCPLMAIN, and call two exported
services. The full library is held once at
`native-compiler/library/blib.bcpl`; this test points to it through
`library-source.txt`.

## Fidelity boundary

The canonical historical evidence is
`richards-bcpltape/bcplib/bcpl/blib`.
The native copy deletes the leading `SECTION "BLIB"` directive,
which the MR10 bootstrap compiler cannot parse, and substitutes one
comment. **Every other source line is preserved in order**, including
`GET "LIBHDR"`, all definitions, data, and MVS-specific diagnostics.

A whole-module build may expose compiler capacity limits, unsupported
source syntax, or assembler/static-combiner limitations. The test is
deliberately not disguised as a collection of individually extracted
routines.

## Required behavior

The separately compiled application calls `WRITES` at G!60 and
`WRITEN` at G!62 from the complete BLIB module and invokes native
`WRCH` G!14 for the separator.

Expected output:

```text
BLIB|42
```

The current assembler-level static combiner merges the generated
library trailer into the application section. Success establishes
**whole BLIB compilation and static combination**, not independently
loadable MVS BCPL sections. Other exported BLIB services are not
validated by this test; subsequent tests will explore them.

## Status

**PENDING** — native MVS compile, assemble, link, and run.
