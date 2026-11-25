# DR.1 — Detailed manual outlines and approved migration approach

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.1 — Architecture and Outlines (IN PROGRESS)  
**Date:** 25 November 2026 EST  
**Status:** Migration and reconciliation approach owner-approved; chapter outlines proposed for owner review. No implementation or individual authority transfer authorized.  
**Reviewed main:** 1bb0832d6435f997d3b4e2bbf53593ffa6f25496

## Basis and conventions

Follow the [manual catalog](dr1-manual-catalog-owner-decisions-20261125.md), [reference authority](dr1-reference-authority-owner-decision-20261125.md), [directory organization](dr1-directory-organization-owner-decision-20261125.md), [canonical Markdown](dr1-canonical-markdown-owner-decision-20261125.md) and [navigation](dr1-navigation-owner-decision-20261125.md) decisions. There are eighteen manuals, thirteen product and five project/background. The chapter headings and subtopics below describe intended coverage; not fixed word counts. Source leads are starting points, not a fully verified clause-level mapping. Proposed paths are planning text, not links to nonexistent documents.

Each tutorial teaches through runnable examples, each how-to supports tasks, each explanation develops understanding, each reference specifies facts and contracts. Prefer real BCPL, JCL and assembler with actual MVS evidence. State applicable compiler/release scope and limitations. Reference authority transfers only after reconciliation and approval.

## Product manuals (DR.2)

### Tutorial on BCPL Programming

**Path:** `docs/product/Tutorial-on-BCPL-Programming.md`  
**Audience and purpose:** New programmers; progressive executable exercises.  
**Source leads:** MR10 language-demo and bcpl-demo; historical language sources; native regression examples.

1. Your first BCPL program — START, compile, run, inspect and modify.
2. Constants, variables and declarations — LET, MANIFEST, scope and assignment.
3. Expressions and operators — arithmetic, logical and relational.
4. Conditional execution and iteration — decisions, repetition and termination.
5. Functions and routines — calls, arguments, results and recursion.
6. Vectors, pointers and indirection — indexing, aliases and bounds.
7. Strings and character manipulation — representation, bytes and I/O.
8. Global variables and separate compilation — declarations, headers and modules.
9. Dynamic memory management — allocation, ownership, release and failure.
10. Data structures and algorithms — search, sorting, lists and trees.
11. Coroutines — cooperative producer/consumer within verified scope.
12. Writing a substantial BCPL application — integrate skills and verify output.

**Boundary:** Start with MR10; mark native prerequisites. Teach library calls through use rather than duplicate contracts. Use real examples and expected output.

### Reference for the BCPL Language

**Path:** `docs/product/Reference-for-the-BCPL-Language.md`  
**Audience and purpose:** Programmers and compiler developers; implemented syntax and semantics.  
**Source leads:** Historical MR10 and Cambridge SYN/TRN, manuals, current compiler inputs and tests.

1. Lexical structure — identifiers, reserved words, literals, comments and source characters.
2. Syntax and grammar — notation, grouping and syntactic categories.
3. Data representation — words, truth values, addresses and strings.
4. Declarations and scope — LET, GLOBAL, MANIFEST, STATIC and binding.
5. Expressions and operator precedence — associativity, evaluation and indirection.
6. Commands and control structures — assignments, loops, switches, labels and RESULTIS.
7. Functions and routines — definitions, calls, parameters, RETURN and results.
8. Storage and addressing — local vectors, pointer expressions and lifetime.
9. Program structure and separate compilation — sections, GET, globals and START.
10. Language dialects and implementation differences — verified MR10/Cambridge feature comparison, unsupported and unverified constructs.

**Boundary:** Normative language semantics after approved transfer. Compiler options and library ABI belong in their own references. No implied modern dialect support.

### Explanation of BCPL Compilers

