# Milestone QSAM — Q.1 native three-DD negative evidence (JOBs 6604–6605)

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**Evidence date:** 26 October 2026 (MVS JES)  
**Disposition:** Three-DD native execution **NOT PASSED**; Q.1 **OPEN**.

## Operator-observed preparation and submission

With GitHub `main` at `72903a9db914e3c8c77c6cde92d87181abf0fc8a`,
the operator ran `check-q1-offline.py` (PASS: 181 labels,
123 branches, 16 slots, 32 DCBs), **six**
`test_prepare_q1_3dd.py` host tests (all OK), and synthetic
`prepare-q1-3dd.py --check` (PASS: **2800** cards).
The demoted Cambridge compiler under ICINT19 returned **JOB 6604**,
saved System/370 `CODE` into ignored
`workarea/bcplqsam-q1/three-generated.asm`, and returned host
compilation RC=0. A protected local `q13dd.jcl` was prepared;
the operator explicitly submitted it as **JOB 6605**.

## Native MVS result

From the operator-supplied `job-summary` output:

| Step | Program | Observed completion |
| --- | --- | --- |
| ASMWR | IFOX00 | RC=0000 |
| LKWR | IEWL | RC=0000 |
| ASMA | IFOX00 | RC=0000 |
| ASMN | IFOX00 | RC=0000 |
| ASMR | IFOX00 | RC=0000 |
| ASMQ | IFOX00 | RC=0000 |
| ASMG | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| WGO | Temporary Q.0 F1024 writer | RC=0000 |
| **GO** | **Native BCPLQSAM three-DD application** | **RC=0008** |

JES job `Q13DD` ran **26 October 2026 01:35:32–01:35:33**
(MVS job clock). `JOB RESULT: FAILURE`,
`HIGHEST RC: 0008`, IFOX statements flagged **0**,
highest severity **0**. `job-summary --max-rc 0` returned
host RC=1, and `dump-report-for-job` collected the report
successfully (host RC=0) at
`workarea/bcplqsam-q1/q13dd-report.txt` on the operator workstation.

The previous WSL evidence checker did **not** run the expected-output
record check because the job summary returned failure. Therefore the
provided transcript does **not** establish whether the marker
`BCPLQSAM Q1 THREE DD PASS` was present; its absence must not
be inferred from a skipped check. The *full JES report*, diagnostic
messages and any BCPLREG 2001 finalizer output have **not** yet been
provided for this review.

## Interpretation and next action

The assembler, linker and temporary F1024 writer steps succeeded.
Failure is confined to the GO step in the supplied summary.
The BCPL fixture explicitly calls `STOP(8)` when any QUERY,
OPEN, INFO or CLOSE assertion fails. A generic finalizer error
may also yield an RC=8 under the accepted Runtime Extensions policy.
**GO RC=8 alone cannot distinguish these paths**, nor identify
a failed OPEN, a geometry mismatch, or a returned-CLOSE failure.

Do **not** change QSAM ownership semantics, alter production
`BCXCAT`/`BOOT_OBJ` objects, raise GO REGION above **256K**,
or retry JOB 6605 without reviewing the saved JES report first.

Extract failure messages and the **GO suffix** from the existing
`q13dd-report.txt`. If they are insufficient, introduce an
explicitly test-only stage/return-code instrumented BCPL caller,
not a speculative assembler fix. Preserve this negative evidence
alongside the successful Q.1 IFOX, IEWL and QUERY-only gates.

No Q.1 closure or acceptance is implied.
