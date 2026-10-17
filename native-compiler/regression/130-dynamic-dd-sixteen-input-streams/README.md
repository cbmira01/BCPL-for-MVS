# 130 — Sixteen simultaneous dynamic input DD streams

**Status: ACCEPTED — M2 16-stream target passed on DEVOBJ.**
The original unrolled source failed before native execution during
Cambridge JOB 7328: COMP ICINT19 RC0000; SVCODE IEBGENER RC0012.
Commit `ded524f` compacted only the BCPL test source, preserving
all its sixteen simultaneous DD opens and all contract assertions.
The operator pulled through `8247e98` and reran the unmodified
candidate runtime with the revised test. The runner reported
**PASS 130, PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.

The passing regression establishes independent state and selection
for **sixteen simultaneously live** dynamic input DDs. It does not
establish any artificial 16-stream ceiling. No further concurrency
escalation is planned. The complete `00..129` candidate baseline
was separately accepted previously (129 PASS, expected SKIP 083);
a fresh full `00..130` sweep has not yet been supplied. The first candidate-only
MVS run used the original 438-line unrolled BCPL source. Cambridge
JOB **7328 RG130C** reported `COMP ICINT19 RC=0000` but the next
`SVCODE IEBGENER RC=0012`; the driver could not recover generated
assembler, and no native IFOX/LKED/GO execution took place.
This does **not** establish a sixteen-stream runtime failure.

Source-only commit `ded524f` replaces repetitive unrolled assertions
with previously regression-validated `FOR` loops and variable vector
subscripts, reducing source from 438 to 121 nonterminal lines while
retaining sixteen simultaneous FINDINPUTs, all 120 pairwise identity
comparisons, independent data/newline/EOF tests, and stale-handle
checks. The DD fixtures, expected record and DEVOBJ objects are
unchanged. Its retest completed successfully as described above.

The exact reason for IEBGENER RC0012 is **not yet established**.
JOB 7328's detailed compiler/SVCODE report will be needed if the
compact test also fails. Avoid asserting that source size alone
caused the error.

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
