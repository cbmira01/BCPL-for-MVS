# 130 — Sixteen simultaneous dynamic input DD streams

**Status: STAGED for first MVS execution. NOT YET ACCEPTED.**

This permanent candidate-only compiled Cambridge-BCPL regression is
the M2 concurrency threshold beyond the twelve-stream regression 126.

JCL supplies sixteen distinct dynamically named FB80 input allocations
`DD01` through `DD16` using the existing generic input-DD fixture
mechanism. Each DD contains two distinct one-character records:
the first-record values `A` through `P`, then `Q` through `Z`
followed by digits `0` through `5` for the second records.

Source opens **all sixteen** before any reading, checks sixteen
nonzero and all 120 pairwise-distinct stable stream handles,
interleaves reads in three complete rounds while checking independent
cursor, newline, EOF and UNRDCH behavior, and closes streams in
reverse order while rejecting each stale selection.

Success requires normal GO RC0000, the exact primary record
`BCPL SIXTEEN INPUT OK` and PASS 130. A nonzero GO, compiler or
IFOX/IEWL failure, unexpected abend, or missing marker is FAIL.
This is evidence for 16 concurrent streams, not an assertion that
the host supports an unlimited number or that arbitrary DD limits
do not exist. The runtime and compiler are not changed by this test.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=DEVOBJ
export BCPL_RUNTIME_CANDIDATE=1
export BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6
tools/native/run-regression 130 --show-output
```

Reopen-after-close identity, deterministic resource exhaustion,
explicit FREEMAIN accounting and lossless physical DD attribution
require separate tests before full milestone closure.
