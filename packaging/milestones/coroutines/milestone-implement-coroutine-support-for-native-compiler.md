# Milestone: Implement coroutine support for native compiler

**Project:** BCPL for MVS 3.8 Reconstruction  
**Established:** 10 November 2026  
**Status:** ESTABLISHED; CO.0 CLOSED (qualified); CO.1 CLOSED (qualified owner acceptance, 13 November 2026); CO.2 IN PROGRESS (isolated Core Runtime CHANGECO implementation); CO.3–CO.5 NOT STARTED

**Marches:** CO.0 CLOSED (qualified); CO.1 CLOSED (qualified); CO.2 IN PROGRESS; CO.3–CO.5 NOT STARTED

**Target:** Native System/370 BCPL applications under MVS 3.8J

## Purpose and boundaries

Implement cooperative coroutine execution for native System/370 BCPL: an ABI-compatible context switch, persistent independent execution stacks, lifecycle routines written in BCPL where feasible, and complete native regression coverage.

"Native compiler" in this milestone title refers to coroutine support in **the native System/370 code the Cambridge compiler generates**. The currently available Cambridge compiler runs as INTCODE under ICINT19 and emits System/370 code. The independently reconstructed, native-running compiler under `cambridge-compiler/` is a separate project deliverable; its completion is **not a prerequisite**. The coroutine contract must remain suitable for applications compiled by that future compiler. This milestone does not claim to make the compiler itself run natively or self-host.

No new BCPL language construct or INTCODE opcode is anticipated. A compiler/code-generator change requires separate evidence and design review.

## Sources of authority

- [Architecture discussion, 3 November](../../architecture/coroutine-design-discussion-20261103.md)
- [Runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md)
- [Native runtime contract](../../architecture/runtime-contract-v1.md) and [stack-check contract](../../architecture/stack-check-contract.md)
- [Global Number Registry](../../architecture/global-number-registry.md)
- `richards-bcpltape/` (historical evidence); `mr10-kit-compiler/` (kit and interpreter reconstruction)
- [Research goals and approval gates](coroutine-research-and-design-gates.md)
- [CO.0 historical source audit, 10 November 2026](co0-historical-source-audit-20261110.md) — source findings, historical KM10 coroutine evidence and open execution questions
- [CO.0 MR10 coroutine probe verification plan, 10 November 2026](co0-mr10-coroutine-probe-verification-plan-20261110.md) — five-case JES selection, expected outputs and evidence interpretation
- [CO.0 MR10 coroutine JES summary review, 11 November 2026](co0-mr10-coroutine-jes-summary-review-20261111.md) — five OBSERVED, 62 zero-RC steps, second-pass extracted output and 4/4 compiler-token comparisons matched; owner-accepted golden fixtures; fresh post-promotion runner execution pending

## Architectural direction (qualified CO.1 baseline for CO.2; public ABI still gated)

| Component | Responsibility |
| --- | --- |
| **Core Runtime** | Native `CHANGECO`-equivalent context switch and any minimal stack-limit integration. Prefer a separate IFOX module over unnecessary additions to BCPLMAIN. |
| **BCPL coroutine library** | Portable `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO` where their behavior is verified. Do not modify historical BLIB until historical ownership is supported. |
| **BCPLMEM** | Existing native `GETVEC`/`FREEVEC` candidate for descriptor and stack storage; do not port the MR10 private arena allocator as native G87/G88. |
| **Compiler** | Ordinary procedure-call and activation-record ABI; no coroutine-specific syntax planned. |
| **System Extensions** | No new optional System Extension required for this fundamental runtime mechanism. |

These were working boundaries, now accepted **only as the bounded CO.2 implementation direction** under the [qualified CO.1 closure](co1-formal-acceptance-and-co2-transition-20261113.md). The candidate 24-word descriptor and experimental G!295–299 are **not** approved permanent public ABI allocations. Do not automatically reuse MR10's conflicting global numbers. The [CO.2 kickoff](co2-native-changeco-implementation-kickoff-20261113.md) sets the isolated implementation and MVS evidence gate.

## Discrete, named marches

