# Milestone — Documentation Refactoring

**Project:** BCPL for MVS 3.8 Reconstruction  
**Owner approval:** 24 November 2026 EST — seven marches DR.0–DR.6 approved; DR.0 commencement authorized.  
**Status:** DR.0 CLOSED (qualified); DR.1 IN PROGRESS; DR.2–DR.6 NOT STARTED.  
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
| DR.1 | Architecture and Outlines | IN PROGRESS | Owner-approved catalog, directory structure, navigation and outlines |
| DR.2 | Product Documentation | NOT STARTED | Manuals for BCPL programmers and MVS operators |
| DR.3 | Project Documentation | NOT STARTED | Development, reconstruction, testing, maintenance, promotion and release procedures |
| DR.4 | Documentation Distribution | NOT STARTED | GitHub, offline and MVS documentation representations |
| DR.5 | Validation and Reconciliation | NOT STARTED | Technical accuracy, consistency and operational verification |
| DR.6 | Acceptance and Closure | NOT STARTED | Maintenance policy, release integration and formal acceptance |

### DR.0 — Inventory and Classification

Identify relevant information, audience, subject, Diátaxis type where applicable, authority, condition, dependencies and proposed disposition (retain, consolidate, revise, archive or remove). Identify redundant, contradictory, obsolete, incomplete and unnecessarily verbose documents. Preserve historical material and accepted records. Include documentation embedded in tools, tests and release processes; do not assume the Markdown census is exhaustive. No relocation, deletion or bulk rewriting. Acceptance requires an inventory with explicit coverage and limitations, identification of normative sources and dependencies, and owner review of findings. See [initial inventory](dr0-inventory-and-classification-20261124.md). See also the [semantic inventory](dr0-semantic-inventory-20261124.md) and [record classification and dependency review](dr0-record-classification-and-dependencies-20261124.md).

Owner accepted DR.0 and authorized DR.1 and commits on 24 November 2026. See [formal qualified closure](dr0-formal-qualified-closure-and-dr1-transition-20261124.md).

### DR.1 — Architecture and Outlines

Agree on coherent subject areas, catalog, canonical source/representation, directory organization, stable references, filenames, navigation and outlines before implementation. Repository Markdown is recommended, not a finalized physical architecture. Wiki, Pages, offline representation and rendering details remain open. Obtain owner approval before bulk rewriting or relocation. See [proposed architecture and outlines](dr1-architecture-and-outlines-proposal-20261124.md).

### DR.2 — Product Documentation

Develop approved manuals for programmers and operators. Distinguish MR10 Kit Compiler, interpreter-hosted demoted Cambridge Compiler, and unfinished native-running Cambridge Compiler. Accurately state installed, distributed, verified and unfinished capabilities. Retain technical contracts and their authority.

### DR.3 — Project Documentation

Consolidate active reconstruction, development, testing, maintenance, promotion and release instructions. Separate current procedures from historical investigations and accepted engineering records.

### DR.4 — Documentation Distribution

Establish GitHub, offline and MVS FB80 representations. Derive release-specific information from frozen manifests and the release registry where practical. Preserve RC4 frozen documentation and all published bytes. Validate transformation and encoding fidelity; do not silently truncate records.

### DR.5 — Validation and Reconciliation

Verify technical accuracy, terminology, compiler status, normative contracts, links, navigation, examples, operational procedures, transformation fidelity and retained reconstruction/regression/release capabilities. Seek actual BCPL, IFOX, IEWL, JES and MVS evidence where warranted. Offline checks are not target-system verification. Identify remaining qualifications explicitly.

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
