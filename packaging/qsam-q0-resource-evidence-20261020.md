# Milestone QSAM — Q.0 conditional storage and injected-rollback evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (**open**).
**Environment:** MVS 3.8J / Hercules TK5, isolated IFOX assembler probe.
**Subject:** JOB 2175 `QS0RES`, not a production BCPLQSAM module.

## JOB 2175 — QS0RES — PASS

The owner submitted the tracked
[`q0-qsam-resource-probes/make-jobs.py`](../bootstrap-toolchain/probes/q0-qsam-resource-probes/README.md)
JCL and provided the complete JES, IFOX, linker and `QOUT` report for
20 October 2026.

| Step | Program | Observed result |
| --- | --- | --- |
| ASM | IFOX00 | RC=0000; no statements flagged |
| LKED | IEWL | RC=0000 |
| GO | Q0RES | RC=0000 |

The program printed:

```text
Q0 GETMAIN RC ROLLBACK 3 ALLOC 3 FREE PASS
```

The assembler listing shows real `GETMAIN RC` macro expansions
(SVC 120) at lengths 80 bytes, 96 bytes and 80 bytes, and matching
`FREEMAIN R` macro expansions (SVC 10). A surviving 80-byte region
A retained its sentinel bytes `X'5A'` and `X'A5'` when a failed
setup's 96-byte region B was freed; a third 80-byte region C could
then be acquired and freed. The tested accounting ended at three
recorded successful acquisitions, three recorded releases, and
zero live regions. The GO step completed normally and used no
permanent PDS dataset.

**Critical limitation:** The injected `R15=8` was used by the explicit
rollback sequence rather than by the original `FAILED` branch. No
real `GETMAIN RC` allocation failure occurred, and the generic
`FAILED` cleanup routine was not executed on that run. The PASS
marker is therefore evidence for successful MVS acquisition/release,
the specified rollback, and noncorruption of A only. It is not
evidence of actual storage shortage, the untraversed cleanup
branches, complete BCPLQSAM transactional OPEN, QSAM pending-record
preservation, or the maximum number/size of live handles.

## Follow-up — QS0FAIL (prepared, not executed)

The separate
[`failure-path.asm`](../bootstrap-toolchain/probes/q0-qsam-resource-probes/failure-path.asm)
will route an injected nonzero status through the **same `ROLLBACK`
label reached by nonzero `GETMAIN RC` on B/C**. It is intended to
verify C-before-B release, survival of independent A, continuation
with D, and four acquisitions/four frees. This is explicitly
**not yet MVS-verified** and is still not a test of a true storage
shortage or the separate fatal `FAILED` cleanup routine.

**March Q.0 remains open. Q.1 has not started.**