**Path:** `docs/product/Explanation-of-BCPL-Compilers.md`  
**Audience and purpose:** Programmers and developers; understand lineage, pipelines and execution environments.  
**Source leads:** BCPL history and porting, CG370 architecture notes, historical corpus and compiler source maps.

1. BCPL origins and surviving compiler materials.
2. Source translation — SYN, TRN and OCODE.
3. Back ends — CGI to INTCODE and CG370 to System/370 assembler.
4. MR10 Kit Compiler — ICINT19 and interpreted execution.
5. Interpreter-hosted demoted Cambridge Compiler — bootstrap, CAMBCOMP and native application output.
6. Native-running Cambridge Compiler — recovered design and unfinished reconstruction.
7. Assembly, link-edit, runtime and application relationships.
8. Compatibility and evidence — shared and distinct execution domains.

**Boundary:** Distinguish compiler execution from generated application execution and RC4 from development state.

### Reference for BCPL Compilers

**Path:** `docs/product/Reference-for-BCPL-Compilers.md`  
**Audience and purpose:** Programmers and developers; compiler interfaces, options and constraints.  
**Source leads:** MR10 compiler-options.md; bootstrap-cambridge/compiler-options-and-parm.md; compiler sources, JCL and evidence.

1. Applicable environments and release/development boundaries.
2. MR10 Kit Compiler — source, OPTIONS DD, defaults, flags, OCODE/INTCODE and diagnostics.
3. Interpreter-hosted demoted Cambridge Compiler — source, two-phase grammar, bootstrap transport, front-end and CG370 switches.
4. Native-running Cambridge Compiler — recovered historical interface and EXEC PARM, unfinished status.
5. Output and intermediate artifacts — generated records and object/load boundaries.
6. Diagnostics and constraints — workspace limits and verification scope.
7. Comparison tables — option transport, phase-specific meanings, inputs and outputs.

**Boundary:** Preserve distinct option grammars and first/second-phase N. Source-derived options are not all independently MVS-tested.

### How to Compile and Run BCPL Programs

**Path:** `docs/product/How-to-Compile-and-Run-BCPL-Programs.md`  
**Audience and purpose:** BCPL programmers; execute application workflows.  
**Source leads:** MR10 JCL suite guidance, examples, tools/mr10, bootstrap compiler and accepted jobs.

1. Choose compiler and verify installation scope.
2. Prepare source members, headers and DDs.
3. Compile and run an MR10 program with installed ICINT19.
4. Compile separately and combine MR10 modules where supported.
5. Compile native applications on the development system — CAMBCOMP, IFOX, IEWL and GO.
6. Link runtime, libraries and optional packages.
7. Inspect JES output, return codes and application results.
8. Diagnose compilation, assembly, linkage and execution failures.

**Boundary:** Separate recipient MVS JCL from host automation. RC4 supports MR10, not native compilation. Link reference for options.

### Explanation of the Cambridge Runtime and Libraries

**Path:** `docs/product/Explanation-of-the-Cambridge-Runtime-and-Libraries.md`  
**Audience and purpose:** Programmers and developers; understand service architecture.  
**Source leads:** Nomenclature, runtime interface conventions, memory briefing, BCPLIO and coroutine records.

1. Logical taxonomy and physical modules.
2. Core Runtime — startup, entry, globals, calling convention, stack and termination.
3. Base Library (BLIB) — origins, separate compilation and essential services.
4. Memory, vectors and character streams — ownership and MVS translation.
5. Coroutine Support Library — cooperative transfers, contexts and lifecycle.
6. MR10 interpreted runtime comparison — ICINT19, BLIBI/ICLIB and separate global domain.
7. System Extensions — optional linkage and registration.
8. Standard Libraries and User/Site Libraries — current and proposed scope.

**Boundary:** Explain rationale and architecture; link normative tables. Coroutine Support Library is separate from historical BLIB.

### Reference for the Cambridge Runtime and Libraries

