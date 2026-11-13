# Milestone: Implement coroutine support for native compiler

**Project:** BCPL for MVS 3.8 Reconstruction  
**Established:** 10 November 2026  
**Status:** ESTABLISHED; CO.0 CLOSED (qualified owner acceptance, 12 November 2026); CO.1 investigation IN PROGRESS

**Marches:** CO.0 CLOSED; CO.1 IN PROGRESS (investigation only); CO.2–CO.5 NOT STARTED

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

## Architectural direction (pending CO.1 design approval)

| Component | Responsibility |
| --- | --- |
| **Core Runtime** | Native `CHANGECO`-equivalent context switch and any minimal stack-limit integration. Prefer a separate IFOX module over unnecessary additions to BCPLMAIN. |
| **BCPL coroutine library** | Portable `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO` where their behavior is verified. Do not modify historical BLIB until historical ownership is supported. |
| **BCPLMEM** | Existing native `GETVEC`/`FREEVEC` candidate for descriptor and stack storage; do not port the MR10 private arena allocator as native G87/G88. |
| **Compiler** | Ordinary procedure-call and activation-record ABI; no coroutine-specific syntax planned. |
| **System Extensions** | No new optional System Extension required for this fundamental runtime mechanism. |

These are working boundaries, **not an approved callable interface, descriptor layout, or global allocation**. Do not automatically reuse MR10's conflicting global numbers.

## Discrete, named marches

| March | Name | Work and acceptance gate |
| --- | --- | --- |
| **CO.0** | **Historical Research and Behavioral Contract** | Audit MR10 `ICLIB`, coroutine BCPL, historical tape, saved compiler OCODE/INTCODE, accepted panel and unverified probes. Establish call, yield, resume, result, parent, termination, deletion and reuse semantics. **Gate:** evidence-classified behavior specification and open-question ledger; no native runtime changes. |
| **CO.1** | **Native ABI and Stack Architecture** | Trace actual CG370 call/return sequences, register liveness, first activation, stack limits/guards, global collisions, module linkage, lifecycle ownership. Resolve descriptor, interface, allocation and diagnostic contracts. **Gate:** owner-reviewed native design with isolated native probe plan **before** implementation. |
| **CO.2** | **Native CHANGECO Implementation** | Implement an isolated Core Runtime IFOX primitive against CO.1 design; verify two contexts, first transfer, suspension/resumption, nested locals, continuations and result passing. **Gate:** focused IFOX/IEWL/GO evidence under MVS 3.8J from candidate objects only. |
| **CO.3** | **Coroutine Library and Lifecycle** | Implement and link the agreed BCPL callable routines; verify creation, parent-chain calls, waiting, resumption, termination, deletion and storage reuse. **Gate:** independent BCPL module linkage and deterministic MVS behavioral tests. |
| **CO.4** | **Robustness and Edge-Case Verification** | Verify stack boundaries, recursion, repeated switches, allocation exhaustion, invalid/active/stale descriptors, cleanup and error paths. Do not claim general recovery from arbitrary machine addresses or unrecovered MVS abends. **Gate:** focused positive/negative evidence and no newly broken runtime invariants. |
| **CO.5** | **Integration, Regression, and Release** | Add named tests to the native Bootstrap suite without renumbering historical cases; run MR10, native and applicable project suites; prove clean-room reconstruction, reproducible linking, documentation and release readiness. **Gate:** separate owner acceptance with source revision, complete per-suite outcomes, IFOX/IEWL/GO/JES evidence and separately authorized installation/promotion. |

**CO.0 is CLOSED (owner-accepted with qualifications, 12 November 2026); CO.1 is IN PROGRESS (source investigation only; design NOT APPROVED); CO.2–CO.5 are NOT STARTED.** See [formal CO.0 closure](co0-formal-closure-20261112.md) and [CO.1 source investigation](co1-native-abi-and-stack-source-investigation-20261112.md). Subsequent marches close only after separate evidence-backed owner decisions.

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

Creation of this milestone authorizes only this documentation and planning. It does **not** authorize implementation, JES submissions, new MVS datasets, promotion/overwrite of accepted objects, release publication, or any march closure. The major ABI, stack and library decisions must be discussed and approved before CO.2.
