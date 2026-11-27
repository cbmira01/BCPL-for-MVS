# Milestone — Documentation Refactoring

**Project:** BCPL for MVS 3.8 Reconstruction  
**Owner approval:** 24 November 2026 EST — seven marches DR.0–DR.6 approved; DR.0 commencement authorized.  
**Status:** DR.0 CLOSED (qualified); DR.1 CLOSED; DR.2 CLOSED (qualified); DR.3 CLOSED (qualified); DR.4 CLOSED (qualified); DR.5 IN PROGRESS; DR.6 NOT STARTED.  
**Authority:** GitHub `main`. Inventory baseline: `ed0f8066859ed4e1a310bbb91520d0d629c5dca3`.

## Objective

Make the documentation for the Cambridge BCPL Programming System for MVS 3.8J and its reconstruction project coherent, accurate, concise, navigable, maintainable and distributable. Support the four governing objectives: easy to modify, reconstruct from scratch, test, and produce a release. Reduce complexity rather than redistribute it.

## Governing principles

Follow the [owner discussion record](../../architecture/documentation-refactoring-discussion-20261124.md) and [runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md). Distinguish product documentation from project documentation and information semantics from physical representation. Apply Diátaxis to reader-facing technical documentation, not governance, historical evidence, configuration, legal records or archival material. Prefer one authoritative source, coherent manuals with chapters, outline-first development, consistent navigation, concise prose, tables and useful diagrams. Prefer real BCPL, JCL and assembler examples verified on MVS; identify unverified examples.

| Type | Title convention |
| --- | --- |
| Tutorial | Tutorial on … |
| How-to guide | How to … |
| Explanation | Explanation of … |
| Reference | Reference for … |

Filenames correspond to titles, with hyphens between words. The preferred System Extensions family is `Tutorial-on-System-Extensions.md`, `How-to-Use-System-Extensions.md`, `Explanation-of-System-Extensions.md`, and `Reference-for-System-Extensions.md`. The reference contains chapters for BCPLDEMO, BCPLTIME, BCPLQSAM and future extensions. Do not require four documents per component or subject.

## Approved roadmap

| March | Title | Status | Principal deliverable |
| --- | --- | --- | --- |
| DR.0 | Inventory and Classification | CLOSED (qualified) | Inventory, authority, dependencies and candidate dispositions |
| DR.1 | Architecture and Outlines | CLOSED | Owner-approved catalog, directory structure, navigation and outlines |
| DR.2 | Product Documentation | CLOSED (qualified) | Manuals for BCPL programmers and MVS operators |
| DR.3 | Project Documentation | CLOSED (qualified) | Development, reconstruction, testing, maintenance, promotion and release procedures |
| DR.4 | Documentation Distribution | CLOSED (qualified) | Owner-approved Markdown and existing MVS FB80 distribution policy; additional formats and tests deferred |
| DR.5 | Validation and Reconciliation | IN PROGRESS | Technical accuracy, consistency and operational verification |
| DR.6 | Acceptance and Closure | NOT STARTED | Maintenance policy, release integration and formal acceptance |

### DR.0 — Inventory and Classification

Identify relevant information, audience, subject, Diátaxis type where applicable, authority, condition, dependencies and proposed disposition (retain, consolidate, revise, archive or remove). Identify redundant, contradictory, obsolete, incomplete and unnecessarily verbose documents. Preserve historical material and accepted records. Include documentation embedded in tools, tests and release processes; do not assume the Markdown census is exhaustive. No relocation, deletion or bulk rewriting. Acceptance requires an inventory with explicit coverage and limitations, identification of normative sources and dependencies, and owner review of findings. See [initial inventory](dr0-inventory-and-classification-20261124.md). See also the [semantic inventory](dr0-semantic-inventory-20261124.md) and [record classification and dependency review](dr0-record-classification-and-dependencies-20261124.md).

Owner accepted DR.0 and authorized DR.1 and commits on 24 November 2026. See [formal qualified closure](dr0-formal-qualified-closure-and-dr1-transition-20261124.md).

