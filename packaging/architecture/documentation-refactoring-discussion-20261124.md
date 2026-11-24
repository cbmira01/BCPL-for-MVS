# Diátaxis and semantic documentation refactoring

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 24 November 2026 EST  
**Status:** Post-milestone discussion record; proposed direction, not an approved implementation plan.  
**Repository baseline:** `main` at `e5eca51ed2738c4f8532e5ee909cea3c55acd3d5`

## Purpose

Following the formal qualified closure of **Tape artifact release**, consider a semantic refactoring of project documentation. The objective is to make information easier to find, understand, maintain and distribute, while preserving accepted engineering evidence and historical records.

The project must remain easy to modify, reconstruct from scratch, test and release. Documentation should support those objectives rather than introduce unnecessary bureaucracy.

## Diátaxis as the technical documentation philosophy

Diátaxis organizes technical documentation around the reader's needs, not the repository layout or the implementation structure. Its four kinds of documentation have distinct purposes:

| Kind | Reader's need | Project example |
| --- | --- | --- |
| Tutorial | Learn through guided practical experience | Write, compile and execute a first BCPL program on MVS |
| How-to guide | Accomplish a particular task | Install from tape, reconstruct from source, run regressions or produce a release |
| Explanation | Understand a subject and its rationale | Cambridge Compiler architecture, OCODE and INTCODE, coroutine implementation |
| Reference | Obtain precise technical information | BCPLQSAM public API, Global Number Registry, native runtime ABI |

Classify a document according to its primary purpose. A tutorial is not merely a sequence of operational instructions; a how-to guide assumes a reader with a task to accomplish. Explanation provides understanding rather than instructions, and reference describes established facts, interfaces and contracts accurately.

## Proposed normative naming conventions

Use recognizable title prefixes for technical documents, with filenames corresponding directly to their titles. These are project conventions inspired by Diátaxis, not requirements imposed by Diátaxis itself.

| Kind | Title pattern | Example filename |
| --- | --- | --- |
| Tutorial | Tutorial on … | `Tutorial-on-Writing-Your-First-BCPL-Program.md` |
| How-to guide | How to … | `How-to-Install-BCPL-from-Tape.md` |
| Explanation | Explanation of … | `Explanation-of-OCODE-and-INTCODE.md` |
| Reference | Reference for … | `Reference-for-BCPLQSAM.md` |

Prefer **Reference for** over **Reference to**, which can suggest a citation or link rather than a technical reference document.

Use clear subjects, retain established project terminology and avoid ambiguous general-purpose labels such as “Guide to,” “Notes on,” “Overview of” and “Briefing on” when a more precise Diátaxis title is appropriate. Existing historical titles and identifiers need not be renamed.

A document's title establishes a contract with its reader. Its content must fulfill the purpose promised by that title. The filename should remain meaningful outside its original directory, including in search results and distributed documentation.

## Distinguish documentation semantics from representation

Extend the existing architectural principle of distinguishing what code does from how it is packaged to project information. Distinguish what information means from how it is stored, formatted, maintained and distributed.

Maintain one authoritative source for each fact or body of content in GitHub. Where practical, derive appropriate representations from that authority rather than maintaining independent copies:

- GitHub-readable technical documentation, such as Markdown.
- Offline manuals, potentially HTML or PDF.
- MVS-readable documentation distributed as PDS members with appropriate record formats, including FB80 where required.

The specific canonical formats, directory structure, document metadata and rendering tools remain design decisions. Do not introduce an elaborate documentation framework merely to implement a naming convention.

Release-specific dataset inventory, version, supported capabilities and installation information should derive from the relevant frozen manifests and release metadata where practical. Distributed documentation must describe the exact release with which it is delivered. Validate transformations for record width, encoding and preservation of meaning.

## Information outside the Diátaxis taxonomy

Diátaxis should govern reader-facing technical documentation, not every file in the repository. Keep these information classes logically distinct:

- Project governance, milestones and marches.
- Design decisions, acceptance records, test evidence and project history.
- Machine-readable manifests, registries and configuration.
- Copyright, licensing, attribution and historical provenance.
- Preserved historical source material and original documentation.

Normative technical contracts may serve as authoritative reference material; associated approval records and engineering evidence retain their separate purposes. Avoid duplicating current status in multiple narrative indexes. Preserve accepted evidence and original historical records without requiring them to function as current operating instructions.

## Repository and distribution consistency

The repository and tape must communicate consistent technical scope, licensing, attribution and provenance. The project's MIT license applies to original project work unless otherwise marked; it does not establish new rights over historical material. The preservation-first policy and unresolved historical redistribution rights must remain accurately represented.

RC4 illustrates the cost of separately maintained documentation: its mandatory companion guide supersedes stale BT0003 notes. Preserve the accepted RC4 artifact, companion guide, release tag, frozen manifest, and acceptance evidence. Future releases should generate or assemble coherent release-specific documentation before acceptance rather than rely on corrective companion documents where avoidable.

## Refactoring approach

Favor incremental semantic improvement over a wholesale rewrite. Identify authoritative sources and reader needs before reorganizing files. Consolidate redundant current information, separate obsolete instructions from active procedures, and retain historical evidence and links. Do not create empty manuals or impose a uniform format where it adds no value.

The technical work should continue to favor real BCPL, JCL and assembly, verified through MVS, the compiler and MVS system tools. Documentation and tooling changes should make that work simpler.

## References

- [Diátaxis](https://diataxis.fr/) and its [introduction](https://diataxis.fr/start-here/).
- [Runtime and library nomenclature](https://github.com/cbmira01/BCPL-for-MVS/blob/main/packaging/architecture/runtime-and-library-nomenclature.md).
- [Tape artifact release formal closure](https://github.com/cbmira01/BCPL-for-MVS/blob/main/packaging/milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md).
- [RC4 companion documentation](https://github.com/cbmira01/BCPL-for-MVS/blob/main/packaging/distribution/publication/RC4-README.md).

This record captures the post-milestone discussion. It does not open a milestone, assign march numbers, approve a documentation architecture, authorize a repository refactoring or authorize MVS operations.
