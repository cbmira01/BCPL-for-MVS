# Coroutine research and design gates

**Milestone:** [Implement coroutine support for native compiler](milestone-implement-coroutine-support-for-native-compiler.md)  
**Recorded:** 10 November 2026  
**Status:** OPEN; CO.0 IN PROGRESS, research and approval goals, not native implementation evidence

**Five-probe execution checkpoint:** [11 November JES review and second-pass extraction](co0-mr10-coroutine-jes-summary-review-20261111.md) documents five OBSERVED cases, 62 zero-RC JES steps, 23 zero interpreted phase codes extracted from local reports, five matched program-output sequences, and four matched compiler-artifact pairs. The owner accepted the five golden contracts on 11 November; these are interpreted, not native, tests. The expanded runner has not yet been re-executed on MVS.

**Five-probe verification plan:** [CO.0 MR10 coroutine development-probe procedure](co0-mr10-coroutine-probe-verification-plan-20261110.md) records runner selection, candidate oracle and required JES evidence; no new probe execution or acceptance is claimed.

**CO.0 discovery (10 November):** The tape's `INDEX` explicitly identifies a **KM10 coroutine library**, including `KM10.COMACRO`, `KM10.COBLIB(CORTN)`, `KM10.COBLIB(STANDARD)`, `KM10.J(COLIB)`, and the **missing** `KM10.COMAIN`. This materially expands the prior historical-source inventory. See the [CO.0 source audit](co0-historical-source-audit-20261110.md). The native switching algorithm and full historical callable API remain unrecovered.

## Evidence already in Git

| Area | Established source observation | Research still open |
| --- | --- | --- |
| MR10 BCPL routines | `mr10-kit-compiler/library/coroutines.bcpl` implements reconstructed `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO`. | Distinguish designed/tested behavior from historical interfaces and cover error/termination paths. |
| MR10 switch | `mr10-kit-compiler/source/iclib.int` uses existing INTCODE `X32`; `icintv19.asm` implements `X32` by restoring interpreted P and C. | Trace each scratch global, saved continuation and value-transfer rule in `CHANGECO`; document first activation and resumption. |
| MR10 descriptor | Existing probe documentation records `C!0` saved P, `C!1` parent, `C!2` list link; `P=C+3`; `P!2` FN, `P!3` SIZE, `P!4` C. | Do **not** assume these interpreted offsets/registers map onto native S/370. |
| Tests | MR10 12-case regression panel has accepted `basic-coroutine`; `10-coroutines/` has five additional owner-accepted interpreted development probes. | The five candidate outputs and structural artifacts were reviewed and are frozen as goldens; native behavior and negative-path semantics remain unverified. |
| Historical Cambridge/KM10 | Ordinary `sys3/bcpl/libhdr` and `bcplib/bcpl/blib` do not expose the MR10-named coroutine API, **but** original `km10/comacro`, `km10/coblib/cortn` and `km10/j/colib` prove a historical native coroutine variant existed. | The tape-listed `km10/comain` is missing. Recover full historical interface, initialization and switching behavior from surviving indirect evidence; do not conflate the variants. |
| Native ABI | Native contract assigns R5 frame, R6 return, R7–R9 arguments/results, R4 restored from frame, R11 system vector; current BCPLMAIN has a single bounded working stack. | Identify all live registers/condition codes/stack state and restoration requirements using actual CG370 output and MVS probes. |
| Globals | MR10 numbers 6–8 and 91–95 conflict with the Cambridge `LIBHDR`. | Choose and approve new native slots and exports against Global Number Registry, compiler CGHDR and whole-executable collisions. |
| Storage | Native `BCPLMEM` supplies `GETVEC`/`FREEVEC`; stack checks use `STKLIM` and runtime diagnostics. | Establish isolated per-coroutine stack layout, guard, high-water, root stack, exhaustion and cleanup. |

Interpret a claim as **DECLARED**, **SOURCE-OBSERVED**, **INTERPRETED-MVS-TESTED**, **NATIVE-MVS-TESTED**, **INFERRED** or **UNVERIFIED**. Do not substitute a source observation or GO RC for behavioral proof.

## CO.0 — Historical Research and Behavioral Contract