### DR.1 — Architecture and Outlines

Agree on coherent subject areas, catalog, canonical source/representation, directory organization, stable references, filenames, navigation and outlines before implementation. Repository Markdown and GitHub presentation are owner-approved; no independent Wiki, Pages deferred pending need. Detailed offline/MVS representations and rendering remain DR.4 design decisions. Obtain owner approval before bulk rewriting or relocation. See [proposed architecture and outlines](dr1-architecture-and-outlines-proposal-20261124.md), [manual catalog decisions](dr1-manual-catalog-owner-decisions-20261125.md) and [owner decision on normative reference manuals](dr1-reference-authority-owner-decision-20261125.md), and [owner-approved directory scheme](dr1-directory-organization-owner-decision-20261125.md), [canonical Markdown decision](dr1-canonical-markdown-owner-decision-20261125.md), and [navigation decision](dr1-navigation-owner-decision-20261125.md). See [manual outlines and approved migration approach](dr1-manual-outlines-and-migration-20261125.md).

Owner approved the chapter outlines and authorized DR.2 on 25 November 2026. See [formal closure and DR.2 transition](dr1-formal-closure-and-dr2-transition-20261125.md).

### DR.2 — Product Documentation

Develop approved manuals for programmers and operators. Distinguish MR10 Kit Compiler, interpreter-hosted demoted Cambridge Compiler, and unfinished native-running Cambridge Compiler. Accurately state installed, distributed, verified and unfinished capabilities. Retain technical contracts and their authority.

Owner accepted qualified closure on 25 November 2026 after correction of two acceptance-review defects. All thirteen product manuals and 107 chapters are drafted; individual normative transfers and detailed reconciliation remain pending. See [formal qualified closure and DR.3 transition](dr2-formal-qualified-closure-and-dr3-transition-20261125.md).

### DR.3 — Project Documentation

Consolidate active reconstruction, development, testing, maintenance, promotion and release instructions. Separate current procedures from historical investigations and accepted engineering records. See the [DR.3 kickoff in the closure record](dr2-formal-qualified-closure-and-dr3-transition-20261125.md).

Owner directed acceptance and transition on 25 November 2026. All five project manuals and 45 chapters are drafted and committed; complete normative reconciliation and target validation remain pending. See [formal qualified closure and DR.4 transition](dr3-formal-qualified-closure-and-dr4-transition-20261125.md).

### DR.4 — Documentation Distribution

Establish GitHub, offline and MVS FB80 representations. Derive release-specific information from frozen manifests and the release registry where practical. Preserve RC4 frozen documentation and all published bytes. Validate transformation and encoding fidelity; do not silently truncate records.

Owner approved retaining canonical UTF-8 Markdown and the existing small, plain-text project-EBCDIC FB80 documentation set, unchanged tape layout and existing release generation. Offline rendering, complete manual distribution and additional documentation testing are deferred. No new tooling or target verification is claimed. See [formal qualified closure and DR.5 transition](dr4-formal-qualified-closure-and-dr5-transition-20261125.md).

### DR.5 — Validation and Reconciliation

Verify technical accuracy, terminology, compiler status, normative contracts, links, navigation, examples, operational procedures, transformation fidelity and retained reconstruction/regression/release capabilities. Seek actual BCPL, IFOX, IEWL, JES and MVS evidence where warranted. Offline checks are not target-system verification. Identify remaining qualifications explicitly. DR.5 begins under the owner-approved transition; see [DR.4 closure and DR.5 kickoff](dr4-formal-qualified-closure-and-dr5-transition-20261125.md). Respect the DR.4 deferral of dedicated documentation transformation tests; technical reconciliation and verification of software behavior remain in scope.