**Path:** `docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md`  
**Audience and purpose:** Programmers and runtime developers; supported runtime/library behavior and ABI.  
**Source leads:** Runtime v1/v2, stack-check and BCPLIO contracts, LIBHDR, MR10 library/GLOBALS, CO.5/CO.6 and current code.

1. Scope, terminology and compiler-specific interfaces.
2. Core Runtime — startup, exports, globals, registers, calls and stack.
3. Core Runtime — storage, allocation, vectors, byte access and termination.
4. Core Runtime — character streams, selection, translation, errors and cleanup.
5. Base Library (BLIB) — supported formatting, strings, conversions and other routines.
6. Coroutine Support Library — creation, activation, transfer, deletion, limits and common behavior.
7. MR10 interpreted runtime and libraries — separate ABI, slots and services.
8. Optional libraries and extensions — linkage, deferred facilities and user/site libraries.
9. Compatibility, diagnostics, restrictions and verification scope.

**Boundary:** Reconcile candidate versus production contracts, G!150 conflict and bounded CO.6 scope. Registry owns allocations; extension API belongs in its own reference.

### Tutorial on System Extensions

**Path:** `docs/product/Tutorial-on-System-Extensions.md`  
**Audience and purpose:** BCPL programmers with native application experience; learn through BCPLDEMO.  
**Source leads:** BCPLDEMO header, permanent-support decision, R.5 evidence and accepted examples.

1. Prepare an eligible development environment.
2. Discover BCPLDEMO and its header.
3. Write a client and perform QUERY.
4. Select, compile, assemble, link and run.
5. Inspect returned values and expected output.
6. Modify and rerun; learn from a controlled failure.
7. Next steps — time, record I/O and shared references.

**Boundary:** Use a verified BCPLDEMO exercise; no unsupported RC4 native workflow.

### How to Use System Extensions

**Path:** `docs/product/How-to-Use-System-Extensions.md`  
**Audience and purpose:** BCPL programmers; select and use packages.  
**Source leads:** Extension READMEs, BCX selection/catalog, headers and accepted tests.

1. Choose packages and prerequisites.
2. Include declarations and query capabilities.
3. Prepare selection, assemble and link objects.
4. Use multiple extensions without collisions.
5. Supply DDs, record geometry and buffers for BCPLQSAM.
6. Use time and demo services.
7. Handle statuses, close resources and verify results.
8. Diagnose selection, registration, linkage and MVS errors.

**Boundary:** Procedures, not duplicate API tables. Distinguish source-mode and installed evidence.

### Explanation of System Extensions

**Path:** `docs/product/Explanation-of-System-Extensions.md`  
**Audience and purpose:** Programmers and developers; understand optional architecture.  
**Source leads:** Nomenclature, R.0 ABI decisions, archived Decision G/QUERY and R.1–R.5 closure.

1. Role of System Extensions.
2. Global dispatch and public headers.
3. BCEX descriptors and BCRG registration records.
4. BCPLREG startup, validation, ownership and finalization.
5. Known-package selection and IEWL linkage.
6. BCPLDEMO, BCPLTIME and BCPLQSAM as examples.
7. Portability, safety and lifecycle.
8. Deferred design and limitations.

**Boundary:** Explain actual logical and object relationships; no unsupported dynamic discovery.

### Reference for System Extensions

**Path:** `docs/product/Reference-for-System-Extensions.md`  
**Audience and purpose:** Programmers and extension developers; complete accepted APIs and common ABI.  
**Source leads:** R.0 ABI/Decision G/QUERY; package headers and closures; Global Number Registry.

1. Common conventions — globals, dispatcher, QUERY v1, vectors, errors and versions.
2. Common registration and selection — BCEX/BCRG v1, limits, diagnostics, collision checks and finalization.
3. BCPLDEMO — purpose, header, DEMOSVC, version, operations, parameters, results, linkage and limits.
4. BCPLTIME — purpose, header, TIMESVC, time representations, operations, statuses and linkage.
5. BCPLQSAM — purpose, header, QSAMSVC, logical records, QUERY/OPEN/READ/WRITE/CLOSE/INFO, vectors, buffers, limits, devices, lifecycle, errors and JCL.
6. Cross-package restrictions, compatibility and verification qualifications.
7. Related registry, declarations and historical evidence.

