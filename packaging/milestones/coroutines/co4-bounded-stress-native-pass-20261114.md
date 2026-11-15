# CO.4 — Bounded native stress/refusal: owner-reported PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Source revision tested:** `612234b106b5ef450b9d2ee70effd0f39ca96a70`  
**Reported:** 14 November 2026, Louisville local time (15 November UTC)  
**Evidence:** **OWNER-REPORTED NATIVE-MVS-TESTED**, qualified

## Operator report

From the repository root, the owner ran `python3 -B tools/coroutines/run-co4-bounded-stress.py --run` after confirming the exact GitHub revision. The complete console outcome was:

```text
CO.4 bounded stress PASS
CO.4 native execution RC=0
CO.4 evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-bounded-stress/20261115T013519Z-sn_p5kw4
CO.4 runner RC=0
```

The accepted CO.4 runner inherits the CO.3 independent compilation and native job mechanism. Its strict `assess()` requires the expected `CO3BGO` JES identity, JOB RESULT SUCCESS, HIGHEST RC 0000, each of four IFOX steps (ASMA, ASML, ASMM, ASMS), IEWL (LKED) and GO at RC=0000, plus the exact nine ordered `CO4BCPL` records. Its own receipt is `co4-result.json` next to the inherited `result.json`.

**Evidence boundary:** The console output supports that the owner-operated strict runner returned PASS/RC=0 for that source revision. Individual compiler JOB numbers, the native JES JOB number, raw listings, JES summary and exact output lines were **not supplied** in the conversation; they remain in the owner-local evidence directory and have **not** been independently reviewed here. No claim of an independently audited JES receipt is made.

## Scope and limitations

This PASS extends CO.4 evidence to the bounded known-live two-worker stress/refusal fixture: 32 alternating root-to-worker calls, up to four recursive ancestor frames and 30 explicit nested `COWAIT` suspensions, preserved values/locals/root G54/G55 checks, safe target refusal and orderly deletion. The source fixture and runner impose those checks; the observed PASS supports their acceptance at the runner level.

It **does not** establish exact active `STKLIM` or `APLIMIT`, stack overflow boundary behavior, deliberate allocator failure/rollback, ABA-safe identity, stale pointer safety, arbitrary-pointer recovery, or generalized concurrent/reentrant correctness. The separate C4 cases remain in scope. CO.4 remains **IN PROGRESS** and CO.5 **NOT STARTED**. No runtime object was installed or released, no regression identities changed, and the accepted CO.3 receipts remain untouched.
