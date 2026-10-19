# 127 — Repeated FIND must preserve live handle identity

**Status: ACCEPTED, candidate-only DEVOBJ regression.** The first
compiled-BCPL execution (Cambridge JOB 6794, native JOB 6795) assembled
and linked cleanly but GO abended **S013-C0** with
`IEC141I 013-C0,IGG0199G,RG127R,GO,DD01`, consistent with opening
an already-open instream DD twice.

Source commits `9c9dcb4` and `04ebb84` inserted a live-handle lookup
before RDJFCB and QSAM OPEN, reusing the active name/direction identity.
Operator staged revised BCPLIO via JOB **6796**; DEVOBJ-only BLDDEVI
launcher JOB **6798**, payload JOB **6799**, reported IFOX00 ASMIO
RC=0000 and IEBGENER PUTIO RC=0000, with zero flagged statements.
The same compiled-BCPL regression 127 then reported **PASS 1 / FAIL 0 /
SKIP 0 / TOTAL 1** with the standard DEVOBJ candidate variables. The
operator did not supply individual GO step JOB numbers in that positive
run; the runner accepted its normal completion and logical-record
fixtures. **The duplicate FIND targeted gate is accepted**, pending
full post-change compatibility revalidation.

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

**Acceptance evidence:** candidate BCPLIO build JOB 6799 and
targeted regression 127 PASS, as described above. The test still does
not cover reopening a DD after close, nor FINISH/STOP cleanup of
unclosed streams. Those need separate cases. Combined JES output does
not independently prove physical REPORT DD attribution.
