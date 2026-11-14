# CO.3 — Parent-chain native test failure, evidence classification pending

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (IN PROGRESS)  
**Source tested:** GitHub main at a09e371edb3ca75c09ae8c0580ff09d0cb7f1ed0  
**Date:** 14 November 2026  
**Classification:** OWNER-REPORTED NATIVE-MVS-FAILED; failing step not yet established

The owner executed the isolated parent-chain candidate and reported
runner RC=1 with the message:

    CO.3 first lifecycle FAIL: native GO job did not complete RC=0

Saved operator-local evidence:

    workarea/co3-first-lifecycle/20261114T190836Z-v_koeeti

That broad message was emitted when the overall JES job summary was not a
zero-RC success; the runner checked this BEFORE individual IFOX/IEWL/GO
step outcomes. It does NOT by itself prove that GO executed, or that
RESUMECO, IFOX, IEWL, or the test oracle caused the failure.

The raw operator-local result.json, job-summary.log and job-report.log
have not been furnished to the assistant. Native JES job number, step
RCs, program output markers and abend status therefore remain unknown.
Preserve this result as a failure, not a passing test.

An isolated read-only inspector at tools/coroutines/inspect-co3-evidence.py
can report the saved native job identity, completed steps, job status,
application markers and selected MVS abend diagnostics. It submits NO JCL,
runs NO compiler/native job and changes NO MVS datasets. The runner's
misleading generic error text is corrected for subsequent executions.

The first lifecycle positive-path JOBS 5384, 5385 and 5386 remain a
separate owner-reported PASS; this failed parent-chain attempt does not
alter those receipts. Do not modify RESUMECO or accepted runtime objects
until the actual failing step has been established.

**Disposition:** CO.3 IN PROGRESS; CO.4 and CO.5 NOT STARTED.
