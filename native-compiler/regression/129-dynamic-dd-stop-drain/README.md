# 129 — STOP(8) drains outstanding dynamic streams

Status: **STAGED RED GATE; not run or accepted.**

This compiled-BCPL DEVOBJ-only regression is paired with 128 FINISH.
It opens input DD01 and two output destinations REPORT and REPORT2.
Both named output buffers retain unfinished records. It writes a
completed record to primary SYSPRINT then calls STOP(8), with no
ENDREAD or ENDWRITE.

The required GO termination code is RC=0008 (see expected-go-rc.txt),
not an abend. The expected primary marker and both named partial
logical records must be present. Assertion failure paths deliberately
STOP(12), distinguishing them from the intended STOP(8) completion.

The current IOFIN omits dynamic descriptor draining. The first
test-first run is therefore expected to fail due to absent partial
REPORT records. This does not by itself prove FREEMAIN accounting,
input DCB CLOSE, or physical SYSOUT DD attribution.

Run from repository root with
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6,
using tools/native/run-regression 129 --show-output.
