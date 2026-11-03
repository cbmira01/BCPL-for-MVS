# Stage 1 audit — top-level modules and regression-suite architecture

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 3 November 2026  
**Authoritative repository:** `cbmira01/BCPL-for-MVS`, `main`  
**Read-only inspection baseline:** `1cabdc426b0a4bf29421cf5ec75585ae2335eb44`  
**Status:** Stage 1 repository audit and **proposed** migration design. No reorganization, code implementation, acceptance change, or MVS action was performed.

## 1. Scope and authority

This audit records the implementation implications of the agreed *target* structure: root-level `system-extensions/`, `standard-library/`, and `tests/`. Consult [runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md), [BSL scope discussion](../../architecture/bsl-scope-and-module-design-20261103.md), [regression separation discussion](../../architecture/regression-suite-separation-20261103.md), and the governing [Runtime Extensions](../../milestones/runtime-extensions/milestone-runtime-extensions.md), [BCPLTIME](../../milestones/bcpltime/milestone-date-and-time-services.md), and [QSAM](../../milestones/qsam/milestone-qsam.md) records before implementation.

Preserve the original compiler/runtime/BLIB architecture, BCEX/BCRG v1, approved global numbers, official milestones and marches, QSAM and other accepted evidence. GitHub `main` is source authority; actual target acceptance requires MVS 3.8J, IFOX, IEWL, JES and BCPL execution evidence. This is a **repository-location and test-ownership** initiative, not a redesign of the compiler or package ABI.

Inspection used GitHub's recursive `main` file tree and direct reads of key manifests, runners, generators, JCL and architecture records. It was **targeted**, not an exhaustive content grep of all repository files. A complete, reproducible text-reference search is required as an implementation preflight; do not treat the dependency inventory below as complete.

## 2. Verified layout and inventories

The baseline recursive GitHub tree reported **1,813 files** and was not truncated. There are presently no top-level `system-extensions/`, `standard-library/`, or `tests/` directories.

| Existing location | Observed inventory / responsibility | Disposition |
| --- | --- | --- |
| `bootstrap-toolchain/extensions/` | 147 tracked files; six package/subsystem directories | Move *package ownership* to root-level `system-extensions/` after dependency validation |
| `bootstrap-toolchain/extensions/bcpldemo/` | 5 files; supported reference optional extension | Candidate for `system-extensions/bcpldemo/` |
| `bootstrap-toolchain/extensions/bcpltime/` | 9 files; clock extension sources, documentation and acceptance test material | Candidate for `system-extensions/bcpltime/` |
| `bootstrap-toolchain/extensions/bcplqsam/` | 118 files; assembler, public header, many tests, preparers, verifiers and runbooks | Candidate for `system-extensions/bcplqsam/`; classify per file before moving |
| `bootstrap-toolchain/extensions/bcx/` | 4 files; optional-package selection macro implementation | Candidate for `system-extensions/bcx/` or common extension infrastructure; **do not** bury it under BCPLQSAM |
| `bootstrap-toolchain/extensions/r2testb/` | 3 files; historical R.2 test package | Preserve as reference/fixture; final placement to be decided |
| `bootstrap-toolchain/extensions/template/` | 8 files; example package/template | Candidate for root-level extension development template |
| `bootstrap-toolchain/regression/` | 177 contiguous numbered native test directories, IDs 00–176, plus shared scripts and documentation | Separate test *ownership* before physical case relocation |
| `mr10-kit-compiler/tests/` | Existing MR10 panel and specialized MR10 tests | **Leave in place**; participate through a suite adapter/aggregator |
| `tools/mr10/run-regression-panel` | Manifest-driven MR10 runner | Retain existing command |
| `tools/bootstrap/run-regression` | Numeric discovery and native suite orchestration | Keep working during migration; later make suite-aware |
| `tools/bootstrap/run-production-regression` | Production `BOOT_OBJ` wrapper | Keep semantics and compatibility |
| `tools/bootstrap/run-installed-r5-t1-regression` | Installed `EXT_OBJ` / `EXT_MAC` profile wrapper | Preserve explicit installed-mode and punch control |
| `config/dspal.yaml` | MVS PDS mapping authority | Update paths deliberately, **not** PDS names or record contracts |