**Boundary:** One chapter per extension; common package subsection pattern. Preserve Q.5 exclusions and stage ceiling after reconciliation. BCPLDEC deferred; R2TESTB fixture only.

### How to Install BCPL from Tape

**Path:** `docs/product/How-to-Install-BCPL-from-Tape.md`  
**Audience and purpose:** MVS operators; install a specific distribution.  
**Source leads:** RC4 companion, frozen manifest, installer, TA.3/TA.7 evidence.

1. Identify release, media, checksum and target.
2. Review manifest, HLQ, storage and profile prerequisites.
3. Mount media and restore bootstrap/installer.
4. Select and install applicable MR10, NATIVE or COMBINED profile.
5. Verify inventory, directory/DCB and members.
6. Run supported functional verification.
7. Recover from incomplete installation without overwriting existing installations.

**Boundary:** Release-specific companion governs exact media. RC4 native payload is installation/inventory accepted only; no independent IPL/alternate HLQ acceptance.

### How to Operate the BCPL Programming System

**Path:** `docs/product/How-to-Operate-the-BCPL-Programming-System.md`  
**Audience and purpose:** MVS operators; routine operation of an installed product.  
**Source leads:** RC4 companion, installed suite JCL and verified MVS/JES procedures.

1. Identify installed release, profile and available environments.
2. Confirm libraries, procedures, datasets and DDs.
3. Submit and monitor installed jobs.
4. Review output, spool routing, codes and diagnostics.
5. Run health checks and supported smoke tests.
6. Manage routine input/output datasets and resource usage.
7. Respond to failures, preserve evidence and escalate.
8. Distinguish routine operation from installation, reconstruction and promotion.

**Boundary:** Product operation is not TK5 host/project management. Operating title and outline proposed for review.

## Project and shared background manuals (DR.3)

### How to Reconstruct BCPL from Source

**Path:** `docs/project/How-to-Reconstruct-BCPL-from-Source.md`  
**Audience and purpose:** Maintainers; safe clean-room rebuild.  
**Source leads:** Automated/manual rebuild guides, driver/contract, config and accepted evidence.

1. Establish Git revision, dedicated MVS and prerequisites.
2. Review destructive scope; preserve evidence and authorize cleanup.
3. Perform interactive reconstruction.
4. Perform unattended/batch population when explicitly authorized.
5. Understand stages — ICINT19, bootstrap/CAMBCOMP, Core Runtime, BLIB, coroutines and extensions.
6. Verify installation and run supported regressions.
7. Perform manual stage-by-stage reconstruction with stop/review gates.
8. Diagnose failures and recover through supported procedures.

**Boundary:** Retain a distinct manual rebuild chapter and safety gates. No native-running compiler claim.

### How to Develop and Test BCPL for MVS

**Path:** `docs/project/How-to-Develop-and-Test-BCPL-for-MVS.md`  
**Audience and purpose:** Developers and maintainers; controlled changes and target verification.  
**Source leads:** Git/MVS and operator policies, runtime workflows, tests README and actual tools.

1. Working authority, target isolation and approvals.
2. Development — investigate, define contract and edit real BCPL, JCL or assembler.
3. Development — build candidate, inspect listings/maps without premature promotion.
4. Testing — design independent oracles; focused tests and source/installed modes.
5. Testing — native 00–189, MR10 baseline/supported/development and paired coroutine suites.
6. Testing — offline versus MVS results, JES, printer/punch attribution and failure evidence.
7. Review and promote — controlled installation, evidence and rollback.
8. Full regression, record evidence, maintain documentation and obtain acceptance.

