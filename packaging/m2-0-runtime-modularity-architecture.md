# M2.0 — Runtime Modularity and Maintainability Architecture

**Status (14 October 2026):** Gates A-D accepted and closed; Gate E maintainability review OPEN; Gate F candidate acceptance pending. The original gate plan and historical decisions below remain the governing charter.  
**Date:** 13 October 2026  
**Predecessors:** M1.8 reproducible five-member runtime builds (closed); M1.9 runtime contract and observability audit (closed).  
**Reference contract:** [Runtime Contract Specification v1.0](runtime-contract-v1.md).

## Decision and rationale

**BCPLMAIN should become the relatively small bootstrap and coordinator for independently assembled runtime services, rather than continue accumulating every service implementation.** Runtime modularity has two independent motivations:

1. **System/370 addressability and build isolation.** RX-format 12-bit displacements limit a base-register window to 4,096 bytes. As a large assembler CSECT expands, its base-register strategy, literal pools, local data and control flow become increasingly difficult to maintain without disturbing unrelated functionality. Separate **CSECTs**, with independent assembly and controlled entry points, are a principled boundary. Merely splitting one monolithic CSECT across source files does **not** solve the addressability problem.
2. **Readability, maintainability and historical intelligibility.** Future readers should be able to find a significant subsystem in one coherent source file, understand its responsibility and calling conventions without traversing thousands of unrelated assembler statements, and distinguish historical evidence from new MVS-specific engineering. Modularity is not just a technique for getting the assembler to accept growing code.

The useful analogy is Java's frequent class/file correspondence, **without** implying object orientation or automatic encapsulation: a major assembler service subsystem is usually one principal CSECT in a correspondingly named source file, assembled to one relocatable object module, and link-edited alongside the application.

## Architectural rule

> **One service responsibility, one named assembler source file, one principal CSECT, one independently reproducible object-library member.** A CSECT may export multiple related ENTRY points. Intermodule dependencies must be explicit through EXTRN and documented native/BCPL linkage contracts. Exceptions require a written reason.

This is a **cohesion** rule, not a demand for one CSECT per procedure. Avoid gratuitous fragmentation: tightly coupled functions sharing private state should remain together. A file may contain required assembler support declarations, DSECTs or carefully justified ancillary sections; the principal runtime implementation CSECT still owns the module identity.

A CSECT is not a Java class: it supplies neither protected encapsulation nor instances, and it does not automatically preserve register contents. API discipline, symbol exposure, private data ownership and reentrancy must be enforced by design.

## Division of responsibility

| Module | Intended ownership | Current state at M1.9 |
| --- | --- | --- |
| `bcplmain.asm` / BCPLMAIN | MVS entry linkage, initial runtime storage and global vector, module registration, runtime-service initialization, START dispatch, coordinated shutdown and task return | Exists but also contains substantial I/O, stack checking and local APTOVEC code |
| `bcplmem.asm` / BCPLMEM | GETVEC/FREEVEC, allocation descriptors, counters, binding and reclamation | Independently built; DEVOBJ active |
| `bcplbyte.asm` / BCPLBYTE | Machine-dependent word/byte access, GETBYTE and PUTBYTE | Independently built; DEVOBJ active |
| `bcplapt.asm` / BCPLAPT | Temporary-vector construction, nested BCPL call and its limit checks | Independently built and linked, but **canonical G40 still points to BCPLMAIN's local APTOVEC**; APLIMIT is not initialized in the canonical wiring |
| `bcplio.asm` / BCPLIO | **Proposed**, not yet created: stream selection, QSAM DCBs and buffers, input record conversion, WRCH/RDCH/UNRDCH, ENDREAD/ENDWRITE and related output services | Currently implemented within BCPLMAIN; possible future extraction |
| `bcplstack.asm` / BCPLSTACK | **Proposed**, not yet created: generated frame checks, stack-limit handling and potentially overflow reporting | Currently implemented within BCPLMAIN; extraction requires system-vector and exit coordination |
| `BLIB` | Higher-level historical BCPL library routines, including WRITEF and selected diagnostics | Special case: BCPL source compiled to native relocatable object, **not** hand-coded assembler |

Names and proposed extractions are architectural candidates, **not** a frozen M2.0 implementation backlog. Inspect size, state coupling and link boundaries before deciding whether to extract BCPLIO before BCPLSTACK.

## Interfaces and assembly/link-edit boundaries

