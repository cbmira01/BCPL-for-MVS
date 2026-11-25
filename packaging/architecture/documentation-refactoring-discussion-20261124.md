# Diátaxis and semantic documentation refactoring

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 24 November 2026 EST  
**Status:** Documentation Refactoring discussion record; agreed principles, owner preferences and open design questions, not an approved implementation plan.  
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

## Continued owner discussion — Documentation Refactoring

The owner agreed to the general approach and the distinction between product documentation and project documentation, emphasized outline-first development and concise human-facing writing, and favored coherent manuals with chapters rather than separate documents for each component. The following records the direction agreed or preferred so far, not a finalized milestone plan.

### Product documentation and project documentation

**Product documentation** describes the Cambridge BCPL Programming System for MVS 3.8J as a usable programming system. **Project documentation** describes the work of reconstructing, developing, verifying, maintaining and distributing it.

The intended audiences overlap:

| Audience | Primary need |
| --- | --- |
| BCPL programmers | Write, compile, link and execute applications |
| MVS operators | Install, configure and operate the programming system |
| Project developers | Modify, reconstruct and test components |
| Project maintainers | Manage compatibility, acceptance and releases |
| Historical researchers | Understand historical BCPL and reconstruction provenance |

Do not create independent, duplicative documentation collections for each audience. A programmer should be able to use BCPLQSAM without reading the history of Q.0–Q.5; a developer must still be able to find that history and its evidence.

Diátaxis applies to human-facing technical documentation in both bodies of knowledge. Governance, engineering records, machine-readable configuration, legal information and preserved historical materials retain their own purposes and need not conform to Diátaxis. A current technical reference may draw on an accepted contract without duplicating or superseding its authority silently.

### Inside-out, outline-first development

Begin substantial documents with their purpose, audience, Diátaxis classification, title, filename and an outline of section headings. Review the outline for coverage, navigation, overlap and logical progression before filling in the text.

Use similar section structures for related documents where useful. For example, explanations of the MR10 Kit Compiler, demoted Cambridge Compiler and future native-running Cambridge Compiler can share headings for purpose, historical origins, architecture, compilation phases, inputs and outputs, execution environment, runtime and library dependencies, capabilities and limitations, and related documentation.

These are flexible conventions, not mandatory templates. Do not invent empty sections or imply that the unfinished native-running Cambridge Compiler is available.

### Editorial and navigational standards

- Write for human readers: use short sentences, simple direct language and concise explanations, while retaining precise BCPL and MVS terminology.
- Design for both sequential reading and quick consultation. Use predictable, descriptive section headings and linked navigation.
- Use tables for comparisons, inventories, interfaces, parameters and status codes where they improve clarity.
- Use graphics for architecture, data flows, relationships and processes where they convey meaning better than prose. Text-based diagram source (for example, Mermaid) is a proposed practical option, not a mandatory renderer.
- Prefer real BCPL, JCL and assembler examples verified on MVS. Identify illustrative or unverified examples as such.
- Apply the agreed Diátaxis-inspired title and filename conventions consistently: Tutorial on, How to, Explanation of, Reference for. Filenames correspond to titles with hyphens between words.
- Avoid repeated explanations, unnecessary narrative history, empty placeholders and artificial document fragmentation.

### Organize by coherent subject, not individual implementation module

The four Diátaxis types are reader needs, not a requirement for four files for every software component. Prefer a small set of coherent manuals with chapters, adding documents only where reader needs or subject complexity justify it. Common material belongs in one place.

The owner's preferred System Extensions documentation family is:

| Filename | Reader's purpose |
| --- | --- |
| `Tutorial-on-System-Extensions.md` | Learn through a practical programming exercise |
| `How-to-Use-System-Extensions.md` | Select, link, register and use extensions |
| `Explanation-of-System-Extensions.md` | Understand their design, runtime relationship and architecture |
| `Reference-for-System-Extensions.md` | Consult common conventions and individual extension APIs |

