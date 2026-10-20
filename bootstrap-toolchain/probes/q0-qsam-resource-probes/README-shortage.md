# Milestone QSAM — Q.0 bounded actual GETMAIN RC refusal experiment

**Status:** MVS PASS in **JOB 2177** (20 October 2026), all three
steps RC=0000 and observed R15=4 from a real conditional GETMAIN.
This standalone IFOX `Q0NOMEM` probe demonstrates a **genuine returned-control failure**
from one conditional MVS `GETMAIN RC` call. It adds no BCPLQSAM
implementation, private handle API, or changes to accepted PDSes.

## Why a single oversized request?

Historical IBM OS/VS2 Supervisor documentation (Release 3.7, predecessor
of MVS 3.8) describes a conditional `GETMAIN RC` returning R15=4
when insufficient storage is available, while an unconditional request
may terminate the job. A 256K REGION with **one** 1,048,576-byte
conditional request tests the supported refusal path without repeatedly
consuming memory. It is an investigation, **not** a claim of an MVS-wide
storage bound. The actual 3.8J/TK5 result is [documented](../../../packaging/qsam-q0-real-getmain-refusal-evidence-20261020.md).

Period documentation: IBM, *OS/VS2 System Programming Library:
Supervisor*, Release 3.7, GC28-0628-2, see the GETMAIN section:
https://manuals.plus/m/ca02f3630a89bf1964845446205823d03875c414cb0f6e1cec1879f5d8da21a4

## Expected experiment

1. Obtain independent area A (80 bytes), set and retain sentinel bytes.
2. Obtain area B (96 bytes), representing unpublished handle setup.
3. Issue **exactly one** `GETMAIN RC,LV=1048576`. With GO
   `REGION=256K`, expect a nonzero R15 (specifically 4).
4. If R15=4, enter `ROLLBACK`, release B, verify A is intact,
   obtain and release 80-byte D, then release A.
5. Require 3 small allocations, 3 frees, 0 live, and output:

```text
Q0 REAL GETMAIN RC4 ROLLBACK 3 ALLOC 3 FREE PASS
```

**Unusual outcomes:** If the 1MiB request **succeeds**, free that entire
allocation immediately using the checked address and the original size,
then clean up A and B and return RC=8. A non-4 error code also returns
RC=8 after pointer-guarded cleanup. If MVS abends, retain the complete
JES report; **never** label it a successful conditional return. There is
no allocation retry loop, and the job sets a one-minute GO CPU limit.

## Operator commands

Run the source-only check first. It does not use credentials or create
an authenticated deck:

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-resource-probes
python3 "$PROBE/make-shortage-job.py" --check
```

**Operator opt-in is required** to generate and submit the request:

```sh
python3 "$PROBE/make-shortage-job.py" --allow-large-getmain
bash tools/mvs/submit-jcl workarea/qsam-q0-resource/q0-shortage.jcl
tools/mvs/dump-report-for-job JOBNUMBER
```

Generation puts mode-0600 JCL under ignored `workarea/`. It may
include job-card credentials; never commit the deck. Expected steps:
ASM RC=0000, LKED RC=0000, GO RC=0000 plus marker. A nonzero GO RC or
ABEND is a useful *negative result*, not an API acceptance result.

No QSAM `GET`/`PUT` is attempted. There is no proof that a real
shortage leaves a pending logical record intact; stage allocations
must precede the first `GET` as already required by the Q.0 design.
March Q.0 remains open; Q.1 has not started.