| March | Name | Work and acceptance gate |
| --- | --- | --- |
| **CO.0** | **Historical Research and Behavioral Contract** | Audit MR10 `ICLIB`, coroutine BCPL, historical tape, saved compiler OCODE/INTCODE, accepted panel and unverified probes. Establish call, yield, resume, result, parent, termination, deletion and reuse semantics. **Gate:** evidence-classified behavior specification and open-question ledger; no native runtime changes. |
| **CO.1** | **Native ABI and Stack Architecture** | Trace actual CG370 call/return sequences, register liveness, first activation, stack limits/guards, global collisions, module linkage, lifecycle ownership. Resolve descriptor, interface, allocation and diagnostic contracts. **Gate:** owner-reviewed native design with isolated native probe plan **before** implementation. |
| **CO.2** | **Native CHANGECO Implementation** | Implement an isolated Core Runtime IFOX primitive against CO.1 design; verify two contexts, first transfer, suspension/resumption, nested locals, continuations and result passing. **Gate:** focused IFOX/IEWL/GO evidence under MVS 3.8J from candidate objects only. |
| **CO.3** | **Coroutine Library and Lifecycle** | Implement and link the agreed BCPL callable routines; verify creation, parent-chain calls, waiting, resumption, termination, deletion and storage reuse. **Gate:** independent BCPL module linkage and deterministic MVS behavioral tests. |
| **CO.4** | **Robustness and Edge-Case Verification** | Verify stack boundaries, recursion, repeated switches, allocation exhaustion, invalid/active/stale descriptors, cleanup and error paths. Do not claim general recovery from arbitrary machine addresses or unrecovered MVS abends. **Gate:** focused positive/negative evidence and no newly broken runtime invariants. |
| **CO.5** | **Integration, Regression, and Release** | Add named tests to the native Bootstrap suite without renumbering historical cases; run MR10, native and applicable project suites; prove clean-room reconstruction, reproducible linking, documentation and release readiness. **Gate:** separate owner acceptance with source revision, complete per-suite outcomes, IFOX/IEWL/GO/JES evidence and separately authorized installation/promotion. |

**CO.0 is CLOSED (qualified); CO.1 is CLOSED (qualified owner acceptance, 13 November 2026); CO.2 — Native CHANGECO Implementation is IN PROGRESS; CO.3–CO.5 are NOT STARTED.** The bounded CO.2 architecture inherits Approach A (valid/live descriptor preconditions), S1 (independent stacks and coordinated limits), native register/continuation restoration and private candidate-only linkage. The public ABI, permanent global allocations, and complete lifecycle rules are not approved for production promotion. See [formal CO.0 closure](co0-formal-closure-20261112.md) and [CO.1 source investigation](co1-native-abi-and-stack-source-investigation-20261112.md). Subsequent marches close only after separate evidence-backed owner decisions. See the [JOB 5356/5357 native candidate PASS](co1-bcpl-native-candidate-jes-5356-5357-pass-20261113.md) for the first fully successful compiler/IFOX/IEWL/GO BCPL coroutine switch. Subsequent candidate successes establish [nested checked-frame survival under JOB 5360/5361](co1-nested-frames-jes-5360-5361-pass-20261113.md) and [two live worker contexts under JOB 5362/5363](co1-two-worker-jes-5362-5363-pass-20261113.md); neither resolves the production design gate. The [direct worker-to-worker candidate PASS, JOB 5364/5365](co1-worker-to-worker-jes-5364-5365-pass-20261113.md), extends the native context-switch evidence while preserving creation-parent semantics. The [terminated-worker re-entry guard candidate PASS, JOB 5366/5367](co1-terminal-worker-reentry-jes-5366-5367-pass-20261113.md), verifies a bounded negative return from a **known-live** terminated descriptor; this remains an experimental interface, not an approved production lifecycle policy. The [bounded descriptor registry PASS, JOB 5368/5369](co1-bounded-descriptor-registry-jes-5368-5369-pass-20261113.md), adds MVS evidence for rejecting unregistered, null, active and terminated targets before an invalid target dereference; it does not establish safe deletion/reuse or a final registry design. The [revocation-before-FREEVEC candidate PASS, JOB 5370/5371](co1-terminated-descriptor-revocation-jes-5370-5371-pass-20261113.md), verifies revoking a terminated descriptor before freeing its storage and rejecting the former address without re-registration. It does **not** establish safe storage-address reuse. The [generation-token same-descriptor-address PASS, JOB 5372/5373](co1-generation-token-same-address-jes-5372-5373-pass-20261113.md), demonstrates a revoked old token remaining invalid after the same still-allocated descriptor is reused for a second worker lifetime, using a test-only BCPL resolution wrapper. It is not proof of actual MVS allocation-address reuse or a production-enforced opaque handle ABI.

## 14 November 2026 — CO.2 native positive-path checkpoint

The [owner-reported CO.2 JOB 5374/5375 PASS](co2-native-changeco-jes-5374-5375-pass-20261114.md)
establishes one completed Cambridge compilation, three RC=0000 IFOX
steps, one RC=0000 IEWL, one RC=0000 GO and a seven-record ordered BCPL
oracle, with native runner RC=0. This is qualified
**OWNER-REPORTED NATIVE-MVS-TESTED** evidence, not independent inspection
of the owner's raw JES receipts. It is promoted as the **CO.2 source
verification baseline**, not as a public API or installed runtime object.

