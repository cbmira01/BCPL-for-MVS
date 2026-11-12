# CO.0 — Formal closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract  
**Date:** 12 November 2026  
**Owner decision:** **ACCEPTED AND CLOSED**, explicitly authorized 12 November 2026  
**GitHub review checkpoint:** `b8983d083e3f70a697324774a2298b995dbe038a`  
**Next march:** CO.1 — Native ABI and Stack Architecture (**NOT STARTED**)

## Acceptance

The owner explicitly directed **immediate formal closure of CO.0**
after review of the
[qualified CO.0 acceptance candidate](co0-acceptance-candidate-and-co1-transfer-20261112.md).
The CO.0 milestone gate is accepted: an evidence-classified behavioral
specification, historical/source provenance, reproducible interpreted
MVS test evidence and a preserved open-question ledger are recorded.
This acceptance is **qualified** and does not reclassify unverified
items as tests.

## Accepted behavioral evidence

The [behavior ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md)
records accepted interpreted behavior for call/yield/resume and
continuation/value transfer (including JOB 5322), ordinary worker
return/re-entry (JOB 5324), valid-descriptor rejection (JOB 5325),
and bounded allocation/deletion/reuse tests (JOBS 5326–5330).
The [CO0-U08 comparison matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md)
freezes exact interpreted outputs for JOBS 5331 (8/8), 5332
(14/14) and 5333 (18/18), **40/40** total; each had interpreter CODE=0,
runner RC=0, JES 12/12 RC=0000. Independently rechecked JES
receipts do **not** represent new program executions or native tests.

The earlier [canonical MR10 panel acceptance](co0-canonical-default-mr10-jes-5272-5283-acceptance-review-20261111.md)
recorded 12/12 PASS at its cited revision and 142/142 zero JES RC.
The five legacy development probes, after canonical promotion, were
**4 PASS / 1 FAIL**: original fixed-stack JOB 5318 **failed**;
the separately identified corrected-frame candidate JOB 5321 passed
10/10. Do not claim unqualified five-case compatibility or silently
replace the historical golden. See the [CO0-U01/U02 record](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md).

All reported coroutine program executions in CO.0 are
**INTERPRETED-MVS-TESTED**, not **NATIVE-MVS-TESTED**.

## Approved design direction carried forward

- **Approach A — historical-style pointer descriptors:** callers use
  opaque-to-client valid, live descriptor pointers. Arbitrary, stale,
  fabricated or freed pointers are outside the supported initial
  release API contract. Generation-validated managed handles
  (Approach B) remain deferred research. See the
  [CO0-U09 owner decision](co0-u09-native-coroutine-ownership-and-stack-decision-briefing-20261112.md).
- **S1 — active stack-limit switching:** each coroutine owns an
  independent stack; switches install the incoming safe limit and
  restore the root limit when returning. The existing checked-entry
  full frame-size constraint remains required. S2 per-check
  indirection is deferred. See the
  [CO0-U09 S1 owner decision](co0-u09-native-coroutine-stack-check-integration-investigation-20261112.md).

These are approved **architectural directions**, not an approved native
descriptor layout, machine register-save set, global assignment,
linkage/registration design or tested native stack implementation.

## Explicit accepted limitations and CO.1 transfer

The [historical audit](co0-historical-source-audit-20261110.md)
identifies the original KM10 sources and missing
`KM10.COMAIN`. Exact historical internals and a complete
cycle-by-cycle interpreter trace are not recovered. Unsafe
stale/invalid-pointer cases remain untested by design. Bounded
negative SIZE probes do not establish all allocation safety.
Native execution, stack-check integration and ABI behavior remain
**UNVERIFIED**.

CO.1 must resolve actual CG370 calling/register liveness; first
activation and continuation/save layout; root and worker descriptor
fields/lifecycle; allocation, guards and exceptional cleanup; S1
active-limit update ordering and stack diagnostics
(`STACKBASE`/`STACKEND`/`STACKHWM`); Global Number Registry
collision review; proper callable export/registration; and isolated
IFOX/IEWL/GO/JES probe specifications.

The [CO.1 transfer register](co0-acceptance-candidate-and-co1-transfer-20261112.md)
is the detailed list of these remaining design responsibilities.

## Authority and change boundary

**CO.0 is CLOSED, with the qualifications above. CO.1–CO.5 remain
NOT STARTED.** Closing CO.0 does not authorize CO.1 implementation,
JES submission, resident MVS dataset alteration, global allocations
or runtime promotion. CO.1's gate requires an owner-reviewed native
design and isolated probe plan before implementation. The formal
closure does not imply any of CO.2–CO.5 are started.
