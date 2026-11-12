# CO.0 — Formal acceptance candidate and CO.1 transfer

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract  
**Prepared:** 12 November 2026  
**Source authority:** GitHub `main`; pre-acceptance checkpoint `c0ce8c25b9f5036d6fddfbd497b4e5dca51aac6b` plus the subsequent S1 decision update  
**Status:** **READY FOR OWNER REVIEW — NOT CLOSED**  
**CO.1–CO.5:** **NOT STARTED**

## Scope and CO.0 gate

The [governing milestone](milestone-implement-coroutine-support-for-native-compiler.md)
defines CO.0 as an historical/interpreted behavioral research march:
audit MR10 `ICLIB` and BCPL routines, recovered historical tape,
compiler traces, and interpreted test evidence; establish observable
call, yield, resume, value, parent, return/re-entry, deletion and
reuse behavior. The required gate is a **reviewed evidence-classified
behavior table, provenance, reproducible interpreted testing procedure
and explicit open-question ledger**. It does **not** require native
coroutine implementation or native ABI approval.

The [evidence-classified behavior and open-question ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md)
is the detailed source of the bounded behavioral contract. Its older
dated assertions must be read together with subsequent appended
acceptance updates; the source has not been silently rewritten to
claim that historically divergent tests passed.

## Interpreted acceptance inventory and qualifications

| Area | Accepted evidence | Bounded result / explicit qualification |
| --- | --- | --- |
| Canonical MR10 12-case panel | [Panel review](co0-canonical-default-mr10-jes-5272-5283-acceptance-review-20261111.md) | 12/12 PASS at the cited canonical checkpoint; 142/142 zero JES RC; interpreted, not native |
| Original five development probes | [CO0-U01/U02 gate](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md) | Original post-promotion set **4 PASS / 1 FAIL**; legacy fixed-stack JOB **5318 fails**; distinct corrected COBOOT-frame JOB **5321 passes** 10/10 with CODE=0 and 10/10 zero JES RC; do **not** report an unqualified 5/5 |
| Continuation/value transfer | JOB **5322**, [behavior ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md) | 13 ordered records, interpreted CODE=0, runner RC=0, 14/14 JES RC=0000; full internal-cycle P/C trace remains incomplete |
| Ordinary worker return/re-entry | JOB **5324**, [behavior ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md) | Bounded return/re-entry accepted, not automatic destruction; exceptional termination is not established |
| Supported descriptor rejection | JOB **5325**, [descriptor audit](co0-u04-descriptor-validation-and-source-safety-audit-20261112.md) | Seven records; CODE=0, runner RC=0, 14/14 JES steps RC=0000; independently rechecked summary RC=0. Null/current deletion and valid busy root only; arbitrary/stale addresses remain out of scope |
| Allocation and cleanup | JOBS **5326–5330**, [behavior ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md) | Bounded exhaustion, exact-fit, coalescing, middle unlink and guarded negative SIZE=-10/-20; not native stack overflow or general SIZE safety |
| Two-coroutine direct suspension | JOB **5331**, [U08 matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md) | 8/8 exact records, CODE=0, runner RC=0, 12/12 JES RC=0000 |
| Two nested suspended call chains | JOB **5332**, [U08 matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md) | 14/14 exact records, CODE=0, runner RC=0, 12/12 JES RC=0000 |
| Repeated nested suspension sites | JOB **5333**, [U08 matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md) | 18/18 exact records, CODE=0, runner RC=0, 12/12 JES RC=0000 |

An independent owner recheck of JOBS **5331–5333** returned summary
shell RC=0 for each, JOB RESULT SUCCESS and **36/36 JES steps RC=0000**
combined; a further recheck of JOB **5333** at `main`
`c0ce8c25b9f5036d6fddfbd497b4e5dca51aac6b` again returned
12/12 JES RC=0000 and summary shell RC=0. These are **JES receipt
rechecks**, not new BCPL program executions.

All observed coroutine test results in this report are
**INTERPRETED-MVS-TESTED** (with their stated scopes), *not*
**NATIVE-MVS-TESTED**. Compiler-only token/frame tests are not
themselves coroutine runtime execution.

## Provenance and bounded historical conclusions

The [historical audit](co0-historical-source-audit-20261110.md)
records the surviving KM10 coroutine-related macros, library sources
and linkage job and the **missing `KM10.COMAIN`**. The original
`KM10.COMAIN` machine-code algorithm and complete historical API
are not recovered; no historical identity with the project-created
MR10 coroutine routines is asserted. The source-verified `X32`
P/C transfer and the reconstructed `ICLIB` 18-token switch bridge,
plus interpreted outputs, support **bounded observed continuation
semantics**, not a full cycle-level trace of every internal register
or scratch global.

