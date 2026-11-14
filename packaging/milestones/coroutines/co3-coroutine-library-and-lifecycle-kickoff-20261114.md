# CO.3 — Coroutine Library and Lifecycle: kickoff and handoff

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle  
**Status:** **IN PROGRESS**  
**Opened:** 14 November 2026 (Louisville local time)  
**Authority:** [CO.2 qualified owner closure](co2-formal-acceptance-and-co3-transition-20261114.md)  
**Source authority:** GitHub `main` — verify its current HEAD before changes

## Mission and gate

Implement and **independently compile and link** the agreed BCPL-callable coroutine management routines, using the verified separate IFOX `BCPLCO` context-transfer mechanism. Target creation, parent-chain calls, waiting, resumption, ordinary completion, deletion and storage reuse under native System/370 execution on MVS 3.8J. The official CO.3 gate is **independent BCPL module linkage and deterministic MVS behavioral tests**. Do not conflate compiler execution (still INTCODE-hosted) with the emitted native application.

## Authoritative starting points

1. [Milestone](milestone-implement-coroutine-support-for-native-compiler.md), [CO.2 closure](co2-formal-acceptance-and-co3-transition-20261114.md), [qualified CO.1 closure](co1-formal-acceptance-and-co2-transition-20261113.md), [CO.0 formal closure](co0-formal-closure-20261112.md), and [research/design gates](coroutine-research-and-design-gates.md).
2. [Runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md), [native runtime contract](../../architecture/runtime-contract-v1.md), [stack-check contract](../../architecture/stack-check-contract.md), and [Global Number Registry](../../architecture/global-number-registry.md).
3. `bootstrap-toolchain/asm/bcplco.asm`, `bootstrap-toolchain/asm/bcplmem.asm`, `bootstrap-toolchain/asm/bcplmain.asm`, plus the existing native Cambridge compiler/export, registration and link-edit patterns.
4. Two accepted owner-reported native positive-path evidence records: [JOBS 5374/5375](co2-native-changeco-jes-5374-5375-pass-20261114.md) and [JOBS 5378/5379](co2-native-continuations-jes-5378-5379-pass-20261114.md). Preserve the separate failed first repeated-continuation result.
5. `mr10-kit-compiler/library/coroutines.bcpl`, the interpreted CO.0 behavior/oracle records, and surviving KM10 coroutine source inventory in `richards-bcpltape/`. Missing `KM10.COMAIN` is an evidence gap, not a reason to invent historical facts.

## Immediate engineering work

**First investigate, then build.** Audit actual independent BCPL object-module compilation, global export/import and IEWL registration, and distinguish historical `CREATECO`/`DELETECO`/`CALLCO`/`COWAIT`/`RESUMECO` semantics from reconstructed MR10 behavior. Reconcile the accepted CO.0 interpreted oracles with native calling and root/parent-chain requirements.

Prepare an owner-reviewable **CO.3 private callable contract** with ownership, valid/live descriptor preconditions (Approach A), one-active-coroutine/parent-chain invariants, natural worker return and waiting/resume semantics; stack size/guard and allocation policy (S1); deletion rules for active and suspended frames; safe revocation and address reuse policy; status/error and exceptional-cleanup behavior. The CO.2 candidate's two-worker registry, 24-word layout, G!295–299 and private error codes are **not** frozen public contracts. Do not assign a permanent global until per-executable collision checking and Global Number Registry approval.

After reviewing major design choices with the owner, create the smallest independent BCPL coroutine library module and test-local registration/linkage adapter compatible with the established Core Runtime. Prefer BCPL source for lifecycle management; use IFOX only for machine-specific mechanisms. Use `BCPLMEM` `GETVEC`/`FREEVEC` where suitable and avoid freeing active stacks or any stack with reachable frames. Do not modify historical BLIB merely to place these routines there.

Develop deterministic test oracles for root ↔ child calls, parent chains, wait/resume result propagation, ordinary return, deletion and supported reuse; distinguish safe positive paths from deliberately deferred CO.4 negative/robustness cases. Compile Cambridge BCPL, assemble IFOX, link IEWL, execute native GO under MVS 3.8J and retain strict completed-JOB step/record receipts. Verify the generated assembly and library import/export behavior rather than assuming that an IEWL include creates BCPL global registration.

## Operating and change controls

- GitHub `main` is authoritative; inspect current HEAD before work. Do not create branches or untracked artifacts on the owner's WSL checkout.
- Perform source/static/unit checks in the assistant's isolated environment. Keep native JCL and IFOX/IEWL/GO verification isolated in **temporary** MVS datasets, with read-only `BOOT_OBJ`. Do not install or overwrite accepted objects without separate authorization.
- Commit verified source, tests and evidence to GitHub `main` only with the owner's approval; the owner has directed that CO.3 begin without delay. Provide **only MVS-facing** guarded WSL command blocks when target testing is ready, with concise console output and full evidence in `workarea/`.
- Use official march names/numbers. Never renumber existing regressions. Make rebuild-from-scratch, test isolation and release reproducibility explicit.
- A successful host-side fake driver is **not** MVS verification. Classify actual owner-run MVS evidence separately; investigate failures against real BCPL, IFOX, IEWL and GO results.
- Preserve existing qualifiers: no blanket historical fidelity claim; no full PSW/condition-code or public ABI guarantee; no automatic reentrancy, multitasking, stale pointer recovery or general negative-path safety.
- **CO.3 must not be declared CLOSED without a separate explicit owner acceptance decision.** CO.4–CO.5 remain NOT STARTED.

**Immediate next action:** source-grounded CO.3 lifecycle/API and independent-BCPL-module linkage investigation, followed by the smallest testable implementation proposal and owner design review. Do not block that investigation on full reconstruction of missing historical sources or the independent native-running Cambridge compiler.