**Important count:** the 177 native test directories cover every ID 00–176 without gaps: 146 cases 00–145, 13 cases 146–158, 4 cases 159–162, and 14 cases 163–176. The native panel's historical `SKIP 083` is an existing installed-production profiling rule, not evidence of a missing case.

The MR10 `00-regression-panel/manifest.tsv` and `tools/mr10/run-regression-panel` already provide named/category selection and expected interpreted completion-code/record checks. The MR10 panel has a distinct interpreter-hosted execution path. Its tests should remain adjacent to the MR10 kit, rather than being physically combined with S/370 native tests.

## 3. Proposed target locations (not an approved move list)

| Existing Git path | Proposed Git path | Notes |
| --- | --- | --- |
| `bootstrap-toolchain/extensions/bcpldemo/` | `system-extensions/bcpldemo/` | Keep reference extension and historical contract |
| `bootstrap-toolchain/extensions/bcpltime/` | `system-extensions/bcpltime/` | Preserve accepted T.0/T.1 evidence |
| `bootstrap-toolchain/extensions/bcplqsam/` | `system-extensions/bcplqsam/` | Separate active package source from development probes/test harness after file classification |
| `bootstrap-toolchain/extensions/bcx/` | `system-extensions/bcx/` | Shared BCX selection infrastructure |
| `bootstrap-toolchain/extensions/r2testb/` | `system-extensions/r2testb/` *or* historical archive/test fixtures | Needs owner choice based on active consumers |
| `bootstrap-toolchain/extensions/template/` | `system-extensions/template/` | Keep separately from runtime and compiler |
| future BSL code | `standard-library/<family>/` | No approved BSL APIs, objects, global numbers or datasets yet |
| `bootstrap-toolchain/regression/00-*/` … `145-*/` | `tests/bootstrap/<existing-case-name>/` **eventually** | Retain original case IDs; moving these is lower priority and adds risk |
| native cases 146–158 | `tests/runtime-extensions/<existing-case-name>/` | Separate BCX/BCPLDEMO coverage in manifest if needed |
| native cases 159–162 | `tests/system-extensions/bcpltime/<existing-case-name>/` | Interoperability cross-category tags without duplicate counting |
| native cases 163–176 | `tests/system-extensions/bcplqsam/<existing-case-name>/` | Include device/negative prerequisites in manifest |
| future BSL cases | `tests/standard-library/<family>/` | Prefer module-level test selection and reports |
| future cross-family cases | `tests/integration/` | Define ownership vs tagging to avoid double counting |
| `mr10-kit-compiler/tests/` | **No move** | A future project-level runner invokes its existing manifest-based suite |

The target `tests/` is for **formal native regression and cross-component integration suites**, while diagnostic probes and transient development evidence may remain with their implementations. `bootstrap-toolchain/` retains bootstrap compiler, runtime, tools and their build inputs; `cambridge-compiler/` remains the separate future native compiler. Do **not** relocate Core Runtime or historical BLIB merely because a new Standard Library directory appears.

**Open design choice:** moving every bootstrap case to `tests/bootstrap/` is not essential to achieve independent suite reports. A manifest-based split can occur first while all 177 numbered directories remain where they are. Prefer this lower-risk alternative unless physical centralization has a verified benefit.

## 4. Verified path and execution dependencies

### Dataset inventory / build chain

`config/dspal.yaml` directly maps:
- `EXT_MAC(BCXPRE,BCXCAT,BCXPOST)` to `bootstrap-toolchain/extensions/bcx/*.asm`;
- `EXT_ASM(BCPLDEMO,BCPLTIME,BCPLQSAM)` to the corresponding extension assembler files;
- `EXT_SOURCE(DEMOHDR,TIMEHDR,QSAMHDR)` to the corresponding public headers;
- `BOOT_JCL(BCPLDEMO,BCPLTIME,BCPLQSAM)` to `bootstrap-toolchain/jcl/*.jcl`.

