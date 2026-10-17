# 127 — Repeated FIND must preserve live handle identity

**Status: STAGED RED contract test**, not yet run under MVS and not
accepted. This is a permanent candidate-only compiled-BCPL regression.

M0's approved duplicate-FIND contract explicitly requires multiple
calls to `FINDINPUT` or `FINDOUTPUT` for the **same normalized DD name,
same direction and same active lifetime** to return exactly the same
BCPL opaque handle, without executing a second QSAM OPEN. A stale
handle must not designate a newly opened stream after ENDREAD/ENDWRITE.

JCL allocations:
- `DD01`: two one-character FB80 DD DATA records A and B
- `REPORT`: FB132 SYSOUT, with `expected-report.txt` fixture

The compiled BCPL test calls `FINDINPUT("DD01")` then
`FINDINPUT("dd01")`, checks equal live handles, reads and switches
between the two aliases while retaining cursor state, and closes the
stream. It then does the same for `FINDOUTPUT("REPORT")` and
`FINDOUTPUT("report")`, writes the expected REPORT logical record
and closes exactly once. Assert failures call `STOP(8)`;
success alone emits `BCPL DUPLICATE OK` and finishes with GO RC0000.

```sh
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 127 --show-output
```

The current BCPLIO implementation of DIFIND and DQFIND appears to
allocate/open a new descriptor on every otherwise valid FIND without
an active-name-and-direction lookup. Thus **a controlled STOP(8) FAIL
is expected** from this first run; record the red gate before changing
the runtime. This test does not yet cover reopen-after-close using
the same DD, nor FINISH/STOP cleanup of unclosed streams, both of
which need distinct tests. The existing combined JES checker does not
independently prove REPORT DD attribution.
