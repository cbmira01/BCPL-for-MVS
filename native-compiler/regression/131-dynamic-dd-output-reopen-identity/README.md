# 131 — Dynamic output DD close/reopen: new handle identity

**Status: STAGED candidate-only RED/UNKNOWN gate; NOT RUN OR ACCEPTED.**

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

**Important unknown:** whether repeated OPEN of the same MVS 3.8
SYSOUT DD creates two SYSOUT substreams that the current
combined-JES record checker will preserve in logical record
order. If this fails, inspect GO RC/IEC/IEF diagnostics and
actual JES SYSOUT before changing the runtime or expected
fixture. The runtime was **not** altered to stage this test.
A separate future input-DD reopen probe must respect non-seekable
DD DATA semantics; output reopening cannot prove input rewind.