`EXT_OBJ` is a separately managed optional-extension **binary object PDS** (`populate: false`), while `EXT_MAC`, `EXT_ASM`, and `EXT_SOURCE` have Git-backed text members. **Moving Git files must not rename MVS aliases, DSNs, global numbers or data formats.** The clean-room guide `docs/Rebuild-BCPL-for-MVS-from-source.md` explicitly inventories the `EXT_*` sources/objects and distinguishes populated sources from installed objects. Its steps and links require coordinated revision.

The existing `bootstrap-toolchain/jcl/bcpldemo.jcl`, `bcpltime.jcl`, and `bcplqsam.jcl` assemble from installed `HERC02.BCPL.EXT.ASM(...)` and install to `HERC02.BCPL.EXT.OBJ(...)`, with installation safety warnings. These JCL files need **classification** before any move: they are extension-owned installation procedures but currently published through `BOOT_JCL`. Host source path relocation and MVS PDS remapping are different operations. Preserve conditional execution and object-readback verification.

### Native runner chain

`tools/bootstrap/run-regression` scans `bootstrap-toolchain/regression/`, enforces legacy two-digit/three-digit case prefixes, defaults to 00..highest, handles the installed-production `SKIP 083`, candidate-only cases, and writes logs under `workarea/native-regression/logs`. The `run-production-regression` wrapper selects `BOOT_OBJ`; `run-installed-r5-t1-regression` injects installed `EXT_OBJ/EXT_MAC` configuration and has explicit `--resume-punch` opt-in.

`bootstrap-toolchain/regression/run-test-mvs.sh` calls `run-test.sh` using its own directory to find the repo root. The 967-line `run-test.sh` resolves cases using a sibling `NN-case-name` glob. It reads fixtures including `source.bcpl`, `library.bcpl`, `library-source.txt`, `expected.txt`, `candidate-only.txt`, `compile-only.txt`, `qsam-native.txt`, `time-selection.asm`, `extension-selection.asm`, expected GO RCs and named DD input/expected-output records. It chooses different native preparation/link/verification paths from these markers.

A **second hard-coded case lookup** appears inside its embedded Python GO/JCL modification block (near lines 690–707): it searches `root/bootstrap-toolchain/regression` to find `exec-parm.txt` and `input.records`. Adjusting only the outer runner or a single base directory would miss this path. `run-test.sh` also calls nearby `make-two-object-job.py` and runtime source/assembler probes, so a careless whole-directory move breaks both tool discovery and case fixture lookup.

`tools/checks/prepare-r5-extension-regression.py` hard-codes the existing `bootstrap-toolchain/regression`, `bootstrap-toolchain/extensions/bcpldemo` and BCX/probe paths. `tools/checks/prepare-t1-time-regression.py` similarly references the regression cases and BCX, BCPLTIME and BCPLDEMO package paths. `tools/checks/run-q2-qsam-regression.py` is invoked by the `qsam-native.txt` marker and must be traced as a separate case execution backend. The large BCPLQSAM package directory contains both active sources and many `prepare-*.py` / `check-*.py` tools, tests and runbooks; retain their relative-file assumptions or update the callers atomically.

### Additional documentation and verification surfaces

- `tools/bootstrap/README.md`, `bootstrap-toolchain/extensions/*/README.md`, `tools/checks/`, `tools/mr10/`, `packaging/operations/` and the clean-room guide describe the current commands and paths.
- Existing `tools/checks/test_*.py` tests validate R.5/T.1/BCPLQSAM preparers, installed-mode env resolution and `dspal` behavior; they need host-only regression checks after any path rewiring.
- Accepted evidence references old paths. **Do not mass-rewrite dated acceptance logs or historical files**; use redirects/indexes and new documentation to explain location changes.
- `workarea/` and `mvs-state/` are not migration targets. Never clean or delete either as part of a source-tree reorganization; past notes identify possible irreplaceable local evidence/state.

## 5. Major risks and safeguards