**Boundary:** One how-to with distinct development/testing chapters. Preserve test identities, case 083 skip and no-retry guards.

### Reference for Project Tools

**Path:** `docs/project/Reference-for-Project-Tools.md`  
**Audience and purpose:** Developers, maintainers and project operators; tool contracts.  
**Source leads:** Actual executable source/help and tests, tool READMEs and config/dspal.yaml.

1. Shared conventions — repository root, prerequisites and configuration.
2. Hercules/TK5 and MVS console/job tools.
3. DSPAL — aliases, mappings, population, submission, readback and deletion.
4. MR10 tools — interpreter, compiler and suites.
5. Bootstrap/native tools — prepare, compile, assemble and install.
6. Checks, runners and coordinators — selectors, modes, evidence and exit codes.
7. Reconstruction — scope, options, safety and workarea.
8. Distribution — manifest/registry, orchestration and evidence review.
9. Command and failure reference — inputs, outputs, changes and recovery limits.

**Boundary:** Verify actual interfaces before claiming options. How-tos own recipes; config retains machine-readable authority.

### How to Create a Release Candidate

**Path:** `docs/project/How-to-Create-a-Release-Candidate.md`  
**Audience and purpose:** Maintainers; produce and privately verify a candidate.  
**Source leads:** Existing canonical tools/distribution how-to, create-release, manifest/registry and evidence.

1. Confirm scope, prerequisites and authorization.
2. Preview identity and VOLSER.
3. Reserve identity and freeze manifest/registry.
4. Prepare source, documentation and installation payloads.
5. Produce and verify on MVS — guarded staging, tape write and readback.
6. Install in fresh namespaces and verify supported functions.
7. Review private evidence, checksums and package consistency.
8. Record acceptance and separate publication authorization; stop/recovery rules.

**Boundary:** Keep existing canonical path until dependency review; no duplicate. New driver offline-tested only, not verified by BC0005.

### Explanation of the MVS Programming Environment

**Path:** `docs/project/Explanation-of-the-MVS-Programming-Environment.md`  
**Audience and purpose:** Programmers, operators and developers; coherent technical background.  
**Source leads:** Existing System/370, IBM data, MVS, IFOX, JCL, object/load and Hercules briefings; contemporary primary sources and observed MVS.

1. System/370 architecture — registers, addressing, instructions and PSW.
2. IBM data — words, bytes, EBCDIC, binary/decimal and records.
3. MVS architecture — address spaces, tasks, program state and storage.
4. System interfaces — supervisor services and macros.
5. Datasets and access methods — sequential/PDS, DCB and QSAM.
6. JCL and JES — jobs, steps, DDs, allocation, spool and codes.
7. IFOX assembler — source cards, directives, macros, CSECTs and bases.
8. Object modules and IEWL — symbols, relocation, maps and libraries.
9. Program execution — loading, linkage, save areas and return.
10. Debugging — listings, maps, dumps, abends and evidence.
11. Hercules and TK5 — emulated machine, devices and host/guest boundaries.
12. Putting it together — BCPL, assembly, linkage, execution and I/O.

**Boundary:** One coherent explanation, no arbitrary size target. Consolidate overlap and verify technical accuracy against primary sources.

## Owner-approved migration and reconciliation approach

The owner explicitly agreed to the approach explained in the 25 November conversation: migrate information into coherent manuals while preserving existing authorities and records, reconcile contract provisions with implementation and actual evidence, and validate and explicitly approve transfer incrementally. Migration changes the organization of information; reconciliation establishes meaning and accepted scope. Neither authorizes software behavior changes.

### Proposed practical implementation

