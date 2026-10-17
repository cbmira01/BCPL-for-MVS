# 133 — Mixed dynamic input/output stream interleaving

**Status: ACCEPTED for the candidate's logical M3 mixed-stream gate
(2026-10-17); full 00..133 compatibility panel not yet executed.**
The operator pulled `main` from `c4f7a8d` through `b25d643`
and ran `tools/native/run-regression 133 --show-output` using
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`. Result:
**PASS 133; 1 PASS / 0 FAIL / 0 SKIP / TOTAL 1**.

The candidate runtime was not changed to obtain this result.
PASS establishes the checked logical record ordering and interleaved
cursor/buffer behavior, **not** exact physical JES DD association.
A future lossless DD attribution test must verify the real REPORT
and REPORT2 SYSOUT streams independently under M5.

M3 focused compiled-BCPL candidate regression for two independent
input DD DATA streams (DD01 and DD02) and two independently
allocated output SYSOUT streams (REPORT and REPORT2). All four
streams must be open simultaneously.

The program begins a partial output record on each destination,
switches to different input streams to consume record data,
resumes the output records, and verifies the complete logical
output in both named fixtures. Additional records are emitted
after crossing input record boundaries and reaching EOF. It
explicitly closes input and output streams and verifies primary
SYSPRINT selection is restored.

Success requires normal GO RC0000 and exact primary record
`BCPL MIXED STREAM OK`, plus ordered logical fixture records:
REPORT = `REPORT AB`, `SECOND 1`; REPORT2 =
`REPORT2 QR`, `SECOND 2`. Any assertion fails via STOP(8).
The existing record checker verifies logical records in the
combined JES report; it **cannot establish physical DD attribution**
or preserve significant trailing spaces. Those remain M5 gates.

No compiler or BCPLIO source modification was made to stage
this test. This test is a focused M3 coverage extension and
does not retroactively change accepted M2 behavior.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 133 --show-output
```