A future attempt to recover `KM10.COMAIN` or trace each internal
interpreter state transition is **deferred research** unless new
evidence makes it necessary for native correctness.

## Owner decisions recorded for the initial native release

1. **Approach A, pointer descriptors:** `CREATECO` returns a
   descriptor pointer passed as an opaque client reference. Clients
   must supply valid, live references. Arbitrary, forged, stale and
   freed pointers do not receive a safety guarantee. Managed
   generation-validated handles (Approach B) are retained as
   **future research**, not a release dependency. See
   [CO0-U09 decision record](co0-u09-native-coroutine-ownership-and-stack-decision-briefing-20261112.md).
2. **S1, active stack-limit switching:** Each coroutine uses its own
   stack region; a coroutine transfer must select the incoming
   active safe limit, and returning to root must restore root's
   limit. Retain the present checked-entry frame-size discipline.
   Indirect per-check limit lookup (S2) is deferred. See the
   [S1 source investigation and owner decision](co0-u09-native-coroutine-stack-check-integration-investigation-20261112.md).

These choices are **approved architectural directions**, **not** an
approved CO.1 native ABI, register-save sequence, private descriptor
layout, stack extent or new global-number assignment.

## CO.1 — Native ABI and Stack Architecture transfer register

| Item | Specific unresolved CO.1 work |
| --- | --- |
| Native machine-state preservation | Examine actual CG370 code and IFOX-generated call/return/checked-entry sequences; prove R4/R5/R6/R7–R9/R11/R12/R15 liveness, saved continuation, return-value transfer and first entry |
| Descriptor and root context | Choose private pointer descriptor fields and root record; specify live/busy/idle/finished states, parent handling and deletion preconditions |
| Independent stack allocation | Choose GETVEC/MVS storage units, size guards, clearance and cleanup; do not transplant MR10 `SIZE+9` synthetic-frame layout |
| S1 stack integration | Decide update ordering of current safe limit, stack base/end and root restoration; preserve full inline callee frame-size checks and defined overflow path |
| Public stack diagnostics | Decide per-context or root-only `STACKBASE`, `STACKEND`, `STACKHWM` semantics without inventing historical behavior |
| Globals and linking | Audit historical LIBHDR, CGHDR, Global Number Registry and effective application/library exports; allocate native globals only by owner decision; prove actual registration rather than assuming IEWL inclusion suffices |
| Lifecycle/error | Preserve the bounded accepted first-transfer, parent, busy-target, ordinary return/re-entry and deletion oracles; decide supported errors and allocator teardown; do not promise safety for arbitrary machine pointers |
| Native isolated test gate | Prepare candidate-only IFOX/IEWL/GO/JES jobs, source revisions and acceptance traces; adapt JOBS 5331–5333 (8/14/18 exact records), preserve native/interpreted evidence separately |

CO.1 begins only with separate owner authorization after CO.0
closure review. Per the [milestone](milestone-implement-coroutine-support-for-native-compiler.md),
the **CO.1 gate itself** requires owner-reviewed native design and an
isolated native probe plan **before implementation**. Do not build
native CHANGECO, change resident MVS objects/datasets, assign globals,
or enroll new native regression tests merely because this handoff exists.

## Closure recommendation and explicit remaining exceptions

**Recommended decision for owner:** Accept the bounded CO.0
behavioral research and close **CO.0 — Historical Research and
Behavioral Contract**, **with qualifications**, treating the native
ABI and failure-path choices above as CO.1 work. Do **not** describe
all original five development probes as passing; do **not** claim
historical `KM10.COMAIN` recovered; do **not** claim native coroutine
execution.

**Until owner explicitly accepts closure:** CO.0 remains
**IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**. This record
is a **formal acceptance candidate**, not an approved closure,
milestone renumbering, new implementation or release authorization.


## 12 November 2026 — Superseding formal owner decision

The owner subsequently explicitly accepted and **CLOSED CO.0**, with all qualifications preserved, in the [formal CO.0 closure](co0-formal-closure-20261112.md). The earlier `READY FOR OWNER REVIEW — NOT CLOSED` and conditional acceptance language are retained as the candidate's historical checkpoint, but superseded. **CO.1–CO.5 remain NOT STARTED.**
