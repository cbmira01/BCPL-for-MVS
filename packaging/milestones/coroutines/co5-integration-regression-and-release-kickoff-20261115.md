# CO.5 — Integration, Regression, and Release: kickoff

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.5 — Integration, Regression, and Release  
**Status:** **IN PROGRESS**  
**Opened:** 15 November 2026  
**Authority:** [CO.4 formal qualified closure](co4-formal-acceptance-and-co5-transition-20261115.md)  
**GitHub authority:** `cbmira01/BCPL-for-MVS`, branch `main`; verify actual HEAD at start.

## Mission and official acceptance gate

Integrate the owner-accepted bounded native System/370 coroutine implementation into the project's reproducible native Bootstrap testing/build system **without changing historical test identities**, validate through MR10 and applicable native/project regression suites, demonstrate clean-room reconstruction and reproducible IFOX/IEWL linking, and prepare documentation for release decisions.

The milestone's CO.5 gate is **separate owner acceptance with source revision, complete per-suite outcomes, IFOX/IEWL/GO/JES evidence and separately authorized installation/promotion**. Opening CO.5 does not mark it complete or authorize release, permanent object writes or a public ABI freeze.

The approved design remains Approach A, S1, a root and two registered live workers, known-live descriptor preconditions and temporary candidate-only linkage until the owner separately approves production interfaces.

## Mandatory source review before implementation

Review these authoritative records and live source before planning material changes:

- [Milestone and exact march gates](milestone-implement-coroutine-support-for-native-compiler.md), [CO.4 formal acceptance](co4-formal-acceptance-and-co5-transition-20261115.md) and [CO.4 review candidate](co4-qualified-acceptance-review-candidate-20261115.md).
- [Runtime/library nomenclature](../../architecture/runtime-and-library-nomenclature.md), [Global Number Registry](../../architecture/global-number-registry.md), [native runtime contract](../../architecture/runtime-contract-v1.md) and [stack-check contract](../../architecture/stack-check-contract.md).
- Candidate Core Runtime `bootstrap-toolchain/asm/bcplco.asm`, accepted `bootstrap-toolchain/asm/bcplmain.asm`, `bcplmem.asm`; `packaging/milestones/coroutines/candidates/co3-delete-reuse/library.bcpl` and `co3drop.inc`.
- The accepted CO.3/CO.4 candidates, fixtures and `tools/coroutines/` runners, including the separate LIMITS, ACCOUNT and DENY evidence.
- `tests/README.md`, `tests/suites/*.tsv`, `tools/tests/run-suite`, `tools/tests/run-project-regressions`, the [clean-room rebuild procedure](../../../docs/Rebuild-BCPL-for-MVS-from-source.md), and [repository/MVS authority](../../operations/git-mvs-authority.md).

## Immediate CO.5 work sequence

1. **Inventory the exact current revision and integration boundaries.** Verify GitHub `main`, working-tree expectations, source and evidence hashes, existing Core Runtime exports/installed-object boundaries, and candidate-only global slots. Identify which native coroutine facilities need packaging and whether the existing bounded ABI requires an additional owner design decision before any production binding.
2. **Propose named native Bootstrap test integration.** The existing accepted native suites own cases 00–176 (bootstrap 00–145, runtime-extensions 146–158, BCPLTIME 159–162, BCPLQSAM 163–176). Do **not** renumber, reuse or silently alter those identities, SKIP 083 or device-opt-in cases 175–176. Inspect manifests and runner assumptions before proposing new IDs, ownership, selection flags, source fixtures, stable names and expected outputs. Seek owner approval on material integration/interface decisions before implementing.
3. **Keep test source and acceptance evidence reproducible.** Preserve independent compilation of the BCPL coroutine library, private IFOX context switch/DELETECO bridge, `/CN` checked frames, IFOX/IEWL native GO, source revision, job identities, exact ordered BCPL records and per-case raw receipts. Do assistant-operated host validation first, then present one guarded operator MVS batch for related native tasks. Do not create hidden MVS-only fixes.
4. **Run coordinated regression and report each suite separately.** The project coordinator currently offers `mr10`, `mr10-probes`, `bootstrap`, `runtime-extensions`, `bcpltime`, and `bcplqsam`; its offline `--list` and `--check` are suitable starting points. Use an explicit chosen native profile, account for expected SKIP 083, require separate device authorization for 175/176, and record genuine FAIL/BLOCKED/OBSERVED cases without redefining them as PASS. Do not invent a full-suite success from separate passing candidates.
5. **Plan and separately authorize clean-room validation.** The rebuild driver can destroy and recreate managed MVS datasets and can overwrite accepted objects. Inspect scope and approvals **before running any destructive or installation operation**. Verify that the coroutine library, native assembler components, BCPL/global bindings, JCL and test fixtures can be reconstructed from Git rather than hidden resident state.
6. **Prepare release readiness and an owner acceptance package.** Document install/recovery boundaries, exact object/module provenance, test matrix and suite outcomes, limitations of Approach A/S1 and the CO.4 risk ledger; obtain separate approval before public ABI promotion, permanent globals, `BOOT_OBJ` writes or release publication.

## Working discipline / handoff requirements

- GitHub `main` remains authoritative. No feature branch, no untracked resident MVS implementation, no renumbering of existing native cases. Do not commit/push except with explicit owner authorization for the proposed changes.
- Consult milestone, nomenclature and design/acceptance documents before implementing substantial interfaces. Prioritize real BCPL, IFOX/System/370 assembly and JCL plus MVS verification over host-only simulations.
- Consolidate host tests locally and operator MVS runs into guarded batches; output concise status and preserve separate raw evidence. Operator shell commands must avoid `set -e`, `set -u`, `set -o pipefail` and must not terminate the interactive shell.
- CO.4's accepted test coverage is **qualified**. Actual MVS exhaustion, deliberate overflow, arbitrary stale/freed descriptors, ABA-safe identity and exceptional abend cleanup remain outside acceptance and require explicit redesign/testing decisions.
- CO.5 remains **IN PROGRESS** until a separate evidence-backed owner closure. Release and dataset promotion require their own authorization.

**Next action:** audit existing native Bootstrap suite integration and decide the placement/identity of named coroutine tests before changing implementation, then proceed in the smallest reproducible MVS-backed increments.
