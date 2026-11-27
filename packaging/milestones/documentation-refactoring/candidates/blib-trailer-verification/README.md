# DR.5 — Resident BLIB export-trailer verification

**Status:** Prepared; native verification pending.
Source checkpoint `6763eb9f69f7812d84d9d320c6704154f4ebf6ee`.

[Historical JOB 2197](../../../../archive/runtime-extensions/runtime-extensions-r0-trailer-job-2197-evidence-20261021.md)
observed 21 BLIB procedure exports and one application START export.
This agrees with historical BLIB/LIBHDR source. G!71 TERMINATOR is a
referenced global data slot, not a BLIB procedure export; G!79
USERPOSTMORTEM is a referenced hook, not an exported BLIB procedure.
The subsequent BLIB rebuild makes a new census appropriate, without
reopening R.0 or invalidating JOB 2197.

The [driver](../../../../../tools/checks/run-dr5-blib-trailer.py) reuses
the unchanged [R.0 assembler observer and parser](../../../../../bootstrap-toolchain/probes/r0-export-trailer-probe/README.md).
It compiles the existing minimal application using resident CAMBCOMP,
then links the existing observer, application and resident runtime/BLIB
objects. The sole adaptation of the historical deck is inclusion of
BCPLRGS and BCPLREG to resolve current BCPLMAIN references. Only the
observer executes. It reads actual relocated export pairs, without
running the compiled application, BLIB or BCPLMAIN.

Expected application set: G!1. Expected BLIB set:

    3 4 5 56 58 59 60 62 63 64 65 66 67 68 69 70 74 75 76 77 78

Require compiler COMP/SVCODE RC0 and CODE=0, observer ASMT/ASMA/LKED/GO
RC0, bounded report records, exact slot sets and no app/BLIB overlap.
The historic parser's static Core Runtime overlap table is historical,
not an assertion of current runtime ownership. Addresses and maximum
global are recorded but not compared to historical absolute addresses.
The census does not establish binary provenance, actual startup global
publication or safe execution of diagnostic procedures.

Run-scoped evidence: workarea/dr5-blib-trailer/. No installed PDS writes,
physical JES device output, release modification, or automatic retry.
The old JES names R0TRCMP/R0TRAIL are retained to reuse the verified
deck generator; this is DR.5 evidence, not another R.0 march or a
numbered regression.

Host validation: the exact driver passed Python compilation, isolated
exact inventory checks (five negative inventory tests) and mocked
deck insertion checks (three negative shapes). Full integrated
preflight runs before live submission; local full checkout remains
blocked by DNS. No fresh IFOX/IEWL/GO result claimed.
