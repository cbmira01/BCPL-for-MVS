# DR.1 — Architecture and Outlines: proposed documentation architecture

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 24 November 2026 EST  
**Status:** PROPOSED — owner review required; no implementation authorized.  
**Source baseline:** 22ef831baa0376405731db3066c61d925b579e22

## 1. Purpose and design basis

Implement the reader-oriented principles in the [owner discussion](../../architecture/documentation-refactoring-discussion-20261124.md), using the [nomenclature](../../architecture/runtime-and-library-nomenclature.md) and [DR.0 accepted inventory](dr0-record-classification-and-dependencies-20261124.md). Keep the system easy to modify, reconstruct from scratch, test and release. Prefer coherent manuals, not one file per component or per API. Distinguish information semantics from storage and packaging.

The proposal is deliberately incremental: preserve existing authoritative paths and add a small reader-facing catalog. No empty manuals, no bulk movement of engineering records, no separate wiki source.

## 2. Proposed physical and logical organization

```text
README.md                         project and public-release entry point
docs/
  README.md                       reader-facing catalog
  product/
    Tutorial-on-*.md              product manuals
    How-to-*.md
    Explanation-of-*.md
    Reference-for-*.md
  project/
    How-to-*.md                   project manuals
    Explanation-of-*.md
    Reference-for-*.md
  [existing documents]            retain during reconciliation
packaging/                        governance, contracts, decisions, evidence
  architecture/
  milestones/
  operations/
  evidence/
  archive/
  distribution/                   release-specific authorities and evidence
[component directories]           source-local READMEs, headers, examples
tests/                            local case descriptions, sources, oracles
tools/                            local usage/help and executable interfaces
richards-bcpltape/                original historical corpus
```

Proposed directory names are product and project, not four Diátaxis subdirectories per audience or one directory per module. Each collection has a small number of manuals with chapters. The top-level docs index presents both reader need (tutorial, how-to, explanation, reference) and subject; use cross-links rather than duplicate documents. Existing packaging index remains the entrance to records, not a second manual catalog. Component README files remain concise navigational or source-local documents, especially when required by code. No mandatory additional README per subject. No new directories/files solely to reserve future work.

## 3. Proposed first manual catalog and chapter outlines

**Subsequent owner decisions:** see [manual catalog decisions, 25 November 2026](dr1-manual-catalog-owner-decisions-20261125.md). The original proposal below is retained as the discussion baseline; the revised catalog supersedes it where the owner has agreed changes.

Titles and filenames follow the agreed conventions. The following 15 manuals are candidates, not a quota or approved implementation list. Each outline is deliberately bounded. All filenames are proposed relative to docs/product or docs/project. Actual manuals are created only when sufficient verified content exists. Cross-references are part of the outline. Avoid repeating interface tables, command recipes, or status matrices across manuals.

### Product documentation (DR.2)

| File | Audience and purpose | Proposed chapter outline | Main existing source / authority |
| --- | --- | --- | --- |
| Tutorial-on-Writing-Your-First-BCPL-Program.md | New programmer; guided learning | Prerequisites and environment; first START program; compile and run using MR10; inspect output; change the program; next steps | MR10 demos and suite JCL; RC4 companion; real accepted examples |
| How-to-Install-BCPL-from-Tape.md | MVS operator; install exact release | Identify candidate and compatibility; inspect manifest and media; select profile; bootstrap and install; verify directories/DCBs and available functions; diagnose failure | RC4 companion, frozen manifest, installer and accepted records; future release-specific companion overrides general instructions |
| How-to-Compile-and-Run-BCPL-Programs.md | Programmer; perform application tasks | Choose supported compiler environment; source and headers; interpreted MR10 workflow; native application workflow on development system only as supported; JCL/DDs and library selection; diagnostics; verify output | MR10 JCL/options; bootstrap-cambridge README; actual compiler and runner |
| Explanation-of-BCPL-Compilers.md | Programmer/developer; understand compiler lineage and execution | Historical origins; BCPL source to OCODE; INTCODE/ICINT; MR10 Kit Compiler; interpreter-hosted demoted Cambridge Compiler/CG370; unfinished native-running Cambridge Compiler; dependencies and scope | BCPL history/porting; CG370 notes; compiler source and accepted evidence |
| Reference-for-BCPL-Compilers.md | Programmer/developer; precise compiler usage facts | Supported environments and status; MR10 inputs, OPTIONS DD and outputs; demoted Cambridge compiler input/option phases and PARM transport; generated artifacts; diagnostics and limits; native-running compiler historical scope only | MR10 compiler-options.md; bootstrap compiler-options-and-parm.md; actual compiler source and accepted results |
| Explanation-of-the-Cambridge-Runtime-and-Libraries.md | Programmer/developer; understand execution and library architecture | Logical taxonomy; Core Runtime startup and linkage; historical BLIB Base Library; memory and streams; Coroutine Support Library; optional System Extensions; proposed Standard Libraries; user/site libraries | Nomenclature; BCPL memory and runtime explanations; accepted contracts and source |
| Reference-for-the-Cambridge-Runtime-and-Libraries.md | Programmer/developer; consult supported services | Scope and compiler-specific boundaries; representations and globals; Core Runtime services; Base Library (BLIB); Coroutine Support Library; character-stream contracts; error and resource rules; link to System Extensions reference and global registry | Registry, scoped runtime/BCPLIO/coroutine contracts, LIBHDR declarations, actual code and verified results |
| Tutorial-on-System-Extensions.md | Programmer; learn by example | Prerequisites (development native application environment, not unsupported RC4 native workflow); BCPLDEMO; header and QUERY; compile/select/link/run; inspect values and output; modify example | BCPLDEMO permanent support decision, header, verified R.5 examples |
| How-to-Use-System-Extensions.md | Programmer; accomplish practical tasks | Select packages; use headers and QUERY; assemble selection and link; JCL/DD and record geometry; use multiple extensions; handle errors and clean up; verify output | BCXSEL/BCXREQ, BCXCAT, extension READMEs, actual accepted examples |
| Explanation-of-System-Extensions.md | Programmer/developer; understand design | Role relative to Cambridge Runtime Library; GLOBAL dispatcher; BCEX/BCRG v1, BCPLREG, ownership and startup/finalization; known-package selection; portability and limitations | Nomenclature; R.0 ABI decisions including G/QUERY; R.5 and formal closure |
| Reference-for-System-Extensions.md | Programmer/developer; precise accepted API | Common conventions; BCPLDEMO; BCPLTIME; BCPLQSAM; links to Global Number Registry, headers and contracts | Permanent G!203 DEMOSVC; G!201 TIMESVC; G!200 QSAMSVC; accepted API/closures; no separate individual API manuals |