On 27 November 2026 the owner approved the [first individual normative transfer, BCPLQSAM rollback precedence and historical BLIB diagnostic qualifications](dr5-query-authority-and-qsam-precedence-acceptance-20261127.md). The owner subsequently approved the [common registration and finalizer authority transfer](dr5-registration-authority-transfer-acceptance-20261127.md), including bounded post-structural diagnostic ordering. The owner also approved the [three package-specific API transfers](dr5-extension-package-api-authority-transfer-acceptance-20261127.md). The owner then approved the [BCPLIO and Base Library authority transfers](dr5-stream-and-base-library-authority-transfer-acceptance-20261127.md). The owner then approved the [remaining public Core Runtime authority transfer and focused DEBUGINT correction](dr5-core-runtime-authority-transfer-acceptance-20261127.md). The owner then approved the [Coroutine Support Library authority transfer](dr5-coroutine-library-authority-transfer-acceptance-20261127.md). The owner then approved the [remaining MR10 runtime and library authority transfer](dr5-mr10-runtime-library-authority-transfer-acceptance-20261127.md). The owner then approved the [BCPL language authority transfer](dr5-language-authority-transfer-acceptance-20261127.md). The owner then approved the [BCPL compiler authority transfer](dr5-compiler-authority-transfer-acceptance-20261127.md). The owner then approved the [Project Tools authority transfer](dr5-project-tools-authority-transfer-acceptance-20261127.md). The owner then approved the [BCX selection-macro authority transfer](dr5-selection-macro-authority-transfer-acceptance-20261127.md). All five reference manuals now govern their planned supported public contracts, subject to the stated qualifications. The [manual navigation audit](dr5-documentation-navigation-and-reconciliation-audit-20261127.md) verifies all 715 literal relative link occurrences and eight heading fragments across the 18 manuals and catalog. The [offline verification record and target gates](dr5-offline-verification-and-target-gates-20261127.md) records 14 actual scoped offline unit-test passes and independent suite-inventory validation; complete checkout-dependent checks are blocked locally and required before target execution. The [host-test reconciliation](dr5-host-test-reconciliation-20261127.md) records corrections for the 19 offline failure/error reports. The [independent reconstruction host verification](dr5-independent-reconstruction-host-verification-20261127.md) records 68 actual reconstruction test passes, including all six previously failing synthetic integration paths, and supersedes the earlier assignment of offline checks to the operator. The [complete host verification](dr5-debugint-offline-and-ci-verification-20261127.md) records all five gates PASS at `9ce68413a9e61194adde4de7ad200768eeb31666` (954 checker and 38 release tests, inventory, bootstrap inputs and DEBUGINT preflight), using a GitHub-hosted Linux runner. The authorized focused DEBUGINT target run is next. Detailed DEBUGINT behavior, private interfaces, repository-wide inbound dependency qualification and target operational gates remain open.

### DR.6 — Acceptance and Closure

Establish practical maintenance and release-integration policy. Record verified results and remaining qualifications; obtain formal owner acceptance and closure.

## Preservation and scope boundaries

Preserve published RC4, frozen documentation, manifests, registry records, Global Number Registry assignments, accepted milestone/march records, historical sources and original documentation, MVS verification evidence, licensing, attribution and provenance. Preserve reconstruction, regression and release capabilities. Do not reopen completed milestones merely to reorganize documentation. Historical redistribution rights remain unresolved. Distinguish the development dataset map from release manifests and registry. Preserve private evidence and no-retry markers outside Git.

## Acceptance criteria

- Authoritative technical information is identifiable and not silently superseded.
- Current documentation is concise, coherent, navigable and accurately represents compiler capabilities and limitations.
- Redundant and obsolete active documentation is substantially reduced.
- Examples and procedures are verified where appropriate, with limitations recorded.
- Release-specific documentation describes its corresponding distribution.
- Historical records, contracts and accepted evidence remain preserved.
- Reconstruction, regression and release capabilities remain intact.
- Owner approves maintenance policy, qualifications and formal closure.

## Working authority

Discuss major design choices before implementation; test before committing whenever possible; obtain owner approval for commits and state-changing operations. Reserve owner-facing command blocks for necessary MVS operations. DR.0 approval does not authorize MVS changes, new release production, publication, bulk rewriting, relocation or deletion. No march is closed without owner approval.
