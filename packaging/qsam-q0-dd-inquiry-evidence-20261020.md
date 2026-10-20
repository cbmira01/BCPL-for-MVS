# Milestone QSAM — Q.0 non-opening DD inquiry evidence (2026-10-20)

**Status:** MVS 3.8J / Hercules TK5 PASS; standalone test-only assembly. **March:** Q.0 — Reconnaissance & contract remains open. No BCPLQSAM implementation or Runtime Extensions registration was tested.

## JOB 2170 — QS0DDCHK

Source authority: `bootstrap-toolchain/probes/q0-qsam-error-path-probes/dd-inquiry.asm` and `make-jobs.py`; submitted from the owner checkout. The owner supplied the complete JES/printer report on 20 October 2026, which was inspected for the result below. The complete report remains in the owner's environment, not committed to Git. The generated JCL was local and ignored.

| Step | Program | Completion |
| --- | --- | --- |
| ASM | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Temporary Q0DDMOD | RC=0000 |

Reader/diagnostic SYSOUT:

    Q0 DD RDJFCB PRESENT=0 MISSING=4 PASS

The IFOX listing shows two `RDJFCB ((2))` expansions (each issuing SVC 64), first with `QPRES` and then `QMISS`. The program required R15=0 for `QPRES` and R15=4 for `QMISS` before outputting the marker. JCL explicitly allocated `QPRES` to temporary `&&Q0PRES` using `UNIT=SYSDA`, `RECFM=FB`, `LRECL=80`, `BLKSIZE=800`; **no QMISS DD** was supplied. JES allocated QPRES on device 0290 / WORK01 and deleted the dataset at step end. Only QOUT was opened for writing the marker. Neither inquiry DCB was opened.

## Interpretation and limits

On this MVS/TK5 configuration, a non-opening `RDJFCB` inquiry correctly distinguished a present JCL DD allocation from a missing one. This supports using the existing `BCPLIO.DDVERIFY` mechanism as a precedent for an optional `BCPLQSAM` pre-OPEN allocation check.

The specific missing-DD R15=4 is established for this test. **Do not infer** that *every* nonzero RDJFCB code means the DD is missing, that an allocated DD is compatible with the requested OPEN, or that OPEN would return control on failure. The experiment did not exercise incompatible DCB geometry, SYNAD, failed CLOSE, or an actual `BCPLQSAM` OPEN. `QS_ERR_NO_DD` should be reported only when missing allocation has been reliably established.

A subsequent [opt-in incompatible-OPEN experiment](../bootstrap-toolchain/probes/q0-qsam-error-path-probes/README.md) is prepared separately to characterize an intentionally invalid FB DCB. This is not part of JOB 2170 and does not yet have MVS execution evidence.

**Q.0 remains open; Q.1 has not started.**