# 067 — Complete historical BLIB compile/link/execute

## Objective

Compile the **entire surviving Cambridge BLIB**, link its generated
code with the application and current BCPLMAIN, and call two exported
services. The historical source is demoted reproducibly into
`workarea/bootstrap-cambridge/demoted/blib` by the established
`make-demoted.py` generator. This test references it through
`library-source.txt`.

## Fidelity boundary

The canonical historical evidence is
`richards-bcpltape/bcplib/bcpl/blib`.
The generated derivative removes `SECTION "BLIB"` and rewrites the two
Cambridge `~=` operators to MR10-compatible `NE`. The `GET "LIBHDR"`,
all definitions, data, and MVS-specific diagnostics remain intact.
The generator checks the historical source shape and source-card width.

A whole-module build may expose compiler capacity limits, unsupported
source syntax, or assembler/static-combiner limitations. The test is
deliberately not disguised as a collection of individually extracted
routines.

## Required behavior

The separately compiled application calls `WRITES` at G!60 and
`WRITEN` at G!62 from the complete BLIB module and invokes native
`WRCH` G!14 for a space separator (avoiding an unresolved\nvertical-bar output transport anomaly).

Expected output:

```text
BLIB 42
```

The current assembler-level static combiner merges the generated
library trailer into the application section. Success establishes
**whole BLIB compilation and static combination**, not independently
loadable MVS BCPL sections. Other exported BLIB services are not
validated by this test; subsequent tests will explore them.

## Status

**PASS** — user-executed native regression 067 on MVS 3.8 (2026-10-08): `BLIB 42`; 1 PASS, 0 FAIL. Complete demoted historical BLIB compiled with the resident Cambridge compiler/CG370, statically combined with a separately compiled application, assembled by IFOX, linked by IEWL, and executed successfully. This does not establish dynamic section loading. The earlier vertical-bar character transport anomaly remains a separate issue.
