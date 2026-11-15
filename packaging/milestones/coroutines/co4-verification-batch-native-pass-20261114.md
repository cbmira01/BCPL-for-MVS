# CO.4 — Three-case STACK/CHURN/BUSY batch: native PASS record

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Source revision:** `976c20da29943a72867195a24e010afe4e395e1a`
**Reported:** 14 November 2026, Louisville local time (15 November UTC)
**Classification:** **OWNER-REPORTED NATIVE-MVS-TESTED**; raw JES unreviewed here.

After a guarded fast-forward to the exact revision, the owner ran the
native batch runner from the WSL checkout. The following exact compact
outcome was supplied:

```text
CO.4 STACK PASS
CO.4 CHURN PASS
CO.4 BUSY PASS
CO.4 batch PASS (3/3)
CO.4 batch evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-verification-batch/20261115T023637Z-n7h_hi5x
CO.4 batch RC=0
```

The accepted batch runner inherits the independently compiled
Cambridge and 4-IFOX/IEWL/GO driver and checks per-case exact ordered
oracles (STACK 6, CHURN 7, BUSY 10 application output records), JES
SUCCESS and zero return codes. The reported PASS indicates that the
strict native runner accepted all three cases in sequence. Individual
compiler and native JES job identifiers, the raw `job-report.log`
contents, JCL and compiler/assembler listings were not supplied here
and have not been independently inspected. The local evidence directory
is authoritative for those underlying receipts.

This run follows the separately retained first-attempt compiler FAIL
in JOB 5404 at revision `6d6ee095b68253ecd175055fdaa2218a6eba0298`.
That FAIL is not reclassified as PASS; the corrected fixture was
committed in `976c20da29943a72867195a24e010afe4e395e1a` and tested
in a fresh session.

**Verified at runner level:** accepted-stack metadata/guard positive
paths and checked recursion/suspension, repeated two-worker
creation/deletion and survivor continuity, known-live busy/parent
refusal, and successful cleanup.

**Not yet proven by this run:** actual live STKLIM/APLIMIT machine
values, independent MEMSTAT allocation balance, deliberate allocator
failure/rollback, true MVS storage exhaustion, general stale-address
or ABA protection, or terminal overflow behavior. Those require
separate source-revision-tracked evidence.

**CO.4 remains IN PROGRESS; CO.5 remains NOT STARTED.**
