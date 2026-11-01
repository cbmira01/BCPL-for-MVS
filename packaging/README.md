# BCPL for MVS — packaging and engineering records

**Authority:** GitHub `main` holds the project's source, build inputs, contracts and acceptance records. MVS 3.8J, IFOX, IEWL and JES evidence determine whether native code works; resident datasets do not supersede Git. See [repository authority](git-mvs-authority.md) and the [WSL operating policy](operator-wsl-command-policy.md).

## Build, installation and source navigation

- [Rebuild BCPL for MVS from source](../docs/Rebuild-BCPL-for-MVS-from-source.md) — the canonical clean-room operator procedure; the old `packaging/clean-room-mvs-reconstruction.md` path was retired.
- [Repository map](repository-map.md), [runtime development workflow](runtime-development-workflow.md), and [runtime object promotion rules](runtime-object-promotion.md).
- [Runtime contract v1](runtime-contract-v1.md), [stack-check contract](stack-check-contract.md), and [Global Number Registry](global-number-registry.md).
- [Cambridge runtime and library nomenclature](runtime-and-library-nomenclature.md) — Core Runtime, historical BLIB Base Library, System Extensions, Standard Libraries and User/Site Libraries.
- [BCPLIO dynamic stream](bcplio-dynamic-stream/README.md) — accepted runtime contract and closure; [evidence metadata](bcplio-dynamic-stream-evidence/).

## Milestones and owner acceptance

| Area | Governing record | Accepted/qualified disposition |
| --- | --- | --- |
| Runtime Extensions | [Milestone](milestone-runtime-extensions.md), [R.0 decisions](runtime-extensions-r0-owner-abi-decisions.md) | [R.1](runtime-extensions-r1-closure-20261022.md), [R.2](runtime-extensions-r2-closure-20261022.md), [R.3](runtime-extensions-r3-closure-20261022.md), [R.4](runtime-extensions-r4-closure-20261024.md), [R.5](runtime-extensions-r5-closure-20261024.md) individually CLOSED; expanded-milestone owner disposition remains separate |
| BCPLTIME | [Date and Time Services milestone](milestone-date-and-time-services.md) | [T.0](bcpltime-t0-closure-20261024.md) and [T.1](bcpltime-t1-closure-20261024.md) CLOSED |
| BCPLQSAM | [Milestone QSAM](milestone-qsam.md), [public API](bcplqsam-public-interface.md) | [Q.1](qsam-q1-closure-20261028.md), [Q.2](qsam-q2-closure-20261029.md), [Q.3](qsam-q3-closure-20261030.md), [Q.4](qsam-q4-closure-20261030.md), [Q.5](qsam-q5-closure-20261101.md) CLOSED; Q.0 closure is recorded in the governing milestone |
| Decimal Arithmetic | [Milestone proposal](milestone-decimal-arithmetic.md) | Future work; no implementation is claimed |

**QSAM qualification:** The owner accepted Q.5 after a full 00–176 regression with **175 PASS / 1 FAIL (case 175) / 1 expected SKIP (083)** and a *separate* successful case-175 rerun. The combined result is **not** one uninterrupted green panel. Installed BCPLQSAM verification and a genuine exceptional MVS CLOSE remain unproven, as detailed in [Q.5 closure](qsam-q5-closure-20261101.md).

The supported reference System Extension is [BCPLDEMO](bcpldemo-supported-reference-decision-20261024.md). Its status must not be inferred merely from global-number allocation.

## Historical engineering archive

Completed experiment notes, preliminary reviews, job-specific MVS evidence and earlier runtime work are organized under [`archive/`](archive/README.md), by **Core Runtime**, **Bootstrap**, **Runtime Extensions**, and **QSAM**. This reduces the active root without erasing historical test provenance.

Some superseded working drafts were retired from the current tree; their original contents remain retrievable from [the pre-cleanup Git revision](https://github.com/cbmira01/BCPL-for-MVS/tree/62df114afe16115b1216367b2d827aba790bc9d6/packaging). No final milestone closure or accepted interface specification is in that retired set.

Other preserved records: [historical BCPL source audit](audits/BCPL-corpus-audit.md) and [regression maintenance notes](maintenance/Handoff-repository-cleanup-regression-runner.md).

**Scope of this reorganization:** documentation and related Markdown navigation links only; no BCPL, assembly, JCL, Python, MVS datasets, or runtime installations were modified.