| Risk | Proposed safeguard |
| --- | --- |
| Breaks in hard-coded Git paths or Python imports | Complete path-reference grep, explicit old/new map, host syntax/unit checks |
| Hidden JCL fixture discovery | Static generation and diff of representative jobs, including EXEC PARM and input DD cases |
| Changes to installed dataset mappings or object selection | Hold MVS aliases/DSNs/member names stable; inspect actual generated JCL and IEWL inputs |
| Accidentally requiring optional extensions for bootstrap tests | Suite manifests with explicit package prerequisites; bootstrap suite runnable independently |
| Loss of historical test traceability | Preserve IDs 00–176, dated acceptance reports and case-to-suite crosswalk |
| New runner reports misleading PASS after implicit SKIP | Distinguish SKIP, blocked/not-installed, expected negative GO RC and true FAIL |
| Rerun overwrites accepted logs | Prefer run-scoped immutable logs/manifests rather than existing default log overwrite |
| QSAM external devices / dangerous operator actions | Explicit prerequisite and separate owner permission for JES/device and persistent MVS changes |
| Unverified bulk relocation | Stage commits, inspect `git diff --summary` and move-by-move manifest validation; do not promote runtime objects |
| Regressions in accepted link registration | Preserve BCEX/BCRG v1, BCX macros, G! allocations and verified installed/candidate profiles |

**Historical evidence qualification:** the owner-closed QSAM Q.5 report records a 00–176 panel of **175 PASS / 1 FAIL (175) / 1 expected SKIP (083)** and a **separate successful rerun of case 175**. Do not replace this with a claim of one uninterrupted green run. Retain official R.0–R.5, T.0–T.1 and Q.0–Q.5 identifiers and their governing closure records.

## 6. Recommended implementation sequence after separate approval

**Stage 2A — manifest preparation and source-location boundaries:** First capture a fresh, revision-pinned old-path/new-path and occurrence inventory. Move only carefully classified extension source/header/macro/template assets, and update `dspal` and host preparers in lockstep. Keep current `EXT_*` PDS aliases and canonical installation JCL behavior. Validate static file existence, host unit tests and generated deck comparisons before and after; do not install any MVS member.

**Stage 2B — regression-suite ownership without moving cases:** Add explicit stable-ID suite manifests to a new root `tests/`; separate reporting/selection from case execution while initially delegating to the existing runners. MR10 remains under `mr10-kit-compiler/tests/` and is invoked as an independent suite. Define exact installed vs source-mode and per-suite prerequisites. Preserve existing legacy commands as compatibility entry points.

**Stage 2C — optional physical test relocation:** Only after 2B parity, decide whether moving the native 00–176 case directories and `run-test*.sh` adds more value than risk. If moving, update both shell and embedded Python path calculations, individual case preparers, helper scripts, JCL generators and documentation together. No case renumbering.

**Stage 3 — independent coordinated regression:** New project-level coordinator may aggregate MR10, Bootstrap, Runtime Extensions, BCPLTIME, BCPLQSAM and future BSL results, without combining their acceptance totals. Preserve suite-level version, environment, build/object provenance, JES job ID, RC/abend and expected-negative outcomes.

**Stage 4 — verification:** Obtain a separately authorized fresh MVS baseline and execute targeted old-vs-new parity for each suite followed by combined clean-room verification. Compare *case by case*, not only totals. Validate installed/source profiles, no-extension linkage, QSAM record/JES device handling and negative cases. Nothing here authorizes an actual run or permanent dataset update.

The stages above are **work packages for discussion**, not official milestone/march numbering.

## 7. Exit criteria for Stage 1 and preconditions for Stage 2

Stage 1 delivers this repository audit, dependency/risk inventory and candidate migration map. It does **not** certify exhaustive file references or functional parity.

Before Stage 2 the owner should approve: (1) which extension development scripts/runbooks move versus remain with historical evidence; (2) whether `BOOT_JCL` extension-install members change source directory while preserving MVS members; (3) whether to implement suite manifests before physically relocating test cases (recommended **yes**); (4) treatment of R.2 test package and cross-extension case attribution; and (5) precise baseline verification and JES/MVS authorization.

Then perform an exhaustive tracked-source reference inventory at the **new** Git HEAD (for example `git grep -n` of both old directories and all runner/manifest identifiers), classify references as active, historical or generated, and produce a reviewed finite edit checklist. The audit's numerical inventory is baseline-specific and must be refreshed before moving files.

**No production source, JCL, test runner or MVS dataset was changed in Stage 1.**
