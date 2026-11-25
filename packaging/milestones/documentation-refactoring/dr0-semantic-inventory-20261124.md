# DR.0 — Inventory and Classification: semantic review checkpoint

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 24 November 2026 EST  
**Status:** DR.0 IN PROGRESS; draft for owner review, not a disposition or architecture approval.  
**Inventory baseline:** `ed0f8066859ed4e1a310bbb91520d0d629c5dca3`  
**Reviewed main:** `1383ef4471255f59f8961e4132aeca996d81e8bf`

## Coverage and method

The initial census counts 857 Markdown files, of which 554 are in packaging and 192 in tests. The current recursive Git tree contains 3,017 entries (three more than the baseline: two added files and a directory). The inventory below is a content-based first pass of principal educational briefings, compiler, library, extension and operational documentation; it uses headings, stated purposes, selected status passages, source paths, and cross-checks against specific accepted records. It is not a line-by-line technical audit of every document. Other files and evidence series are conservatively classified by path and purpose, with detailed review still required. All reads were pinned to the reviewed main commit. No source checkout, MVS execution or new release was performed.

## Reader-facing technical documentation

Disposition labels are candidates only. Subject groupings below are semantic, not directory proposals. Explanations are secondary teaching material unless a separate accepted contract establishes authority. Product and project audiences may share background explanations.

| Existing path (relative to docs/) | Subject and audience | Primary type | Condition / disposition candidate |
| --- | --- | --- | --- |
| README.md | All readers; orientation index | Navigation | Revise to point to the approved manual catalog |
| BCPL-history-and-porting.md | Programmers, researchers, developers; history and bootstrap | Explanation | Split current-state narrative from durable historical explanation; reconcile status |
| BCPL-memory-management.md | Programmers, runtime developers; allocation | Explanation plus research | Separate programmer contract, historical research and candidate allocator design; preserve evidence |
| Hercules-briefing.md | Operators and developers; emulator | Explanation with how-to material | Consolidate operational details with current Docker/TK5 procedures; keep generic background distinct |
| IBM-data-representation.md | Programmers; bytes, words, character/decimal data, records | Explanation/reference | Consolidate overlap with System/370 and object format subjects |
| IFOX-assembler-toolchain-briefing.md | Developers; assembler and link-edit | Explanation/reference/how-to | Review 67,412-byte briefing for reusable chapters, remove repeated orientation, retain technical precision |
| JCL-for-the-programmer.md | Programmers/operators; batch jobs | Explanation/how-to | Consolidate compile/link/run and allocation examples, verify actual examples |
| MVS-3_8-briefing.md | Programmers/operators; OS concepts | Explanation | Review 54,991-byte briefing alongside narrower MVS subjects |
| MVS-access-methods.md | Programmers; datasets and I/O | Explanation | Consolidate shared record/DD/DCB concepts; do not replace BCPLQSAM normative API |
| MVS-debugging.md | Programmers/developers; diagnostics | Explanation/how-to | Separate diagnostic workflow from concepts and dated investigations |
| MVS-program-execution.md | Developers; linkage and execution | Explanation | Reconcile overlap with MVS overview, assembler and object/load modules |
| MVS-storage-and-addressing.md | Developers; storage and addressing | Explanation | Consolidate storage background; retain distinction from BCPL runtime contract |
| MVS-system-programming-interfaces.md | Developers; MVS services | Explanation | Consolidate system services background, preserve macro/SVC distinctions |
| S370-object-and-load-modules.md | Developers; object and load formats | Explanation | Consolidate overlap with IFOX/IEWL and MVS execution |
| System_370-briefing.md | Programmers/developers; machine architecture | Reference/explanation | Review scope and overlap with data representation; not an IBM primary reference |
| Rebuild-BCPL-for-MVS-from-source.md | Maintainers; routine reconstruction | How-to | Retain canonical procedure; fix empty tool-guide dependency only after approval |
| Manual-Rebuild-BCPL-for-MVS.md | Maintainers; individual reconstruction steps | How-to | Retain distinct manual maintenance task; verify parity with automated driver |
| Guide-to-*.md (ten files) | Unfilled placeholders | None | Removal candidates, pending dependency review; Guide-to-Project-Tools.md has two active inbound links |

The ten exact placeholder paths are Guide-to-BCPL-Libraries.md, Guide-to-BCPL-Optional-Extensions.md, Guide-to-BCPL-Programming-on-MVS.md, Guide-to-Building-and-Installing-BCPL.md, Guide-to-Project-Tools.md, Guide-to-the-BCPL-Runtime-Core.md, Guide-to-the-BCPL-System-Architecture.md, Guide-to-the-Bootstrap-BCPL-Compiler.md, Guide-to-the-Cambridge-BCPL-Compiler.md and Guide-to-the-MR10-kit-BCPL-Compiler.md.

