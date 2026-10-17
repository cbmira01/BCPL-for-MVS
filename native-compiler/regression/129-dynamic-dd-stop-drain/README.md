# 129 — STOP(8) drains outstanding dynamic streams

**RED→GREEN GATE ACCEPTED:** Cambridge JOB 7060 compiled; GO payload JOB
7061 assembled and linked RC0000 and exited at the intended
STOP(8) RC0008, without an abend. The primary marker was present,
but the pending REPORT record was missing; harness returned FAIL
129, rather than accepting the exit code alone. IOFIN cleanup
source was installed and accepted in JOB 7065.

**Accepted on 17 October 2026 under DEVOBJ.** Operator staged commit
`8597a88` BCPLIO through JOB 7062 and built with BLDDEVI
launcher JOB 7064 / payload JOB 7065: ASMIO IFOX00 RC0000,
PUTIO IEBGENER RC0000, zero flagged statements.
Afterward regression 129 returned PASS 1 / FAIL 0 / SKIP 0.
A complete candidate `00..129` sweep also returned
**129 PASS, 0 FAIL, 1 expected SKIP (083)**. This is the
externally visible cleanup acceptance, not an instrumented
FREEMAIN/DCB accounting proof.

This compiled-BCPL DEVOBJ-only regression is paired with 128 FINISH.
It opens input DD01 and two output destinations REPORT and REPORT2.
Both named output buffers retain unfinished records. It writes a
completed record to primary SYSPRINT then calls STOP(8), with no
ENDREAD or ENDWRITE.

The required GO termination code is RC=0008 (see expected-go-rc.txt),
not an abend. The expected primary marker and both named partial
logical records must be present. Assertion failure paths deliberately
STOP(12), distinguishing them from the intended STOP(8) completion.

The pre-change IOFIN omitted dynamic descriptor draining and failed
the test-first run. The corrected implementation passed with the
original unchanged fixtures. This does not by itself prove FREEMAIN accounting,
input DCB CLOSE, or physical SYSOUT DD attribution.

Run from repository root with
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6,
using tools/native/run-regression 129 --show-output.
