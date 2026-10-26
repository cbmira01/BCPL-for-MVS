# Milestone QSAM — Q.1 diagnostic JOBs 6608–6609

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton
**Evidence:** Operator-supplied WSL transcript; MVS JES 26 October 2026,
02:47:06–02:47:07.
**Disposition:** Diagnostic **GO RC=0012**, **not accepted**; Q.1 OPEN.

## Validated steps

The operator fast-forwarded GitHub `main` to
`43ea8af02badef7448d201103b667a1aa080d963`.
Q.1 source invariants passed; all six three-DD generator tests and all
four descriptor-diagnostic tests passed. The temporary-only synthetic
JCL check passed (2800 cards). The demoted Cambridge compiler under
ICINT19 generated native System/370 source successfully in JOB 6608,
host RC=0. JOB 6609 ran the protected temporary `Q13DD` test.

`ASMWR`, `LKWR`, `ASMA`, `ASMN`, `ASMR`, `ASMQ`,
`ASMG`, `LKED` and temporary F1024 writer `WGO`:
**all RC=0000**. Native `GO`: **RC=0012**.
Highest JES RC 0012; assembler highest severity 0, flagged statements 0.
The job-summary command returned host RC=1 and the printer report was
collected successfully, host RC=0, under
`workarea/bcplqsam-q1/q13dd-diag-6609-report.txt`.

## Runtime record excerpt

The operator's GO-suffix diagnostic filter showed:

```text
Q13D START
Q13D CALL 01 RC=6
Q13D CALL 02 RC=-1
Q13D ASSERT 01 BEFORE
Q13D CALL 03 RC=-3
Q13D CALL 04 RC=6
Q13D QUERY I0/I1/I2=1 1 0
```

The returned QUERY fields `I!0=1`, `I!1=1`, `I!2=0`
are **correct** under the approved six-word descriptor contract.
The very next BCPL source statement is
`WRITES("Q13D QUERY I3/I4/I5=")`; the report filter supplied to
this review did not show that line or any subsequent marker.

**Important distinction:** The filtered GO records alone do not prove
the program counter stopped at that statement. Buffered output,
a partial non-`Q13D` line, an unreported runtime message, or other
GO/JES output may explain the missing marker. The source assertion
`IF I!0 NE 1 | I!1 NE 1 | I!2 NE 0 DO STOP(8)` occurs
**after** both descriptor-print groups. A prior suggestion that
the first-three-word comparison itself failed was not established.
GO RC=0012 must not be identified as `STOP(8)` without further
independent evidence.

No `OPEN`, `INFO`, or `CLOSE` service call is observed in this
diagnostic trace; first QSAM OPEN remains unverified. The nine
successful prerequisite steps do not establish that Q.1's live QSAM
resource model works.

## Next step before any new JES submission

Inspect the **existing full report** from JOB 6609, particularly
the raw output after the final IEWL `AUTHORIZATION CODE IS`
boundary, including non-`Q13D` lines, trailing fragments, and
GO/JES/abend messages. Do this once from WSL without fail-fast or
rerunning Q13DD. Preserve the prior reports for JOBs 6605 and 6607.

No `bcplqsam.asm` modification, ownership-policy change,
increase beyond GO REGION=256K, or milestone acceptance is
authorized by this observation. If the complete report remains
inconclusive, choose the smallest separately instrumented diagnostic
test before modifying the QSAM core.