- A runtime component is independently assembled; its assembler source establishes its own `CSECT`, `USING` addressability, register usage, literal pools, private state, `ENTRY` exports and `EXTRN` imports. Separating CSECTs reduces addressability coupling but does not eliminate the need for deliberate per-module base-register coverage.
- The MVS linkage editor composes the separately assembled objects into a single application load module. A service update should not require reassembling unrelated modules **when their published ABIs and dependencies are stable**.
- **BCPL-facing services** are installed at defined global-vector entries or system-vector slots. **Native-private interfaces** exist for configuration, initialization, statistics and cleanup. Do not mistake an assembler `ENTRY` for a BCPL callable procedure.
- BCPLMAIN should coordinate **installation of global addresses and service initialization**, rather than let services reach indiscriminately into each other's private storage or global-vector layout. Define explicit initialization contracts for state such as APLIMIT, stack boundaries, DCBs and allocator-list publication.
- Preserve established CG370/BCPL conventions: R5 current frame, R6 return, R7–R9 arguments/results, R4 restoration expectations, R11 system-vector base, and any additional generated-code register requirements. An independent CSECT **must not** appropriate BCPL registers for its own base address without an explicit saving/restoring discipline. Private native interfaces may use different register conventions only when fully specified.
- Assign one module ownership of each mutable state item and its lifecycle. Define startup order, error unwinding, normal termination, and abnormal termination across independent modules.
- Keep public BCPL globals, calling semantics and regression-observed behavior **stable across internal extraction**. A change in implementation ownership should not silently change the programmer-facing contract.

## Source readability and provenance requirements

Every independently owned assembler service source should begin with a concise module-level contract documenting:

1. Module purpose, services and deliberately excluded responsibilities.
2. Principal CSECT, exported ENTRY symbols and required EXTRN symbols.
3. BCPL global-vector/system-vector interface, if any; distinguish data from callable entries.
4. Register and argument conventions, return/result/condition behavior, and registers clobbered or preserved.
5. Addressability strategy, private/static state, reentrancy and storage ownership.
6. Initialization prerequisites, shutdown responsibilities and error paths.
7. Relevant regression IDs, evidence status, related contract documents.
8. **Provenance:** historically recovered behavior, inferred conventions, deliberate MVS adaptations, provisional assumptions and known missing functionality.

Prefer meaningful assembler comments next to non-obvious logic and short explanatory module headers. Place long historical analysis and architectural choices in linked Markdown documents. Do not require a reader to open a separate manual merely to discover how to call a module's public entry points.

Future-user comprehensibility is an **acceptance criterion**, not an incidental benefit: a competent System/370 assembler programmer should be able to inspect and reason about a subsystem independently, then follow explicit interfaces to understand the integrated runtime.

## Proposed sequencing and milestone discipline

**Gate A — Architecture and baseline.** Inventory BCPLMAIN's internal facilities, actual source sizes, external state dependencies, register/base usage and startup/exit couplings. Confirm this decision's module convention and identify only the first limited set of changes. Preserve M1.9 contract v1.0 as baseline.

**Gate B — Activate BCPLAPT.** Using the existing source-mode externalization experiment as evidence, design a canonical explicit EXTRN service publication and APLIMIT initialization. Remove or retire duplicate internal APTOVEC only after the independent path is verified. Include focused 091–093 tests.

**Gate C — Validate existing BCPLMEM and BCPLBYTE modular boundaries.** Verify module independence, service ownership, calling conventions and linked PDS behavior; do not rearrange proven code without need.

**Gate D — Select and extract one substantial subsystem.** Evaluate BCPLIO versus BCPLSTACK using actual addressing pressure, state coupling and testability. Prefer an incremental extraction with explicit initialization/configuration interface rather than another large BCPLMAIN edit. Migrate focused tests and preserve BCPL visible behavior.

**Gate E — Linkage and maintainability review.** Check source headers and provenance, symbol boundaries, base-register discipline, independent object build artifacts and developer navigation. Verify bootstrap/coordination remains intelligible.

**Gate F — Candidate acceptance.** Independently assemble changed modules into DEVOBJ, run focused regressions and the complete native regression panel, review deltas against M1.9 and document accepted results and remaining discrepancies. No production OBJ promotion without explicit authorization.

