# R.2 - Consolidated acceptance campaign

**Status:** Candidate runner; actual MVS campaign not yet executed.
R.2 remains ACTIVE. No accepted object promotion.

From repository root, run the host-only preflight:

```sh
python3 tools/bootstrap/run-r2-acceptance --check
```

To compile all four BCPL callers, submit one 0/A/B/A+B MVS matrix job
and one 21-case negative/dependency batch job, then verify JES results
and extract a consolidated evidence package:

```sh
python3 tools/bootstrap/run-r2-acceptance --execute
```

The runner prints a path to `SUMMARY.md` under
`workarea/runtime-extensions-r2/acceptance/<UTC timestamp>/`. Submit
that summary, results.json and any failure report for review. Do not
commit private authenticated JCL or raw JES printer captures.

It checks the 14 assembler, 4 link and 4 GO steps of the positive
matrix, the exact four BCPL output markers, and four IEWL symbol maps.
The negative job checks every assembler, the 21 independent link
results, expected live diagnostics 1001-1014, GO RC=0012 on rejection,
no publication of G!203/G!299 before START, one successful dependency
link/run, and non-execution after an intentionally unresolved link.

Expected failures are **success conditions only for their named case**.
They must not skip later MVS steps. Host preflight does not prove MVS
execution. No PDS installation or R.2 closure is implied by a PASS.

See [consolidated acceptance design](../../../packaging/runtime-extensions-r2-consolidated-acceptance-design-20261022.md).

## JOB 3086 JCL rejection and correction (22 October 2026)

The first consolidated attempt on Git revision `4134703` passed its
positive matrix as **JOB 3085** (all 22 steps RC=0000). The negative
batch was assigned **JOB 3086** but JES rejected it **before execution**
with `IEF452I R2NEG JOB NOT RUN - JCL ERROR`. No negative/runtime
acceptance tests were completed in that attempt.

The generated IEWL `EXEC` records incorrectly ended their
`PARM='NCAL,LIST,XREF,MAP'` operand with a comma immediately before
a new `//OBJ DD` statement. The comma requires a continuation of
the EXEC parameters; it is not valid there. The generator now removes
that comma, and a host regression asserts this boundary for all 21
link steps. **Real MVS retest still required.**

Use the same `python3 tools/bootstrap/run-r2-acceptance --execute`
entry point after `git pull --ff-only`. Do not mark R.2 ready for
closure until the revised negative batch passes actual MVS checks.