The owner specifically favors **one Reference for System Extensions**, with a chapter for each extension, rather than separate API manuals for BCPLDEMO, BCPLTIME and BCPLQSAM. Additional extensions ordinarily extend the existing manuals. No separate API-reference files are proposed for individual extensions at this stage.

Illustrative outline for the reference:

1. Common conventions: calling convention, global-vector assignments, dispatcher, QUERY and registration.
2. BCPLDEMO.
3. BCPLTIME.
4. BCPLQSAM.
5. Appendices or links to the Global Number Registry, declaration headers and related contracts.

Within each extension chapter, use a consistent structure where applicable: purpose; header, global number and API version; operations; parameters and representations; results and status codes; linkage, dependencies and JCL; restrictions and verification qualifications. Describe only the accepted capabilities and accurately identify limitations.

BCPLDEMO is the natural tutorial example because it is the permanent supported reference System Extension. The how-to guide should cover practical selection, linking, registration, JCL allocations, capability queries, errors and using multiple extensions. The explanation should cover the relationship to the Cambridge Runtime Library, global-vector and dispatcher architecture, BCEX/BCRG registration, selection and portability. These outlines are illustrative and remain subject to review.

Other possible coherent subject areas include compilers, runtime, libraries, development tools and distribution. The exact manual catalog and directory structure remain open.

### Repository Markdown, Wiki and navigation

The owner raised the question of using GitHub Wiki versus linkable Markdown files in the main repository. The recommendation is to keep canonical human-authored documentation in repository Markdown: it is versioned with source, included in ordinary clones, frozen with release tags, and can change atomically with code. GitHub Wiki has separate Git history and would complicate these properties. GitHub Pages may later provide a derived presentation, but no additional publishing infrastructure is needed now.

A reader-facing index should present documentation by need (tutorials, how-to guides, explanations and references), with access to project records, historical material and provenance. Subject-oriented physical grouping with Diátaxis-oriented navigation is a candidate approach; no directory layout or Wiki/Pages policy is finalized.

### Initial inventory observations

At the reviewed main revision `7734bde86783282b44bac91c883b1ce00c4dced1`, all ten `docs/Guide-to-*.md` files are empty. The IFOX briefing is over 67 KB; length warrants review but is not alone a defect. The BCPLQSAM component README retains development-stage instructions and status predating Q.5 closure. The nomenclature record combines established terms and earlier implementation proposals. The automated and manual reconstruction guides already distinguish routine rebuilding from maintenance steps.

Treat these as audit leads, not authorization to delete, rewrite or relocate anything. A complete semantic inventory, identification of canonical contracts and reconciliation of stale claims remain to be performed. Preserve all accepted records, RC4 frozen documentation and historical material. The new release orchestration is offline-tested but not yet verified by an actual MVS run; the earlier BC0005 integration does not establish that verification.

### Remaining decisions

The exact document catalog and outlines, directory organization, authority and stable-reference migration, appropriate offline and FB80 representations, release-specific derivation, validation, maintenance and acceptance criteria require further discussion. Preserve the distinction between the development dataset map, frozen release manifests and release registry. Preserve licensing and historical provenance without implying resolved historical redistribution rights.

## References

- [Diátaxis](https://diataxis.fr/) and its [introduction](https://diataxis.fr/start-here/).
- [Runtime and library nomenclature](https://github.com/cbmira01/BCPL-for-MVS/blob/main/packaging/architecture/runtime-and-library-nomenclature.md).
- [Tape artifact release formal closure](https://github.com/cbmira01/BCPL-for-MVS/blob/main/packaging/milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md).
- [RC4 companion documentation](https://github.com/cbmira01/BCPL-for-MVS/blob/main/packaging/distribution/publication/RC4-README.md).

This record captures the post-milestone and subsequent Documentation Refactoring discussions. It does not formally establish the milestone, assign march numbers, finalize the documentation architecture, authorize implementation or authorize MVS operations.