1. Record an economical migration ledger, preferably a Markdown table per manual or contract family: old path/revision and provision, new chapter/section, authority, source/evidence, unresolved qualification, dependency check, disposition and approval. Avoid elaborate infrastructure.
2. Draft substantive manuals in their approved locations. Keep original paths and operative authorities during drafting. Trace all substantive clauses, examples and safety warnings. Consolidate repetition. Do not link nonexistent manuals from live navigation.
3. Reconcile contract provisions against accepted scope, actual source, headers, JCL, test oracles and MVS evidence. Classify unchanged, clarified without semantic change, superseded by later accepted provision, conflicting or unverified. Investigate contradictions; do not silently broaden behavior or alter code.
4. Validate completeness, compatibility, constraints, negative/error behavior and links. Use existing accepted evidence where sufficient; seek focused real BCPL/IFOX/IEWL/JES/MVS verification when material uncertainty remains, under appropriate authorization. Do not rerun merely to repeat accepted proof. Offline tests are not target evidence.
5. Transfer authority only after explicit owner acceptance of the reconciled contract and verification limits. Record old authority, replacement chapter, effective Git revision and qualifications. Old authority remains operative until then; new draft is non-normative. Perform coherent transfers in DR.2/DR.3 when ready or defer to DR.5 if needed. Preserve original records unchanged, including immutable revision links when useful. Registries, configuration, manifests, oracles, legal records and release-specific authority remain separate.
6. Retire redundant active prose only after coverage, dependency checks and owner-approved disposition. Prefer concise pointers at safe old paths where needed. Do not replace historical acceptance records or required fixture READMEs with pointers. Preserve frozen RC4, BT0003, manifests/registry, candidate sources, historical materials, receipts, no-retry markers and all unverified paths.
7. Verify integrated navigation, reconstruction, regression and release capabilities in DR.5. Establish ongoing maintenance in DR.6. Owner approval remains required for march closure.

### Example: BCPLQSAM

| Existing authority/evidence | Destination or continuing role |
| --- | --- |
| [Public Interface Specification](../qsam/bcplqsam-public-interface.md) | Reference for System Extensions, BCPLQSAM chapter: complete normative API, operations, vectors, statuses, limits, failures and resource behavior |
| [R.0 owner ABI](../runtime-extensions/runtime-extensions-r0-owner-abi-decisions.md), [Decision G](../../archive/runtime-extensions/runtime-extensions-r0-decision-g-contract-20261021.md), [shared QUERY](../../archive/runtime-extensions/runtime-extensions-r0-query-abi-decision-20261021.md) | Common conventions and registration/selection chapters; separate validated authority transfer |
| [Public header](../../../system-extensions/bcplqsam/bcplqsam.h), [implementation](../../../system-extensions/bcplqsam/bcplqsam.asm) | Declarations and implementation evidence |
| [Global Number Registry](../../architecture/global-number-registry.md) | Retains QSAMSVC:200 allocation authority |
| [Q.5 closure](../qsam/qsam-q5-closure-20261101.md) | Preserved acceptance evidence: full panel 175 PASS/1 FAIL/1 expected SKIP then focused 175 PASS; Q5QINST/Q5QVFY receipts absent in that closure; genuine exceptional MVS CLOSE not verified by injected R15 override following successful CLOSE |

This is an illustrative destination map, not a completed reconciliation. Map all normative provisions, including QUERY, OPEN, READ, WRITE, CLOSE, INFO and the 1024 total-byte private stage ceiling, against later accepted scope before transfer. Do not retroactively credit subsequent installation evidence to Q.5.

## Remaining DR.1 gate (historical)

**Owner disposition:** The outlines were approved on 25 November 2026. See [formal DR.1 closure and DR.2 transition](dr1-formal-closure-and-dr2-transition-20261125.md).

Review these outlines for coverage, overlap and appropriate boundaries; approve chapter plan and practical migration arrangements before formal closure. Actual clause mapping and validation are subsequent implementation work. Rendering and record-format design remains DR.4. No implementation, relocation, deletion, contract transfer, release or MVS operation has been performed. DR.0's qualified dependency audit remains a constraint; no complete dependency graph or individual contract validation is claimed.
