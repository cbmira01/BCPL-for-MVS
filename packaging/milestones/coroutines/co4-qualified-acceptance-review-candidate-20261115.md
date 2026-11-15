# CO.4 — Qualified acceptance review candidate (not closure)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification  
**Status:** **OWNER REVIEW CANDIDATE; CO.4 IN PROGRESS**  
**Source authority:** GitHub `main`; evidence revisions enumerated below.  
**Prepared:** 15 November 2026. **No owner acceptance is implied.**

## Governing gate

The [milestone](milestone-implement-coroutine-support-for-native-compiler.md) defines the CO.4 gate as **focused positive/negative evidence with no newly broken runtime invariants**. The [CO.4 kickoff](co4-robustness-and-edge-case-verification-kickoff-20261114.md) requires bounded stack, recursion, repeated switch, storage, invalid/busy/stale descriptor, cleanup and error-path verification. It forbids interpreting this candidate as unrestricted pointer safety, a frozen public ABI, or MVS abend recovery. The accepted architecture remains Approach A (known-live bounded descriptors), S1 (independent checked stacks), one root and at most two workers.

## Native-MVS verification inventory

All reported PASSes were produced by guarded native runners that require separate Cambridge application/library compilation (where applicable), IFOX RC=0000, IEWL RC=0000, GO RC=0000, JES SUCCESS and strict ordered BCPL output. All are **OWNER-REPORTED NATIVE-MVS-TESTED**; raw JES transcripts were not independently reviewed in this conversation.

| Area | Native evidence and revision | Behavior covered |
| --- | --- | --- |
| CO.3 accepted baseline | First lifecycle JOB 5386, parent-chain JOB 5392, delete/reuse JOB 5397 | Independently compiled callable library, resumption, natural return, valid deletion/reuse |
| CO.4 bounded stress | [Native PASS](co4-bounded-stress-native-pass-20261114.md), `612234b106b5ef450b9d2ee70effd0f39ca96a70` | 32 root-to-worker calls, recursive frames and checked suspension, known-live refusals, cleanup |
| CO.4 safe negative | [Native PASS](co4-safe-negative-native-pass-20261114.md), `cc3b2c6c2c96d77d7b12be1779ae005b79c8ebdf` | Invalid size, root/illegal operations, capacity refusal, survivor continuity, cleanup |
| CO.4 STACK/CHURN/BUSY | [Three-case native PASS](co4-verification-batch-native-pass-20261114.md), `976c20da29943a72867195a24e010afe4e395e1a` | Guard/extent, recursive checked frames, 16 create/delete rounds, registry reuse, busy parent refusal |
| CO.4 LIMITS | [Native PASS](co4-inspection-limits-pass-account-first-fail-20261115.md), `b0ce46fd965d1ca7720594fc5516ad7dd12f3993` | Actual observed `STKLIM`/`APLIMIT`, machine/BCPL current context, stack boundary restoration |
| CO.4 DENY | [Native PASS](co4-inspection-followup-account-fcurr-deny-pass-20261115.md), `491f4acaa44a37eb4e63ff7e3bc75693c96211c7` | Simulated first/second allocator refusal, rollback and survivor recovery |
| CO.4 ACCOUNT | [Native PASS](co4-inspection-account-native-pass-20261115.md), `1c97e030e2f12f5786145a8b9f13202d67c0ffe7` | Exact `BCPLMEM` count/byte balance, invalid size, 12 two-worker cycles, cleanup |

These are **independent test runs at different source revisions**, not a complete simultaneous regression of all fixtures at the current Git HEAD. The accepted CO.3 runtime and native coroutine library sources remain unchanged during the most recent inspection fixture fixes; CO.5 must still perform its separately authorized integration and regression gate.

## Previous failures, preserved, not erased

Keep the separately documented compile FAIL JOB 5404, printer UTF-8 failure, GO S0C1 JOB 5419, early ACCOUNT `FAIL`, and pre-registration `FCURR` mismatch as distinct unsuccessful attempts. The source-local fixes and new successful receipts do not retroactively make the old jobs PASS.

## Explicit boundaries / remaining design-gated decisions

1. **Actual MVS `GETMAIN` exhaustion:** `DENY` uses bounded simulated `GETVEC` refusal; it does not establish a real shortage of 24-bit storage or real `GETMAIN` EC failure while coroutines are live.
2. **Deliberate stack overflow:** STACK/LIMITS test safe extents, painted guard and live limits, not crossing `STKLIM` or validating terminal overflow/ABEND policy. Historical INUM behavior is unresolved.
3. **Stale and arbitrary pointers:** bounded known-live membership and revocation-before-free are supported; an arbitrary freed address must not be dereferenced. ABA-safe identity across actual allocator same-address reuse and opaque generation-token enforcement remain unapproved design choices.
4. **Unexpected failures and exceptional termination:** abnormal MVS abend recovery, cancellation of active/suspended frames, general stale-handle recovery, more than two workers, preemptive execution, and reentrant/multitask use are not established by these tests.
5. **Public/distribution boundaries:** G!289–305 are candidate/test-local only where used; no production global registration, Core Runtime installation, library ABI freeze, release, or CO.5 test promotion is authorized.

## Proposed disposition for owner review

**Option A — qualify and close CO.4, subject to owner approval:** accept the bounded Approach A/S1 robustness contract with the explicit exclusions above and preserve their open design/risk ledger for future work. The observed focused positive/negative native results support this **qualified** interpretation of the march gate; they do not support an unrestricted robustness claim.

**Option B — retain CO.4 IN PROGRESS:** require one or more additional bounded target probes and separately approve their failure/overflow design before implementation. Do not silently add a potentially abending test or change descriptor/public ABI semantics.

A qualified closure, if accepted, must be a **separate explicit owner decision** and formal acceptance record. Do **not** start CO.5 or modify installed objects from this candidate alone.

**Current authoritative status: CO.0–CO.3 CLOSED (qualified); CO.4 IN PROGRESS; CO.5 NOT STARTED.**
