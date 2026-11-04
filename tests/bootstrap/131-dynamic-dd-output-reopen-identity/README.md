# 131 — Dynamic output DD close/reopen: new handle identity

**Status: ACCEPTED under the DEVOBJ candidate (17 October 2026).**
After pulling repository head through `2a56367`, the operator ran
`tools/native/run-regression 131 --show-output` using
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`. Result:
**PASS 131, PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.

This is positive compiled-BCPL evidence for a new nonrecycled
opaque output handle after ENDWRITE, retirement of the original,
duplicate FIND returning the current live identity, and ordinary
record output across both lifetimes. It does not prove DD-specific
physical JES attribution, nor any input DD DATA rewind semantics.
The prior full 00..129 suite (129 PASS, expected skip 083) was
accepted separately; the full 00..131 suite has not yet been rerun.

This permanent compiled-Cambridge-BCPL test targets the approved
M0 contract that **ENDWRITE retires a handle permanently** and a
later FINDOUTPUT of the same normalized DD name creates a new
logical lifetime with a **different opaque BCPL handle**. Repeated
FIND while the new lifetime is still open must return its same
active handle (without opening another QSAM DCB).

The JCL supplies REPORT as a QSAM FB132 SYSOUT DD. The program
opens REPORT, writes the newline-terminated logical record
`REPORT FIRST`, ENDWRITEs, and verifies that its old handle
cannot be reselected. It opens the **same DD** using lowercase
`report`, requires a nonzero handle unequal to the retired one,
verifies the new duplicate FIND returns this second handle,
and proves selecting the retired handle cannot displace an
already-selected active handle. It writes `REPORT SECOND`, closes
it, and verifies both retired handles remain invalid. The primary
output marker is exactly `BCPL REOPEN OK`.

Assertions STOP(8), while only successful GO RC0000 may PASS.
The harness checks expected primary and REPORT logical records.
It does **not** prove lossless physical JES DD attribution.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 131 --show-output
```

**Remaining evidentiary boundary:** The combined-JES checker
accepted both REPORT logical records, but no DD-specific spool
capture was supplied. Therefore the result does not establish
physical substream layout or exact DD attribution. The installed
runtime was not modified for this test. A separate future input
DD reopen probe must respect non-seekable DD DATA semantics;
output reopening does not prove input rewind.
