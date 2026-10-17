# 127 — Repeated FIND must preserve live handle identity

**Status: RED GATE CONFIRMED, FIX RETEST PENDING.** The initial
candidate-only compiled-BCPL execution (Cambridge JOB 6794, native
JOB 6795) assembled and linked successfully but GO abended **S013-C0**
with `IEC141I 013-C0,IGG0199G,RG127R,GO,DD01`. This is a regression
failure, **not** the expected controlled STOP(8). It is consistent
with a duplicate OPEN of an already-open instream DD.

Commit `9c9dcb4` adds pre-OPEN active handle/name lookup in both
dynamic FIND paths. It has **not yet been rebuilt or run under MVS**.
The same immutable fixture is the acceptance test for that fix.

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

**Acceptance target after DEVOBJ-only BCPLIO rebuild:** clean IFOX
and PUTIO RC0000; Cambridge/ASMAP/IEWL success; GO RC0000 without
abend; exact primary and REPORT logical records; runner PASS 127.
Until the MVS operator observes that result, do not declare duplicate
FIND behavior accepted. This test does not yet cover reopen-after-close
using the same DD, nor FINISH/STOP cleanup of unclosed streams. Those
need separate cases. Combined JES output does not independently prove
REPORT DD attribution.