For the System Extensions reference, each package chapter uses purpose, header/global/API version, operations, parameter representations, results/status, linkage/JCL, restrictions and verification qualifications. BCPLDEC is deferred, not an available chapter of executable APIs. R2TESTB is an isolated fixture, not a supported extension. The reference explains the accepted common dispatcher interface without inventing a new ABI. For runtime and compiler references, retain separate MR10-local versus Cambridge native contracts.

### Project documentation (DR.3)

| File | Audience and purpose | Proposed chapter outline | Main existing source / authority |
| --- | --- | --- | --- |
| How-to-Reconstruct-BCPL-from-Source.md | Maintainer; clean-room rebuild | Prerequisites and exact destructive scope; interactive and separately authorized unattended rebuild; what the driver builds; verify installation; manual recovery/stepwise rebuild; where to run regressions | Existing canonical rebuild guide, manual rebuild, Docker and DSPAL docs, executable rebuild driver |
| How-to-Develop-and-Test-BCPL-for-MVS.md | Developer; modify safely and verify | Git/MVS ownership; edit/build candidate; focused BCPL/IFOX/IEWL/JES tests; suite selection and expected results; debug output and failure evidence; promotion/rollback; full regression and approval | Runtime workflow/promotion, tools/checks/tests/bootstrap/MR10, operator policy and actual suites |
| Reference-for-Project-Tools.md | Developer/operator; consult tool interfaces | Docker/TK5 and console; DSPAL; compile and build tools; reconstruction; test coordinators; release tooling; arguments, output, prerequisites and destructive boundaries; links to procedures | Tools READMEs, actual executable help/source, config, tests; not duplicated how-to recipes |
| How-to-Create-a-Release-Candidate.md | Maintainer; prepare, produce and verify release | Scope and prerequisites; identity and manifest; reserve/prepare; MVS tape production and installation; independent verification; private evidence review; separate publication approval | Existing canonical tools/distribution/How-to-Create-a-Release-Candidate.md; registry, manifest, release driver and tests |

The existing release how-to is already correctly named. Proposed treatment is to catalog it at its current canonical path initially (no second copy); decide whether to move only after its dependencies are checked. The existing automated rebuild and manual stepwise rebuild remain distinct source procedures during drafting; the proposed consolidated how-to may retain a linked manual-maintenance appendix or separate canonical procedure if outline review shows a single file would obscure the task. Do not reduce operational safety or silently change command behavior.

### Shared technical background — decision required

The current 14 orientation briefings are not all product usage material. Proposed treatment: consolidate overlapping System/370, MVS, JCL, IFOX, IEWL and Hercules explanations into a coherent **Explanation of the MVS Programming Environment** with chapters for machine/data model, address spaces and services, datasets/records, JCL/JES, assembler/linkage/loading, diagnostics and Hercules. This would be a sixteenth manual under docs/project, linked from product manuals; the historical BCPL and allocation briefings instead feed the compiler/runtime explanations. The original broad briefings remain until coverage and source accuracy are verified. Alternative: retain the educational briefings as a distinct background collection rather than rewrite them. Owner approval is requested on this choice; no artificial size target.

## 4. Authority and status model