## Compiler, runtime and library documentation

| Path | Audience / class | Authority and proposed disposition |
| --- | --- | --- |
| bootstrap-toolchain/README.md | Developers; navigation | Retain ownership/source mapping; revise to link manuals |
| bootstrap-toolchain/bootstrap-cambridge/README.md | Developers; how-to and explanation | Consolidate demoted compiler build/use with project procedures; retain distinct compiler identity |
| bootstrap-toolchain/bootstrap-cambridge/compiler-options-and-parm.md | Programmers/developers; reference | Retain historical option grammar and distinguish historical EXEC PARM from current bootstrap transport |
| bootstrap-toolchain/asm/README.md | Developers; source map/reference | Retain canonical source pointers; separate dated acceptance |
| bootstrap-toolchain/library/README.md | Developers; library overview | Reconcile separate Coroutine Support Library terminology and staged/accepted status |
| bootstrap-toolchain/jcl/README.md | Developers; reference/how-to | Retain source-to-member mapping rules; review dated CO.5 installation instructions against current manifest and reconstruction driver |
| bootstrap-toolchain/regression/README.md | Developers; procedure plus test evidence | Consolidate active regression commands; preserve individual test receipts and chronology; current title is ambiguous about native compiler identity |
| mr10-kit-compiler/docs/README.md | Programmers; index | Retain navigation to options, sources, JCL, tests |
| mr10-kit-compiler/docs/compiler-options.md | Programmers; reference | Retain MR10 OPTIONS DD grammar, defaults and verification limits; do not merge with Cambridge option grammar |
| mr10-kit-compiler/library/GLOBALS.md | Programmers/developers; reference | Retain separate MR10-local number map; reconcile wording with authoritative registry without changing slots |
| mr10-kit-compiler/library/README.md | Programmers; reference/how-to | Retain module inventory, invocation and memory-unit semantics; consolidate shared library guidance |
| mr10-kit-compiler/jcl/README-SUITES.md | Operators/developers; how-to | Retain installed ICINT19 run instructions and suite counts; distinguish recipient from development workflow |
| mr10-kit-compiler/tests/README.md | Developers; how-to/reference/evidence | Separate baseline 12-case panel, development probes and supported coroutine suite |
| cambridge-compiler/jcl/README.md; cambridge-compiler/tests/README.md | Developers; directory placeholders | Retain honest unfinished status; no native compiler capabilities implied |
| standard-library/README.md | All technical readers; scope record | Retain design-only status; no BSL implementation or approved API |

## System Extensions documentation

| Path | Audience / class | Candidate disposition |
| --- | --- | --- |
| system-extensions/README.md | Programmers/developers; overview | Retain optional linkage/registration and dataset mapping; link common manuals |
| system-extensions/bcpldemo/README.md | Programmers/developers; API/reference, tutorial candidate and dated evidence | Consolidate accepted API and use in coherent System Extensions manuals; preserve R.5 history and permanent support decision |
| system-extensions/bcpltime/README.md | Programmers/developers; reference/evidence | Consolidate accepted TIMESVC contract and usage; preserve T.0/T.1 reports and direct test commands as historical records where appropriate |
| system-extensions/bcplqsam/README.md | Programmers/developers; API/implementation/evidence | Revise active status against Q.5 qualified closure; preserve Q.1–Q.5 development evidence |
| system-extensions/bcx/README.md | Developers; selection reference/design/evidence | Consolidate current selection model; distinguish accepted BCXCAT known-package selection from earlier designs |
| system-extensions/r2testb/README.md | Developers; test fixture record | Reconcile obsolete verification statement with R.2 closure; explicitly mark isolated G!299 usage incompatible with production CHANGECO |
| system-extensions/template/README.md | Developers; how-to | Retain template purpose; not a package or global allocation; link developer procedure |
| system-extensions/bcplqsam/q1-*, q2-* runbooks; bcpltime/T1-REGRESSION.md | Developers; experiment/acceptance procedures | Historical candidates; inspect remaining live dependencies before any archive action |

The four owner-preferred System Extensions manuals remain the model for DR.1. Do not create new individual API files or silently displace accepted technical contracts during DR.0.

## Project operations and tools

