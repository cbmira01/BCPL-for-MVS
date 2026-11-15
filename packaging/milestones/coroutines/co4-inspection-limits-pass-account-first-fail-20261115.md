# CO.4 — Inspection batch: LIMITS native PASS; ACCOUNT early oracle FAIL

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Tested GitHub `main`:** `b0ce46fd965d1ca7720594fc5516ad7dd12f3993`
**Reported:** 15 November 2026 (UTC)
**Classification:** OWNER-REPORTED NATIVE-MVS-TESTED (mixed PASS/FAIL)

The owner supplied:

```text
CO.4 LIMITS PASS
CO.3 first lifecycle FAIL: wrong ordered BCPL records: ['FAIL']
CO.4 ACCOUNT FAIL
CO.4 inspection batch FAIL (1/3)
CO.4 inspection evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-inspection-batch/20261115T132404Z-dnfqqr22
CO.4 inspection batch RC=1
```

**LIMITS** passed its full inherited native JES/step checks and the 12-record
`CO4LIM` oracle under the tested revision. This is reported through the
strict coordinator; no raw individual JES job numbers were supplied.
The test-only `CO4PROB` R10 repair therefore has a positive target result
for the LIMITS program, unlike the prior native S0C1 on JOB 5419.

**ACCOUNT** failed its strict oracle with exactly the single `CO4MEM FAIL`
record. Its first positive `CO4MEM INIT` marker was absent. Therefore the
failure occurred during initial observer-vector allocation, initial
`CO4PROB`, `CO3INIT`, or the first `SNAP` assertion before `INIT`.
The inherited oracle assessment occurs only after the successful native
JES gate; it is not an IFOX/IEWL/JCL/abend failure. The particular early
assertion is **not** identified by the original one-record output.

**DENY** was not attempted because the original coordinator stops on any
case failure. The run remains an overall **FAIL (1/3)**, not a passed batch.
The owner-local receipt directory is preserved. No changes to installed
`BOOT_OBJ`, approved Core Runtime, or native coroutine ABI are inferred.

## Test-only follow-up (not a diagnosed production defect)

The new follow-up continues verification efficiently without re-running the
unchanged, now PASS, LIMITS fixture. ACCOUNT and DENY now use the same
private G!305 probe-vector pattern as the native-PASS LIMITS fixture:
`PROBEPTR` + a two-parameter `SNAP(N,B)` helper, rather than passing
`P,N,B` through the old three-parameter helper. This removes a difference
between test fixtures but **does not establish a compiler argument ABI bug**.

Both programs emit bounded, exact `F*` markers only on failure paths to
localize allocation/probe/current-context/count/byte/peak disagreements.
Their original successful record sequences and expected byte/count values
are unchanged. The new two-case coordinator continues after an ordinary
zero-RC native output-oracle mismatch, but stops immediately on a failed
compiler, JES step, abend, evidence extraction or infrastructure error.
Each attempt receives separate evidence and the overall batch cannot pass
while either case fails.

**Pending:** native run of ACCOUNT and DENY at the new GitHub commit.
**CO.4 IN PROGRESS; CO.5 NOT STARTED.** No promotion or closure.