- Canonical human-authored prose: UTF-8 Markdown in GitHub main; version it with code and freeze release-specific documentation by tag/manifest. No independent Wiki authority. GitHub Pages is a possible derived view only; no new infrastructure now.
- Normative assignments, accepted ABI/API and evidence remain authoritative at existing paths, not silently superseded by a manual. A reference chapter cites the governing contract and source/header, specifies scope and validation, and summarizes only as necessary. If authority is to migrate, require explicit owner decision, traceability and equivalent contract review.
- For runtime v1/v2 and DEVOBJ BCPLIO, distinguish candidate-scoped evidence from current installed production. Do not declare either comprehensive without reconciliation. Preserve accepted archived Decision G and QUERY records.
- A public header declares names/values, not the whole behavioral contract. Git sources define what is built; actual MVS/BCPL/IFOX/IEWL/JES results establish verified behavior; owner closures establish accepted scope. Conflicts are recorded and reviewed, never silently resolved by narrative.
- Release manifest and registry own exact release content and identity. RC4 / BC0004 companion, publication record and original tape bytes remain frozen. Development main describes a different state, including CAMBCOMP, and cannot imply RC4 supports native compilation. The new release driver remains offline-tested only. Keep legal/provenance and unresolved historical redistribution rights unchanged.
- No duplicated status matrix in every manual. Root README retains short current environment overview; detailed facts link to the appropriate accepted source. Each procedure states its applicable environment and release or development scope. Do not omit qualifications in the interest of brevity.

## 5. Navigation, editorial and stable-reference conventions

The proposed docs index starts with "Learn", "Accomplish a task", "Understand", "Consult a reference" and links to product/project manuals. Provide subject access and links to project records, release-specific companion and historical materials. Descriptive headings and stable relative links serve sequential reading and quick consultation. Use a short chapter index for long manuals, numbered headings only where helpful, tables for contracts and comparisons, and simple text diagrams where clearer. Mermaid may be used later if supported by the chosen representations; never make essential information unavailable on MVS. Avoid repeating chapter text in indexes.

Use the agreed title prefixes, title-matching hyphenated filenames and established project terminology. Include purpose, audience, applicable compiler/profile/version, prerequisites and verification limitations where relevant, not a mandatory boilerplate block. Put a warning immediately before destructive steps; use real BCPL, assembler and JCL from accepted examples, mark illustrative/unverified material. Retain code blocks in appropriate source format, including fixed-card constraints where relevant. No generated empty placeholders.

### Incremental migration

1. Approve catalog, outline boundaries and authority mapping. Add only substantive approved manuals in DR.2/DR.3.
2. Preserve every existing path while drafting; link existing canonical procedures until replacement is reviewed. Record old-to-new section mapping and check technical coverage, source references and executable dependencies before changing navigation.
3. For obsolete active prose that is safe to supersede, retain a concise pointer at the old path where useful, or archive with explicit owner-approved disposition and stable immutable references. Do not replace normative contracts, evidence or required fixture READMEs with pointers.
4. Ten empty guides are conditional removal candidates, not approved deletions; resolve known inbound links and check remaining dependencies first. The prior dependency scan is qualified, so no unsupported absence claims.
5. Retain frozen release files, all 13 coroutine case READMEs, source references, test oracles, legal files and FB80 inputs. Do not relocate milestone candidate sources or alter accepted history.

## 6. Distribution and validation handoff

DR.4 should assemble version-specific documentation from approved Markdown, frozen manifest/registry and verified scope. Prefer minimal reproducible offline representations (HTML or plain text; PDF only if useful), and concise MVS-readable FB80 members for recipient tasks. Keep legal/provenance bytes and companion identity. Rendering/encoding tool choice, exact member mapping and offline package contents remain DR.4 design questions. Require deterministic output, explicit encoding, no silent truncation, record-length validation and actual MVS readback where warranted. Do not modify existing BT0003 or RC4.

DR.5 verifies content against source/contracts and accepted MVS evidence, validates links/anchors and transformations, and checks retained reconstruction, regression and release capabilities. A live test requires appropriate owner authorization. No MVS execution is needed for DR.1 planning. DR.6 defines maintenance and release integration before closure.

## 7. Owner decisions required before DR.1 closure

1. Approve canonical repository Markdown, no independent Wiki, optional derived Pages.
2. Approve the proposed docs/product and docs/project arrangement with reader-need navigation, preserving existing record and dependency paths.
3. Approve or revise the 15-manual catalog and outlines, including the proposed shared MVS background manual (sixteenth) versus retaining the briefings.
4. Approve the authority model, incremental migration, stable-reference and preservation policy; specify any contract authority migration separately.
5. Confirm that DR.4 rendering choices remain deferred and that DR.2 may begin only after formal DR.1 acceptance.

This is a design proposal recorded under the owner's commit authority. No directory creation for manuals, code changes, rewrites, moves, deletions, release activity or MVS operations are authorized or performed by this record.