| Path | Audience / class | Candidate disposition |
| --- | --- | --- |
| README.md; packaging/README.md; packaging/operations/README.md; packaging/architecture/README.md | Readers/maintainers; navigation/status | Revise following approved architecture; preserve current status qualifications |
| tools/README.md | Maintainers; command navigation/reference | Consolidate common entry points, avoid duplicate procedures |
| tools/bootstrap/README.md | Developers; how-to plus historical procedure | Separate current build and installed regression instructions from M3/M5.4 evidence |
| tools/mr10/README.md | Developers; how-to | Retain distinction between installed interpreter, baseline panel and development probes |
| tools/mvs/README.md | Operators; navigation/how-to | Retain operational command entry points; reconcile printer trial/default status |
| tools/mvs/mvs-console-README.md | Operators; command reference/how-to | Preserve safety model, tape operation and prerequisite contracts |
| tools/datasets/README.md; config/README.md | Maintainers; how-to/reference | Retain configuration authority and mapping rules; cross-link dataset tool usage |
| tools/checks/README.md | Developers; how-to/reference | Retain preflight scope, checker self-tests and JCL checks |
| tools/reconstruction/README.md | Maintainers; procedure plus dated experiment history | Reconcile historical disabled driver statements with current rebuild procedure; retain safety decisions |
| tools/tests/README.md | Developers; procedure plus evidence | Consolidate current suite selection and printer-window default; preserve calibration and CO.5/CO.6 records |
| tools/distribution/README.md | Maintainers; navigation/reference | Retain reusable interface and BC0005 evidence; do not imply new driver is live-verified |
| tools/distribution/How-to-Create-a-Release-Candidate.md | Maintainers; how-to | Retain guarded workflow and exact verification qualifications |
| docker/README.md | Operators; how-to | Retain actual Docker/TK5 procedure; link explanatory Hercules background |
| packaging/operations/git-mvs-authority.md; operator-wsl-command-policy.md | Maintainers; governing policy | Preserve authority; do not turn policy into tutorial |
| packaging/operations/runtime-development-workflow.md; runtime-object-promotion.md | Developers; policy/procedure mixed with dated gates | Separate reusable safe workflow from historical one-shot promotions; no replay authorization |

## Normative authorities and preservation classes

