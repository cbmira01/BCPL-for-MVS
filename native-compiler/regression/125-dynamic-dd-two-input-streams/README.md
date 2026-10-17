# 125 — Compiled BCPL, two dynamic input DD streams

**Status: ACCEPTED** for the modular DEVOBJ candidate. The initial
test-first run was intentionally red (JOB 6275, GO RC0008); the
implemented dynamic FINDINPUT and subsequent R10/R11 return correction
made the same compiled-BCPL test pass after BCPLIO was rebuilt in
JOB 6289 (IFOX/PUTIO RC0000, no assembler flags).
The successful native regression 125 reported PASS 1/FAIL 0/SKIP 0.
Subsequent compatibility runs also passed tests 113 and 124 and the
complete 00..123 panel (123 PASS/0 FAIL/expected SKIP 083).
See `docs/Milestone-BCPLIO-dynamic-stream-M1-progress.md`.

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
test. Test 126 now stages the corresponding 12-DD concurrent-stream stress case. Combined
JES output comparison does not independently prove SYSPRINT DD identity.
