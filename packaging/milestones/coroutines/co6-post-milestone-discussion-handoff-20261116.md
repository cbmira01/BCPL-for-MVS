# Handoff — Post-milestone discussion after coroutine support

**Project:** BCPL for MVS 3.8 Reconstruction  
**Repository:** https://github.com/cbmira01/BCPL-for-MVS  
**Authoritative branch:** `main` (verify HEAD before relying on it)  
**Date:** 16 November 2026  
**Purpose:** Discussion and prioritization only. Do not declare a new march, implement work, change production MVS objects, publish a release, or alter a closed milestone without separate owner approval.

## Completed milestone

**Implement coroutine support for native compiler** is **CLOSED (qualified)**. All official marches **CO.0–CO.6** are owner-accepted and closed on their documented terms. The governing closure is `packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md`.

The last comprehensive supported campaign tested source `216b6707c404a91c796ed8f1419a99ef172b184a` under real MVS 3.8J and returned **208 PASS, zero FAIL/BLOCKED and one expected Bootstrap SKIP 083** across eight suites. This includes five supported interpreted MR10 coroutine tests and two paired MR10/native System/370 application oracles. The **separate** five-case historical `mr10-coroutines` diagnostic remains **four PASS, one genuine original fixed-stack CODE=-1 FAIL**. Its source and golden remain unchanged; the corrected-frame version passes independently. Do not conflate these counts.

The accepted native Approach A/S1 scope remains root plus at most two live workers with checked 1024-word stacks, known-live lifecycle semantics, and globals G!289–300. The Cambridge compiler still executes under ICINT19 while generating native System/370 application code. The CO.5 Bootstrap 117 IEWL SB2D incident and incomplete historical compatibility, rollback and distribution work remain recorded qualifications. No public release has been authorized.

## Authoritative documents to read

1. `packaging/milestones/coroutines/milestone-implement-coroutine-support-for-native-compiler.md`
2. `packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md`
3. `packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md`
4. `packaging/milestones/coroutines/co6-fixed-stack-supported-disposition-20261116.md`
5. `packaging/architecture/runtime-and-library-nomenclature.md`
6. `packaging/operations/git-mvs-authority.md`

## Post-milestone conversation

Review what the completed coroutine milestone contributes to the Cambridge BCPL Programming System; distinguish verified capability from deferred or explicitly excluded capability. Discuss remaining risks and technical debt, reliability of clean-room reconstruction and regression/release workflows, and how to prioritize possible future work across the native-running compiler, libraries, packaging/distribution and historical compatibility. These are **discussion candidates, not approved milestones**. Preserve existing official milestone names and numbering.

Prefer real BCPL, System/370 assembly, JCL and MVS execution evidence over unsupported inference. Keep GitHub `main` authoritative for source and decisions; MVS/JES/IFOX/IEWL evidence is authoritative for target execution. Host checks are the assistant's responsibility; any necessary MVS-facing operations should be consolidated and presented as concise command blocks with operator-visible summaries and retained logs. Do not touch untracked workstation files, create branches, commit or change closed/production scope unless the owner approves the specific action.

**First task:** Discuss and compare post-milestone priorities. Offer a concise recommendation and decision points, then wait for the owner's direction before establishing scope or implementation.
