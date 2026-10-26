# Milestone QSAM — Q.1 JOB 6605 postmortem inspection

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**Evidence:** Operator-supplied WSL transcript, JOB 6605, JES date
26 October 2026.  
**Disposition:** Native three-DD **GO RC=0008**, **not passed**.

This follow-up supplements
`qsam-q1-native-three-dd-jobs-6604-6605-negative-evidence-20261026.md`.
At GitHub `main` `99dcbc036b0fe2088ca5696896d5e4afd5a33f80`,
all six Python generator regression tests passed. Reinspection
confirmed: `ASMWR`, `LKWR`, `ASMA`, `ASMN`, `ASMR`,
`ASMQ`, `ASMG`, `LKED`, `WGO` returned zero,
while `GO` returned **0008**. The native GO step shows
`VIRT 108K` in the supplied JES `IEF374I` record, but this
measurement cannot be equated to the complete 16-handle resource
gate or proof of successful QSAM OPEN.

The post-link-edit output verifier now **ran** against the saved
`workarea/bcplqsam-q1/q13dd-report.txt`; it reported:
`SYSPRINT: ordered logical records not found in GO suffix`
and returned host RC=1. Thus `BCPLQSAM Q1 THREE DD PASS`
was not present as the expected standalone ordered output record
in that combined JES report. As usual, physical DD attribution
is not established by the combined printer stream.

The final 100 report lines included IEWL MAP/XREF and the normal
`Q13DD`/JOB 6605 banner after
`AUTHORIZATION CODE IS 0`, but **no visible** application trace.
The operator's grep matched `BCPLREG 2001 FINALIZER RETURNED NONZERO`
and `BCPLQSAM Q1 FINALIZER 16 CLOSE PASS` only where those
strings occurred in **IFOX assembly listings**; these are *not*
observed WTO messages from the running application. The transcript
shows no positively identified runtime finalizer diagnostic or
MVS program abend. This does **not** conclusively rule out a
finalizer-related RC=8 or an internal service error.

`test-q1-3dd.bcpl` explicitly uses `STOP(8)` for 19
assertions, so the GO result and missing pass marker are consistent
with an early assertion failure, but the failing assertion and
the returned QSAMSVC code remain **unidentified**.

## Safe diagnostic next step

**Do not modify the approved public API, installed libraries,
returned-CLOSE handling or QSAM assembler merely on inference.**
Compile the test-only `test-q1-3dd-diag.bcpl` on `main`;
it preserves every original call and assertion, but emits
numbered `Q13D` records plus signed return values using the
established `WRITEN:62` Base Library entry. Regenerate the
existing temporary-only three-DD JCL from this compiled caller
and execute another `Q13DD` job at **GO REGION=256K**.
Preserve the new JOB number independently of JOB 6605 and
inspect only lines after the final IEWL authorization boundary
for *executed* diagnostic records, avoiding false positives from
assembler listings.

This instrumented test is exploratory, not Q.1 acceptance.
