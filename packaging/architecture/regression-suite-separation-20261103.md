# Regression suite separation — future refactoring discussion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Recorded:** 3 November 2026  
**Status:** Future maintenance/design proposal; **not implemented**, no acceptance records superseded

## Problem observed on GitHub main

The `tools/bootstrap/run-regression` runner discovers numbered case directories within `bootstrap-toolchain/regression/` and, with no range specified, defaults to the highest discovered case. `tools/bootstrap/run-production-regression` calls it with the installed production Core Runtime profile. The installed R.5/T.1 wrapper also invokes that production runner.

Therefore foundational compiler/runtime tests and tests of optional extensions participate in one contiguous default panel. This couples the size, prerequisites and release result of the **bootstrap regression panel** to selected optional System Extensions. Sharing a runner is desirable; conflating the **scope and acceptance accounting** of these suites is not.

### Observed historical numbered ranges

| Cases | Established subject | Proposed eventual suite ownership |
| --- | --- | --- |
| 00–145 | native compiler, Core Runtime, BLIB and runtime capabilities | Bootstrap |
| 146 | no-extension optionality | Runtime Extensions |
| 147–155 | BCPLDEMO dispatcher and query behavior | Runtime Extensions / BCPLDEMO |
| 156–158 | optional selection/upgrade/exclusion | Runtime Extensions |
| 159–162 | BCPLTIME alone and interoperability/upgrade cases | BCPLTIME, with cross-extension integration classification |
| 163–176 | BCPLQSAM query, lifecycle, fixed/variable records and SYSOUT | BCPLQSAM |

The classification above is **a proposed reporting split, not a renumbering or reinterpretation of accepted evidence**. Review the exact case contracts during migration, particularly cases that cross package boundaries.

Other independent historical panels, including MR10/interpreter tests, must remain identifiable. Do not assume the native bootstrap panel is the only foundational test suite.

## Desired test hierarchy

- **Bootstrap:** compiler/code generation, native ABI, Core Runtime and historical BLIB. It must be runnable without *selected* optional System Extensions.
- **Runtime Extensions:** BCEX/BCRG registration and selection, optional linkage, BCPLDEMO as the permanently supported reference package, and negative/compatibility tests.
- **BCPLTIME:** package-specific tests and explicitly identified integration cases.
- **BCPLQSAM:** package-specific tests including MVS QSAM record and device evidence.
- **BSL:** future independently reported module, family and cross-family tests.
- **Combined project validation:** invoke applicable suites, report separate PASS/FAIL/SKIP counts, and retain full source revision, installed-object/profile and MVS job evidence.

A suite can use the same compiler, assembler, linkage, JES, logs, evidence analyzers and regression harness without becoming part of a common **acceptance total**. Test identity and runner implementation are separate concepts.

## Low-risk staged refactoring proposal

1. **Inventory and freeze:** enumerate all existing numbered cases, scripts, expected outputs, special profiles, skip reasons, side effects and accepted results. Capture the current `main` commit and run the existing unmodified tests as a baseline when authorized.
2. **Introduce explicit suite manifests:** describe membership by stable historical case ID, prerequisites, profile, expected outcomes and package dependencies. Initially leave all test sources where they are.
3. **Add suite-aware selection and reporting:** reuse the current MVS compile/link/GO runner and evidence checks; preserve standalone single-case/range operations. A no-extension bootstrap command must not accidentally select BCPLQSAM or BCPLTIME.
4. **Parity verification:** compare results on the same reconstructed MVS environment, objects and commit. Confirm not only counts but per-case output, link members, job RCs, negative paths, and expected SKIP logic.
5. **Only after parity, consider relocating files:** directory organization is secondary; if changed, preserve IDs and provenance references, provide compatibility aliases or migration guidance, and check scripts with hard-coded paths.
6. **Document combined release gates:** report each suite independently; define which are required for bootstrap, optional-package and whole-distribution releases. A missing optional installed package should not make foundational testing fail; it must be reported distinctly from an unexpected failure.

**No automatic MVS action:** host-side changes may be analyzed or statically tested, but JES submissions, operator commands, installed-object updates and dataset modifications need separate explicit authorization.

## Historical acceptance and precision

Do **not** retroactively change original case names, numbers, records, commit references or accepted milestone/march statuses.

In particular, [QSAM Q.5 closure](../milestones/qsam/qsam-q5-closure-20261101.md) records a full 00–176 result of **175 PASS / 1 FAIL (case 175) / 1 expected SKIP (083)** and a **separate successful rerun of case 175**. It must **not** be rewritten as an uninterrupted fully green panel. Other historical acceptance reports remain authoritative for their respective runs.

Keep the accepted Runtime Extensions R.0–R.5, BCPLTIME T.0–T.1, and QSAM Q.0–Q.5 numbering and descriptions intact. This discussion does not open, close or rename milestones or marches.

## Design questions for future implementation review

- Do we retain global case IDs permanently and assign suites by manifest, or eventually use path-local case IDs plus a historical mapping? **Preference: retain existing IDs.**
- Does the bootstrap gate stop at 145, or should later foundational tests be allocated under a new stable namespace? Avoid encoding suite ownership in a brittle numeric cutoff forever.
- How are cross-extension interoperability tests assigned to one suite versus a separate integration suite, without double-counting?
- Can optional dependencies be detected without silently skipping required tests?
- How do we report and preserve installed vs candidate object profiles, external QSAM devices and other environment prerequisites?
- Which wrappers and clean-room guides must change together, so defaults and published examples remain accurate?

**Recommendation:** do the suite-manifest and reporting separation before beginning substantial BSL development, but treat the changes as a bounded infrastructure maintenance proposal requiring its own review and native parity evidence. No implementation is authorized by this note.
