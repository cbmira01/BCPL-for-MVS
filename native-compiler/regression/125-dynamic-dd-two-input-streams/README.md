# 125 — Compiled BCPL, two dynamic input DD streams

**Status:** Test-first M1 gate, **not yet MVS-validated**. The existing
BCPLIO FINDINPUT recognizes BCPIN and BCPINB but does not yet open
arbitrary DD names. A first run against the currently accepted DEVOBJ
runtime is expected to fail; this is an intentional capability gap, not
permission to weaken the test or its expected success marker.

Program: `source.bcpl`. JCL allocates two independent 80-column
instream DDs via `input-dda.records` (DDA: AB / CD) and
`input-ddb.records` (DDB: 12 / 34). Neither is the historical
built-in BCPIN or BCPINB.

The source exercises:
- FINDINPUT of two arbitrary DDs, nonzero distinct handles
- Switching A -> B -> A and preserving independent character positions
- Independent UNRDCH, record-boundary newline (10) and EOF (-1)
- UNRDCH of EOF without resetting the other stream
- FINDINPUT of nonexistent NOFILE without changing selection
- ENDREAD and rejection of each stale/closed stream handle
- STOP(8) on each failure, with exactly one final SYSPRINT marker

The candidate-only marker prevents this test being counted as a normal
production runtime PASS. The harness selects DEVOBJ BCPLM6/BCPLIO
through the same environment as accepted test 124.

```sh
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 125 --show-output
```

**Acceptance:** resident Cambridge compile, IFOX, IEWL and GO execute;
GO RC=0000, no abend, the exact post-link logical record
`BCPL INPUT OK` appears. No output from an assertion failure can
count as a PASS. Operator must report the run and first failure.

Input is limited here to JES instream DD DATA fixtures. In particular,
this test does **not** assert that an MVS reopen of the same instream DD
rewinds to the beginning. That needs a separately designed DASD-backed
test. Test 126 should extend this architecture to 12 DD names. Combined
JES output comparison does not independently prove SYSPRINT DD identity.
