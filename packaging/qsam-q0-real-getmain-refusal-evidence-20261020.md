# Milestone QSAM — Q.0 real conditional GETMAIN refusal (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (**open**).
**Job:** 2177 / `QS0NOMEM`; **Status:** PASS on MVS 3.8J / Hercules TK5.
**Source:** Owner-supplied full JES/IFOX/IEWL/QOUT output on 20 October
2026 from the guarded tracked probe
[`make-shortage-job.py`](../bootstrap-toolchain/probes/q0-qsam-resource-probes/README-shortage.md).

| Step | Program | Observed result |
| --- | --- | --- |
| ASM | IFOX00 | RC=0000, no statements flagged |
| LKED | IEWL | RC=0000 |
| GO | `Q0NOMEM` | RC=0000, normal completion |

Exact QOUT marker:

```text
Q0 REAL GETMAIN RC4 ROLLBACK 3 ALLOC 3 FREE PASS
```

The GO step had `REGION=256K`. The assembler listing shows exactly one
conditional `GETMAIN RC,LV=1048576` (1 MiB), in addition to three small
successful 80/96/80-byte acquisitions. The program saved the actual
nonzero MVS return in `BIGRC`, compared it with `4`, and could reach the
PASS marker only after validating `BIGRC=4`. The allocation refusal thus
returned control with **R15=4**; it was not a synthesized failure.

After that real refusal, it released the pending setup's 96-byte B
allocation; checked that the independent 80-byte A allocation and its
sentinel bytes remained intact; obtained, verified, and freed an 80-byte
D allocation; then released A. Its counters confirmed **3 successful
small allocations, 3 releases, and 0 live allocations**. JES reported
no abend. The intentionally oversized 1 MiB allocation was refused and
thus did not need to be freed. All temporary job artifacts were handled
by the existing Q.0 harness; no accepted PDS module was replaced.

**Precisely supported conclusion:** under the tested TK5 job setup, a
conditional oversized GETMAIN request can fail with returned R15=4,
allow rollback without harming an unrelated region, and allow subsequent
small allocations. This supports the approved plan to translate
returned-control allocation failures into `QS_ERR_RESOURCE=-11` in the
future production BCPLQSAM.

**Limitations:** Does not prove every allocation failure is recoverable,
a universal storage ceiling, 16 simultaneous handles, that QSAM CLOSE
succeeds after an OPEN/alloc failure, or that a pending logical record
survives allocation failure. Eager private staging *before first GET*
is still required. No production `QSAMSVC` or Runtime Extensions
registration/finalization was executed.

**Decision:** close the *resource-refusal reconnaissance sub-question*;
retain the independent Q.0 open gate pending the remaining documented
contract and implementation decisions.
