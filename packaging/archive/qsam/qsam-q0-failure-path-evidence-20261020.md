# Milestone QSAM — Q.0 failed-setup rollback handler evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (still open).
**Probe:** `QS0FAIL` / JOB **2176**, MVS 3.8J / Hercules TK5.
**Status:** standalone IFOX/QSAM-adjacent resource test **PASS**;
not the BCPLQSAM package and not a real storage shortage.

## Observed execution

The owner generated the 230-card JCL with
`bootstrap-toolchain/probes/q0-qsam-resource-probes/make-failure-job.py`,
submitted it on 20 October 2026, and supplied the complete JES, IFOX,
link-editor and QOUT report. JES read 232 cards including the generated
job-card continuation. All three steps passed:

| Step | Program | JES result |
| --- | --- | --- |
| ASM | IFOX00 | RC=0000; no source flagged |
| LKED | IEWL | RC=0000 |
| GO | Q0FAIL | RC=0000 |

The QOUT success marker was:

```text
Q0 RESOURCE FAILED PATH 4 ALLOC 4 FREE PASS
```

## Precisely what passed

The standalone assembler acquired A=80 bytes, B=96 bytes and
C=64 bytes with real conditional `GETMAIN RC` requests, writing
distinctive sentinel bytes. The test then **injected** R15=8 and
branched into the `ROLLBACK` entry, which is also the handler targeted
by nonzero results from the B/C GETMAIN sites. The code executed
`FREEMAIN R` first on C, then B, checked that the handler ran once,
that pointers for B/C were cleared, and that the allocation counters
showed 3 acquisitions, 2 releases and 1 live allocation. It verified
A's original sentinel bytes. It then acquired D=80 bytes, verified
A and D, released D and A, and checked **4 acquisitions, 4 releases,
0 live**. The program completed without a system abend.

**Interpretation:** MVS executed the specific failed-setup rollback
handler and the test's reverse-order ownership logic, not merely a
separate explicit sequence as in [JOB 2175](qsam-q0-resource-evidence-20261020.md).
This strengthens Q.0 resource-lifetime evidence but does not establish
that every possible fault takes this same path.

**Not established:** MVS did **not** return a shortage code from an
unsatisfied `GETMAIN RC`; the failure was synthesized. The separate
fatal `FAILED` cleanup handler was not intentionally exercised. The
probe had no real QSAM file handle, pending record, BCPL request/result
vectors, or production per-handle allocation. It is not sufficient to
accept the optional BCPLQSAM implementation.

## Subsequent guarded experiment — executed and passed

The separate [one-shot conditional GETMAIN refusal experiment](qsam-q0-real-getmain-refusal-evidence-20261020.md)
**passed in JOB 2177**. Its real 1 MiB conditional request, under a
256K GO region, returned R15=4 to the program. This was a genuine MVS
return, unlike JOB 2176's injected failure. It did not establish
BCPLQSAM's maximum record size or automatic extension finalization.

**Q.0 remains open; Q.1 has not started.**
