# 128 — FINISH drains outstanding dynamic streams

Status: **STAGED RED GATE; not run or accepted.**

This DEVOBJ-only compiled-BCPL test opens two output DDs (REPORT
and REPORT2) and an input DD (DD01). It leaves two partially filled
output buffers and the selected input stream open, writes a primary
SYSOUT completion marker, and executes FINISH without explicit
ENDREAD/ENDWRITE.

Acceptance requires normal GO RC0000 and the expected logical records
FINISH MAIN OK, FINISH REPORT PART and FINISH REPORT2 PART. Unlike
newline-terminated records, both named output records require the
runtime termination path to flush pending application buffers.

The existing IOFIN only closes fixed bootstrap DCBs; this test is
expected to fail before the IOFIN dynamic-descriptor sweep is
implemented. Do not change the immutable fixture merely to make
the test pass. The test cannot independently prove FREEMAIN accounting,
input DCB closure, or exact physical SYSOUT DD attribution.

Run with the four usual DEVOBJ candidate environment flags:
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`, then invoke
`tools/native/run-regression 128 --show-output`.