- [ ] Trace the full `ICLIB` `CHANGECO` instruction path (saved P/C and scratch globals) and inspect original MR10 kit `ICINT` plus the project's `ICINT19`.
- [ ] Compare `compiler-probe.bcpl` and `frame-layout-probe.bcpl` with saved OCODE/INTCODE; prove argument order and actual synthetic frame behavior.
- [x] Verify all five existing `10-coroutines/` probes: call layout, frame layout, fixed-stack producer/consumer, RESUMECO parent chain, CREATE/DELETE/reuse. Record exact inputs, phase RCs, output oracle and JES evidence when authorized.
- [ ] Establish entry argument, yield value, return value, parent relation, natural return/termination, repeated resume, invalid/deleted coroutine and error behavior; classify any inferred behavior.
- [x] Identify the surviving historical KM10 coroutine-library inventory, control-block macro, coroutine-aware BLIB source, and link-edit job; distinguish it from project-created MR10 code (source audit only).
- [ ] Continue searching period documentation, tape sources and related references for the **missing KM10.COMAIN** implementation and a full historical callable coroutine contract.
- [ ] Design equivalent interpreted/native BCPL behavior tests, permitting only documented header/global mapping differences.

**CO.0 gate:** reviewed behavior table, provenance, reproducible interpreted test recipe, open unknowns. No new native implementation.

## CO.1 — Native ABI and Stack Architecture

- [ ] Examine actual CG370-emitted call/return/checked-entry sequences around nested `CHANGECO` calls; document R4/R5/R6/R7–R9/R11/R12/R15, workspace and continuation behavior.
- [ ] Prove how a never-run coroutine's first frame and continuation are initialized, how context switching returns values, and how the root context is represented.
- [ ] Compare separate GETVEC-backed stacks with the current single `STKLIM`/stack paint/overflow path and `STACKBASE`/`STACKEND`/`STACKHWM`; decide whether and how per-coroutine bounds are installed without violating accepted ABI.
- [ ] Specify ownership, allocation size units, lifecycle states, active/suspended deletion rules, stale references, error reporting and cleanup on ordinary and exceptional termination.
- [ ] Resolve native global numbers and historical BLIB versus separate BCPL library ownership. Establish actual BCPL object trailer/global import and assembler Core Runtime integration; do not assume System Extension BCEX/BCRG provides library linking.
- [ ] Provide a bounded native IFOX/IEWL/GO probe matrix and a non-production object/JCL workflow before submitting JES.

**CO.1 gate:** explicit owner approval of descriptor, stack bounds, register/continuation restoration, public BCPL API/global allocations, library location and lifecycle contract before CO.2.

## CO.2–CO.5 — Required independent verification

| March | Required demonstration |
| --- | --- |
| **CO.2** | Two native contexts, first transfer, suspend/resume, nested locals and return linkage, precise result and register behavior, actual IFOX/IEWL/GO/JES evidence. |
| **CO.3** | Separately compiled BCPL management routines, linked Core Runtime primitive, root/parent-chain behavior, normal completion, deletion and allocation reuse. |
| **CO.4** | Repeated interleaving, recursion, boundaries, overflow, allocation failure, invalid/active/stale pointers, teardown; explicit distinctions between safe negative returns and unrecoverable machine faults. |
| **CO.5** | New named native Bootstrap regression cases preserving 00–176 identities; applicable interpreted MR10, native Bootstrap and project suites; full clean-room rebuild; independent per-case output/RC oracles; exact PASS/FAIL/SKIP/BLOCKED; owner sign-off. |

Use the current `tests/README.md` / `tests/suites/*.tsv` suite system and `mr10-kit-compiler/tests/dev-probes-manifest.tsv`. No test IDs are allocated and no executions are authorized by this document.

## Source inventory

- `packaging/architecture/coroutine-design-discussion-20261103.md`
- `packaging/architecture/{runtime-and-library-nomenclature,global-number-registry,runtime-contract-v1,stack-check-contract}.md`
- `richards-bcpltape/{mr10/bcplkit,sys3/bcpl/libhdr,bcplib/bcpl/blib}`
- `mr10-kit-compiler/{source/iclib.int,asm/icintv19.asm,library/coroutines.bcpl,tests/10-coroutines,tests/00-regression-panel,tests/dev-probes-manifest.tsv}`
- `bootstrap-toolchain/{asm/bcplmain.asm,asm/bcplmem.asm,bootstrap-cambridge}`
- `tests/README.md`, `docs/Rebuild-BCPL-for-MVS-from-source.md`
- `packaging/operations/{git-mvs-authority,operator-wsl-command-policy}.md`
