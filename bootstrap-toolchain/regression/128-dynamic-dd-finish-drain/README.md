# 128 — FINISH drains outstanding dynamic streams

**RED→GREEN GATE ACCEPTED:** Cambridge JOB 7058 compiled; GO payload JOB
7059 assembled and linked RC0000 and exited normally RC0000, but
the primary marker was present while the pending REPORT record was
missing. The harness correctly returned FAIL 128. IOFIN cleanup
source was installed and accepted in JOB 7065.

**Accepted on 17 October 2026 under DEVOBJ.** Operator staged commit
`8597a88` BCPLIO through JOB 7062 and built with BLDDEVI
launcher JOB 7064 / payload JOB 7065: ASMIO IFOX00 RC0000,
PUTIO IEBGENER RC0000, zero flagged statements.
Afterward regression 128 returned PASS 1 / FAIL 0 / SKIP 0.
A complete candidate `00..129` sweep also returned
**129 PASS, 0 FAIL, 1 expected SKIP (083)**. This is the
externally visible cleanup acceptance, not an instrumented
FREEMAIN/DCB accounting proof.

This DEVOBJ-only compiled-BCPL test opens two output DDs (REPORT
and REPORT2) and an input DD (DD01). It leaves two partially filled
output buffers and the selected input stream open, writes a primary
SYSOUT completion marker, and executes FINISH without explicit
ENDREAD/ENDWRITE.

Acceptance requires normal GO RC0000 and the expected logical records
FINISH MAIN OK, FINISH REPORT PART and FINISH REPORT2 PART. Unlike
newline-terminated records, both named output records require the
runtime termination path to flush pending application buffers.

The pre-change IOFIN only closed fixed bootstrap DCBs; its failing
result is retained above. The new IOFIN dynamic-descriptor drain is
validated by this regression. Do not change the immutable fixture merely to make
the test pass. The test cannot independently prove FREEMAIN accounting,
input DCB closure, or exact physical SYSOUT DD attribution.

Run with the four usual DEVOBJ candidate environment flags:
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`, then invoke
`tools/native/run-regression 128 --show-output`.