The separate [repeated-continuation CO.2 candidate](candidates/co2-native-continuations/README.md)
extends the check to two suspensions per nested worker, with independent
native MVS evidence pending. Source-only offline verification and a
fail-closed BCPL output marker parser precede its first MVS attempt.
**CO.2 remains IN PROGRESS; CO.3–CO.5 NOT STARTED.**

## 14 November 2026 — CO.2 repeated-continuation first-run failure

The [first repeated-continuation native MVS attempt](co2-native-continuations-failed-oracle-20261114.md)
at `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5` reported
`X1 Y1 X2 Y2 X3 FVALUE`, runner RC=1. The failure is consistent
with proven BCPL source-oracle errors: `DEEP1(4)` computes 23, not 17,
and `DEEP2(5)` computes 32, not 22. Only the fixture's two numeric
assertions were repaired; a new host regression verifies the recurrence
and rejects the previously faulty fixture. The initial failed native
result remains FAIL. A corrected IFOX/IEWL/GO run is pending;
**CO.2 stays IN PROGRESS, CO.3–CO.5 NOT STARTED**.

## 14 November 2026 — CO.2 second native PASS and acceptance review

The [corrected native repeated-continuation JOB 5378/5379 PASS](co2-native-continuations-jes-5378-5379-pass-20261114.md)
at `5f941bb34cc70649f0325bd73f42eeb67397c5d6` reports three
zero-RC IFOX steps, one zero-RC IEWL, one zero-RC GO, and the exact
`X1 Y1 X2 Y2 X3 R1 Y3 R2 PASS` BCPL sequence; runner RC=0.
The earlier `FVALUE` result remains a separately documented FAIL.

The two positive-path native runs use the same separate candidate
`BCPLCO` assembler module and support the focused CO.2 implementation
gate. A [qualified CO.2 acceptance candidate](co2-qualified-acceptance-candidate-20261114.md)
maps the verified behavior to the march gate and explicitly retains
production ABI, public globals, lifecycle, robustness and release hold
points. It is **not** an owner acceptance or closure document.
**CO.0 and CO.1 remain CLOSED (qualified); CO.2 remains IN PROGRESS;
CO.3–CO.5 remain NOT STARTED.**

## Rules applying to every march

1. GitHub `main` remains the source authority. Use real BCPL, IFOX assembler and JCL; MVS/JES, IFOX and IEWL provide target verification. Preserve current installed `BOOT_OBJ` and use isolated candidates.
2. The native Core Runtime currently has a single working stack and global `STKLIM`; coroutine stacks require explicit bounds/guard and `STACKBASE`, `STACKEND`, `STACKHWM` semantics. No implicit workaround may bypass native checked entry.
3. MR10 uses `CHANGECO:6`, `CURRCO:7`, `COLIST:8`, `CREATECO`–`RESUMECO:91..95`, which conflict with historical Cambridge `LIBHDR`. Allocate native slots only through a subsequent Global Number Registry decision, after checking the full compiler/application export set.
4. A `GLOBAL` declaration is not executable implementation; IEWL linkage is not automatically BCPL global registration. Demonstrate any proposed BCPL library import and Core Runtime export path.
5. Preserve historical sources and provenance. The project-created MR10 coroutine module is behavioral reference, not proof that these precise entry points lived in historical Cambridge BLIB.
6. Preserve all existing regression IDs, manifests, known expected SKIPs and accepted qualifications. The accepted MR10 `basic-coroutine` panel case is not the same as the five `10-coroutines/` probes now independently accepted as interpreted development tests, not native verification.
7. New code must be easy to modify, rebuild from scratch, test in isolation and distribute; no changes to authoritative historical source and no hidden resident-MVS-only patches.

## Exclusions and authorization

No preemptive scheduling, MVS subtasks, timer-driven yields, general thread safety, automatic coroutine syntax, reimplementation of the entire compiler or blanket historical compatibility claims.

**CO.1 → CO.2 transition, 13 November 2026:** The owner explicitly authorized immediate qualified CO.1 acceptance and the start of CO.2. See the [formal acceptance record](co1-formal-acceptance-and-co2-transition-20261113.md) and [CO.2 kickoff](co2-native-changeco-implementation-kickoff-20261113.md). The original authorization boundary below describes milestone creation, not this subsequent approval. Production object installation, permanent global-number assignment, release publication, and CO.2 closure remain separately gated.

Creation of this milestone authorizes only this documentation and planning. It does **not** authorize implementation, JES submissions, new MVS datasets, promotion/overwrite of accepted objects, release publication, or any march closure. The major ABI, stack and library decisions must be discussed and approved before CO.2.