This is a **proposed** gate plan, not acceptance of M2.0 nor authorization to implement features. Decisions concerning public MEMSTAT exposure, stack-overflow RC semantics, abnormal cleanup, automatic historical ABORT/BACKTRACE/MAPSTORE or full I/O functionality should be explicitly scoped and authorized; avoid bundling every M1.9 deferred issue into the first modularity march.

## Operational controls

- **Git is the authoritative source of implementation and architecture**; MVS is an assembly/link/execution target.
- DEVOBJ is the candidate library; production `HERC02.BCPL.OBJ` remains stable and must not be modified without explicit permission.
- Use repository `tools/checks/` for assistant-owned, reproducible verification aids where beneficial.
- Establish focused regression evidence before the full regression, and distinguish source-only checks from actual installed-object exercise.
- Maintain M1.8's successful DEVOBJ regression baseline and M1.9's bounded contract. Do not claim that independent BCPLAPT is currently dispatched merely because it is in the link-edit.

## Design outcome

The intended long-term result is **a small BCPLMAIN that bootstraps and connects a collection of coherent, separately understandable runtime CSECTs**. The reason is as much the longevity and interpretability of this historical reconstruction as the addressing constraints of System/370.

## Observability policy — programmer-centric, historical and minimal

**Decision (13 October 2026):** The reconstruction's observability is primarily **for the BCPL programmer and the people reconstructing the compiler**, not a new MVS operator monitoring subsystem. The project targets an obsolete language on an obsolete operating system; its aim is a coherent, working historical reconstruction and a clear foundation for future Cambridge work by others, **not** a production-grade diagnostics platform.

A diagnostic facility belongs in the immediate project only when it offers:

1. **Historical continuity:** favor the conventions already present in Cambridge BCPL/BLIB over newly invented frameworks.
2. **Concrete reconstruction value:** it should help locate an actual compiler, code-generator, storage, linkage or runtime defect, or verify a documented contract.
3. **Low complexity:** use narrow routines, direct output and focused test probes; avoid large permanent infrastructures.
4. **Teaching value:** implementation and usage should be legible as an example future contributors can understand, copy, improve or replace.

Small nonhistorical aids are allowed when useful, but **must be labeled as reconstruction tooling or provisional extensions**, never presented as recovered Cambridge behavior. Instrumentation for developers does not automatically require a public BCPL global, permanent stable ABI or operator interface.

### Immediate disposition of existing facilities

| Facility | Current direction |
| --- | --- |
| STACKHWM | Retain historical G56 interface; useful for understanding stack consumption. Do not promise unverified exactness. |
| MAPSTORE | Investigate or exercise narrowly if it helps diagnose compiler reconstruction; no mandate to implement every historical mapping behavior now. |
| BACKTRACE | Defer native LEVEL/frame-walk integration until a concrete need justifies it. |
| ABORT | Preserve historical BLIB source and existing behavior; do not undertake comprehensive MVS recovery/postmortem machinery as part of modularization. |
| MEMSTAT | Keep assembler-private by default; use focused allocator experiments if needed. No automatic new BCPL global allocation. |
| DEBUGINT | Keep as a clearly provisional, simple bootstrap diagnostic; no claim of historical public API. |
| Stack overflow diagnostic | Preserve a straightforward message; more elaborate operator-oriented reporting is deferred. |

### Scope boundary

**Not goals of M2.0:** generalized monitoring, telemetry, logging levels, event frameworks, extensive operator dashboards/reports, comprehensive automatic postmortem processing, or diagnostics designed for speculative future consumers. In particular, do **not** turn M1.9's observability gap register into an implicit to-do list requiring every gap to be implemented.

The normal priority is to **reconstruct the compiler and keep the runtime small, understandable and testable**. Favor targeted checks under `tools/checks/` over permanent mechanisms where appropriate. A programmer-visible diagnostic is worthwhile when historical, immediately helpful and modest; otherwise document and defer it to future Cambridge versions or work led by other contributors.

If an MVS completion code or failure message needs adjustment for a specific, demonstrated reconstruction problem, evaluate that as a tightly scoped engineering change—not as authorization to design an operator-centric observability layer.

**Architecture consequence:** Modularization should retain the existing useful diagnostics and leave comprehensible service boundaries where future contributors may extend them. It must not introduce abstraction or instrumentation purely to anticipate later diagnostics.

**Acceptance consequence:** M2.0 reviews simplicity, programmer usefulness and historical clarity; it does **not** demand completion of historical BACKTRACE/ABORT/MAPSTORE or publication of MEMSTAT.