| Authority | Scope |
| --- | --- |
| packaging/architecture/runtime-and-library-nomenclature.md | Vocabulary and logical taxonomy; reconcile stale implementation status only |
| packaging/architecture/global-number-registry.md | Permanent public allocations, reserved slots and known conflicts |
| packaging/architecture/runtime-contract-v1.md; stack-check-contract.md | Native runtime and stack contracts |
| packaging/milestones/runtime-extensions/runtime-extensions-r0-owner-abi-decisions.md and formal closure | BCEX/BCRG v1, QUERY, global ownership and finalization; known-package selection and evidence qualifications |
| packaging/milestones/qsam/bcplqsam-public-interface.md and Q.5 closure | Public QSAMSVC API and actual acceptance limits |
| packaging/milestones/bcpltime/bcpltime-t1-closure-20261024.md; bcpldemo-supported-reference-decision-20261024.md (under runtime-extensions) | Accepted BCPLTIME and BCPLDEMO support scope; reconcile with public headers and code |
| packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md and CO.5/CO.6 closures | Bounded native and cross-compiler coroutine contracts, limitations |
| config/dspal.yaml | Development dataset and source/member mappings |
| packaging/distribution/manifest/releases/*.yaml; registry/releases.yaml | Frozen per-release selection and release identity/lifecycle; distinct from development mapping |
| tests/suites/*.tsv, MR10 panel manifest and independent expected outputs | Executable test ownership and oracle data, not prose documentation |
| LICENSE.md; THIRD-PARTY-NOTICES.md; PUBLIC-RELEASE-AUDIT.md | Legal scope, historical provenance and audit; preserve unresolved redistribution rights |
| richards-bcpltape/ | Historical primary evidence, including extensionless manual, INDEX, original README notes and docmemo; preserve verbatim |

All 175 archive Markdown paths, 209 baseline milestone paths, five evidence paths and 192 tests Markdown paths are protected pending finer classification. Some are normative, some active instructions and many are evidence. No blanket archive or deletion disposition is justified from location alone. The 130 distribution Markdown paths require separate distinction of active release procedures, frozen documentation, and historical records. Preserve accepted closures and original evidence even where they contain superseded paths or terminology. Private MVS receipts and no-retry markers are outside tracked Git inventory and were not inspected.

## Demonstrated contradictions and stale statements

| Finding | Evidence | Proposed resolution, not implemented |
| --- | --- | --- |
| QSAM README says candidate and Q.5 not closed | system-extensions/bcplqsam/README.md opening and dated Q.4 checkpoint; packaging/milestones/qsam/qsam-q5-closure-20261101.md | State owner-closed with qualifications: full 175 PASS / 1 FAIL / 1 expected SKIP and separate successful case 175 rerun; do not infer missing Q5QINST/Q5QVFY receipts or genuine exceptional CLOSE coverage |
| Global Number Registry row 200 says Q.0 design, not implemented | packaging/architecture/global-number-registry.md line 31 vs Q.5 closure | Update status evidence without changing QSAMSVC:200 allocation |
| R2TESTB README says MVS execution unverified | system-extensions/r2testb/README.md vs R.2 closure JOBs 3091/3092 PASS | Preserve historical fixture role and test evidence; production G!299 belongs to CHANGECO, no conflicting co-link |
| BCPLDEMO includes candidate not yet installed section alongside supported status | system-extensions/bcpldemo/README.md and R.5 closure | Separate current API and supported status from dated candidate history |
| Nomenclature describes provisional registration and pending cross-package evidence | packaging/architecture/runtime-and-library-nomenclature.md vs Runtime Extensions formal closure | Preserve accepted terms, reconcile BCEX/BCRG v1, BCPLREG and known-package selection; retain G!150 conflict and historical fixture limits |
| Q.5 closure refers to old bootstrap-toolchain/extensions path | Q.5 closure line 33 vs current config/dspal.yaml lines 584/601 | Preserve closure unchanged; current reference should identify system-extensions/bcplqsam paths |
| Active reconstruction guide and manual both link empty tools guide | docs/Rebuild-BCPL-for-MVS-from-source.md; docs/Manual-Rebuild-BCPL-for-MVS.md | Replace with approved canonical tool reference before any placeholder removal |

Do not confuse a dated historical statement with a contradiction if its historical context is clear. The inventory distinguishes stale active status from valid chronological evidence. The source-derived compiler options references correctly disclose verification limits and should not be normalized to unsupported guarantees.

## Dependency evidence

A bounded literal Markdown-link path scan covered 17 documents (root, docs indexes and rebuild guides, packaging indexes, extension READMEs, tools indexes and release-candidate guide): 170 relative inline link occurrences, two empty targets (both Guide-to-Project-Tools.md), zero absent paths in this scan. It checked paths against the untruncated Git tree, not heading fragments, reference-style links, links embedded in code, external URLs, generated paths or complete repository navigation.

Source inspection confirms the following direct dependencies:

- `config/dspal.yaml` lines 617–623 maps seven `packaging/distribution/docs/*.txt` files to DIST_DOCS members. These are frozen draft BT0003 inputs; preserve paths and bytes. The RC4 companion supersedes them.
- `tools/distribution/create-release` lines 31, 48, 76, 275–276, 332, 434, 503–506, 589 uses release registry, license/provenance files, MR10 test manifest and generated BT0003/ZIP documentation. It reads LICENSE.md and constructs FB80 documentation, stages and reads it back. The new driver is offline-tested only, not actual-MVS-accepted.
- `tools/distribution/test_create_release.py` lines 54–55, 131, 176 pins license and registry fixtures, seven generated members and ZIP README identity. Preserve these test contracts.
- `tools/distribution/release.py` line 361 reads MR10 panel manifest; `tools/reconstruction/contract.py` line 107 reads config/dspal.yaml. Do not conflate release manifests, development configuration or test oracles.
- `packaging/distribution/manifest/releases/BCPL-0.1.0-rc4.yaml` line 216 references THIRD-PARTY-NOTICES.md. `packaging/distribution/registry/releases.yaml` lines 36, 38, 49, 50, 56 binds acceptance, documentation qualification, closure and publication records. Preserve existing records, paths and immutable versions.

These are demonstrated dependencies, not an exhaustive reference graph. A repository-wide scan of source, JCL, configuration, tests and historical references (including dynamic path construction) is outstanding. No files are safe to relocate/delete on the basis of this checkpoint alone.

## Remaining DR.0 work

1. Expand the dependency scan to all candidate documentation and relevant source/test/configuration files, including extensionless historical material and tool help.
2. Classify remaining active component documents and evidence families with explicit coverage, exceptions and authority; identify contradictory or redundant current content without rewriting accepted records.
3. Produce an owner-reviewable complete disposition inventory, including known unresolved references and any legitimate grouping of homogeneous evidence families.
4. Obtain owner review of DR.0 findings and formal closure before commencing DR.1. Directory layout, manual catalog, canonical authority migration, publishing choices and actual deletion remain unapproved.

No existing files, source, release assets or MVS state have changed. This draft has not been committed.
