# CO.4 — Robustness and Edge-Case Verification: formal qualified closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification  
**Owner decision:** **CLOSED (qualified)**  
**Decision date:** 15 November 2026  
**Reviewed GitHub `main`:** `4b144e21615a9c9e8d154166287c5da1a2d21cae`  
**Next march:** CO.5 — Integration, Regression, and Release (**IN PROGRESS**)

## Explicit owner acceptance

The owner directed: **“Close CO.4, and proceed to CO.5 without delay. Give me a handoff prompt for a new conversation.”** This is approval of the bounded **Option A — qualified closure** in the [CO.4 acceptance review](co4-qualified-acceptance-review-candidate-20261115.md), not an authorization to promote or install runtime objects or publish a release.

The governing CO.4 gate is **focused positive/negative evidence with no newly broken runtime invariants**. The accepted scope is Approach A (known-live descriptor preconditions), S1 (independent checked stacks), a root plus at most two live workers, fixed worker safe stack of 1024 words plus 256-byte clearance, and temporary candidate-only bindings. The observed accepted cases did not expose a new broken invariant within that scope. This is a qualified acceptance of the tested behavior, not proof of all possible runtime states or native historical compatibility.

## Source-revision-tracked native acceptance evidence

The following are **OWNER-REPORTED NATIVE-MVS-TESTED** PASS results from strict compiler/IFOX/IEWL/GO/JES runners. Raw operator-local individual JES logs were not independently audited in the conversation. Where tests were executed separately at different revisions, they are **not** an uninterrupted full-suite PASS at the current Git HEAD.

| Area | Tested source revision | Native result and coverage |
| --- | --- | --- |
| [Bounded stress](co4-bounded-stress-native-pass-20261114.md) | `612234b106b5ef450b9d2ee70effd0f39ca96a70` | PASS: repeated calls, recursion, suspension and known-live refusal |
| [Safe negative](co4-safe-negative-native-pass-20261114.md) | `cc3b2c6c2c96d77d7b12be1779ae005b79c8ebdf` | PASS: size/capacity/operation refusal, survivor continuity |
| [STACK, CHURN, BUSY](co4-verification-batch-native-pass-20261114.md) | `976c20da29943a72867195a24e010afe4e395e1a` | PASS (3/3): checked recursion and guards, 16 creation/deletion cycles, busy/parent refusal |
| [LIMITS](co4-inspection-limits-pass-account-first-fail-20261115.md) | `b0ce46fd965d1ca7720594fc5516ad7dd12f3993` | PASS: live STKLIM/APLIMIT, context and stack-boundary restoration |
| [DENY](co4-inspection-followup-account-fcurr-deny-pass-20261115.md) | `491f4acaa44a37eb4e63ff7e3bc75693c96211c7` | PASS: deterministic injected GETVEC denial, rollback, survivor recovery |
| [ACCOUNT](co4-inspection-account-native-pass-20261115.md) | `1c97e030e2f12f5786145a8b9f13202d67c0ffe7` | PASS: MEMSTAT count/byte accounting, 12 two-worker cycles, cleanup |

The source/IFOX fixtures, runner receipts and earlier CO.3 accepted baselines are preserved under GitHub and separately retained operator-local evidence paths. The acceptance review links individual receipt directories. This qualified closure specifically accepts the **separate** final LIMITS, DENY and ACCOUNT outcomes; the original mixed three-case attempt never passed all three in one run.

## Preserved failures and limitations

Original failures remain FAIL, without retroactive reclassification: initial STACK compiler JOB 5404; inspection printer UTF-8 decoding; S0C1 in GO JOB 5419 (test-only IFOX R10 preservation); early ACCOUNT `FAIL`; and pre-registration `FCURR`. The subsequent isolated source/fixture repairs and passing receipts are distinct evidence.

**Not accepted or proven:**

- Actual MVS `GETMAIN` exhaustion, real 24-bit storage pressure, and failure recovery under genuine system allocation refusal. DENY simulated a bounded `GETVEC=0`.
- Deliberate `STKLIM` crossing, precise historical INUM/overflow boundary semantics, stack-overflow diagnostics under deliberate fault, or recovery from unexpected S0C1/other abends.
- Safety for arbitrary/freed/stale descriptor pointers, ABA-safe identity under MVS identical-address reuse, production opaque handles, or unrestricted stale-handle recovery.
- Exceptional cancellation/teardown, multiple subtasks, reentrancy, concurrency, preemption, additional workers, generalized stack sizing, or a public stable coroutine ABI.
- Promotion of temporary G!289–305 bindings to permanent global assignments, modifications of accepted `BOOT_OBJ`/installed MVS objects, or release publication.

These remain an explicit risk/design-decision ledger, not tacit acceptance. Material ABI, pointer-identity, overflow or storage-policy changes require fresh owner design approval before implementation.

## Disposition and CO.5 transition

- CO.0 — Historical Research and Behavioral Contract: CLOSED (qualified).
- CO.1 — Native ABI and Stack Architecture: CLOSED (qualified).
- CO.2 — Native CHANGECO Implementation: CLOSED (qualified).
- CO.3 — Coroutine Library and Lifecycle: CLOSED (qualified).
- **CO.4 — Robustness and Edge-Case Verification: CLOSED (qualified, owner accepted).**
- **CO.5 — Integration, Regression, and Release: IN PROGRESS.**

The [CO.5 kickoff](co5-integration-regression-and-release-kickoff-20261115.md) authorizes beginning integration planning immediately. Its distinct owner-acceptance gate requires native Bootstrap integration without renumbering, MR10 and applicable native suite outcomes, clean-room reconstruction, reproducible linking, release documentation, and explicit acceptance at a cited Git revision. Destructive MVS reconstruction, permanent dataset updates, public ABI promotion and release publication are **not** authorized by CO.4 closure.

This is a documentation-only transition; no MVS job was submitted and no installed object altered to record this decision.
