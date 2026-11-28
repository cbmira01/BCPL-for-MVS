# Cambridge Compiler Bootstrap Restoration

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 28 November 2026 EST  
**Review baseline:** `3db2daab9d2b016e2185e2340e05212bb675ec85`  
**Status:** OPEN — established 28 November 2026 by owner approval; CBR.0 OPEN; CBR.1–CBR.9 NOT STARTED.

## 1. Objective

Restore the historical interpreter-hosted Cambridge Compiler and its supporting execution environment so that construction of the native-running Cambridge Compiler is a straightforward final step rather than a separate major development effort. Preserve the interpreter-hosted compiler as a development and verification environment. The two Cambridge execution environments should use common historical compiler source wherever practical. The MR10 Kit Compiler remains a separate, preserved bootstrap system.

## 2. Governing decisions and authorities

The [approved design discussion](../../architecture/cambridge-compiler-bootstrap-restoration-design-discussion-20261128.md) records decisions 1–17, including historical authorities, verification philosophy and exclusions. Its revised sequencing supersedes only the relevant portion of the [post-Documentation Refactoring direction](../../architecture/post-documentation-refactoring-development-direction-20261128.md).

Consult the [nomenclature](../../architecture/runtime-and-library-nomenclature.md), [Global Number Registry](../../architecture/global-number-registry.md), [runtime interface conventions](../../architecture/runtime-interface-conventions-and-contracts.md), [runtime contract](../../architecture/runtime-contract-v1.md), [CG370 notes](../../architecture/cg370-architecture-notes.md), [stack-check checkpoint](../../architecture/stack-check-contract.md), [compiler reference](../../../docs/product/Reference-for-BCPL-Compilers.md), [runtime and libraries reference](../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md), [language reference](../../../docs/product/Reference-for-the-BCPL-Language.md), and [System Extensions reference](../../../docs/product/Reference-for-System-Extensions.md) within their individual authority and evidence scopes. The canonical [reconstruction procedure](../../../docs/Rebuild-BCPL-for-MVS-from-source.md), [test suite contracts](../../../tests/README.md), and [DR.6 closure](../documentation-refactoring/dr6-formal-qualified-closure-and-milestone-completion-20261127.md) remain effective. Historical source, documented historical intent, reconstructed behavior and actual MVS evidence are distinct authorities. Preserve the historical archive and record gaps and inferences explicitly.

## 3. Approved march roadmap

The owner approved the proposed CBR.0–CBR.9 identifiers and sequencing on 28 November 2026 by directing: “Commit the documents, and open CBR0.” Every march requires owner acceptance before closure and before opening the next march. Prerequisites refer to accepted results, not merely the existence of implementation code. Investigation may identify a dependency requiring an owner-approved resequencing.

| March | Title | Prerequisites | Decisions | Status |
| --- | --- | --- | --- | --- |
| CBR.0 | Architecture and Dependency Reconciliation | Milestone establishment | 1–17 | OPEN |
| CBR.1 | ICINT20 and Word Representation | CBR.0 | 4, 8, 9, 11, 15 | NOT STARTED |
| CBR.2 | Interpreted Library and Host Service Restoration | CBR.1 | 4, 5, 11, 13, 14, 15 | NOT STARTED |
| CBR.3 | Historical Record I/O | CBR.2 | 10, 11, 15 | NOT STARTED |
| CBR.4 | Native Runtime and Compiler Library Integration | CBR.3 | 1, 2, 4, 5, 13, 14 | NOT STARTED |
| CBR.5 | CG370 Sections, Dependencies and Object Generation | CBR.3–4 | 3, 10, 11, 16 | NOT STARTED |
| CBR.6 | Floating-Point Restoration | CBR.5 | 6, 7, 8 | NOT STARTED |
| CBR.7 | Checking and Counting | CBR.4–6 | 4, 12 | NOT STARTED |
| CBR.8 | Source Restoration and Native Compiler Construction | CBR.1–7 | 2, 7, 8, 14, 16, 17 | NOT STARTED |
| CBR.9 | Reconstruction, Regression and Acceptance | CBR.8 | 17 and all preceding decisions | NOT STARTED |

### CBR.0 — Architecture and Dependency Reconciliation

Inventory the effective compiler, interpreter, BLIB/BLIBI/ICLIB dependencies, globals and X-class instructions. Inventory every `make-demoted.py` transformation and identify the relevant historical sources and acceptance test. Investigate the current bootstrap build graph, textual INTCODE packing, historical parameters, compiler library/ABORT behavior, workspace, GET, record I/O, DATE, section dependencies, floating point and instrumentation. Establish an INTCODE X-class Instruction Registry before allocating instructions. Reconcile the Global Number Registry; propose a collision-checked DEBUGINT replacement and obtain approval before assignment. Identify candidate build/install isolation and independent oracles.

**Acceptance:** Approved dependency inventory, registry foundation, verification plan, and candidate isolation approach. No implementation architecture for unresolved choices, numeric allocation or MVS operation is silently authorized. Detailed design decisions may remain gated in their owning marches.

### CBR.1 — ICINT20 and Word Representation

Apply the [owner-approved ICINT20 bootstrap architecture](cbr0-icint20-bootstrap-architecture-20261128.md): fixed assembly-time PROGVEC capacity, dynamically obtained storage, targeted critical-operation bounds checking, and independent bootstrap verification. No runtime PROGVEC sizing option is required.

Develop a separately built ICINT20 with 32-bit interpreted words, four-byte packed strings/bytes, ASCII internal characters, appropriate program and stack storage and applicable textual INTCODE compatibility. Inspect existing deck encodings, GETBYTE/PUTBYTE, pack order, character boundaries and program loading. Do not assume two-byte-packed decks execute unchanged. Establish the minimum compatible ICLIB/BLIBI and test fixtures needed for initial bring-up; investigate how to generate four-byte-compatible library and application decks using the preserved MR10 bootstrap, with any necessary target-dependent changes separately justified. Avoid circular build dependencies. Preserve original ICINT19, MR10 BLIB/BLIBI and executable phases.

**Acceptance:** ICINT20 independently assembles, loads and executes controlled INTCODE programs on MVS; independent word, byte, string, arithmetic, storage-boundary and textual loading tests pass. Measured stack/program capacity and format limits are documented; ICINT19 remains intact.

### CBR.2 — Interpreted Library and Host Service Restoration

Adapt machine-dependent BCPL library source following historical MR10 BLIB/BLIBI/ICLIB division, regenerate ICINT20-compatible BLIBI, and extend hand-written ICLIB as needed. Bring up the existing Cambridge compiler under ICINT20 with only justified adaptations. Restore historical FINDPARM over EXEC PARM, distinguishing runtime initialization from compiler switches; preserve MR10 OPTIONS DD on its accepted path. Restore DATE, WRAPOUTPUT, UNRDCH, SKIPREC and FINDINPUT DDNAME(MEMBER), including ordinary DDNAME access and nested GET. Investigate historical DATE format; do not introduce a BCPLTIME dependency. Replace bootstrap host shims incrementally, retaining them until equivalent services pass tests. Preserve internal ASCII and localize text/target conversion.

**Acceptance:** Independently generated BLIBI/ICLIB work with ICINT20; restored services pass focused MVS tests (including missing members, replay, stream restoration and parameters), and a candidate interpreter-hosted Cambridge Compiler emits usable CODE that is assembled, linked and executed. Any remaining shim is explicitly recorded and owned for resolution before CBR.8 acceptance.

### CBR.3 — Historical Record I/O

Implement historical READREC:23 and WRITEREC:24 through hand-written ICLIB and approved X-class instructions. Use MVS QSAM knowledge and infrastructure as appropriate without making the BCPLQSAM public API the historical interface or requiring optional extension registration. Resolve historical lengths, EOF and errors from callers and evidence. Keep binary records untouched by text translation.

**Acceptance:** MVS tests demonstrate logical records, exact lengths, EOF, recoverable errors, arbitrary byte contents and independent dataset comparison, including FB80 object-deck-shaped records. X-class allocations are approved and recorded; ordinary character I/O remains correct.

### CBR.4 — Native Runtime and Compiler Library Integration

Relocate callable DEBUGINT from G!150 to its separately approved registry allocation, reserving FORMTREE:150. Apply the [owner-approved COMPBLIB architecture](cbr0-compblib-architecture-20261128.md): separate BLIB and COMPBLIB build variants from common source, with ordinary BLIB behavior preserved. Prefer a common Core Runtime with library selection at link-edit time, subject to detailed implementation design. Reconcile STANDARDABORT:112, first-phase F, global initialization and the runtime ABEND dispatch contract before implementation. Restore required native runtime services, including historical FINDPARM, DDNAME(MEMBER) and DATE as applicable; verify existing WRAPOUTPUT, UNRDCH and SKIPREC contracts rather than replacing working services gratuitously. Establish configurable stack allocation separately from first-phase compiler Pnnn free-stack reservation; measure safe limits. Preserve the accepted coroutine and BCEX/BCRG contracts.

**Acceptance:** Collision-free effective global ownership; targeted native MVS probes demonstrate compiler-library selection/error paths and ordinary BLIB preservation; parameter and stack contracts and native member input are evidenced. Compiler-dependent ABORT tests that require the complete compiler are also required at CBR.8; no native compiler execution is needed for milestone acceptance.

### CBR.5 — CG370 Sections, Dependencies and Object Generation

Restore historical SECTION and NEEDS in Cambridge source processing and CG370. Verify textual CODE via IFOX and direct binary SYSGO via IEWL, preserving generator L and N semantics. Inspect ESD, TXT, RLD and END records independently and verify binary transport. Test multiple sections, named control sections, external symbols, relocations, static linkage and unresolved-dependency diagnostics. Treat historical dependencies such as `$LOAD$` explicitly: defer dynamic load-and-go and overlays without silently stubbing reachable requirements. External source splitting remains acceptable for MR10 bootstrap generation.

**Acceptance:** Independently inspected textual and direct binary object outputs link and run representative native BCPL programs with matching expected results; section and external reference behavior and diagnostics are evidenced by IFOX/IEWL/JES. No byte-for-byte identity between independently produced assembler and CG370 decks is required where equivalent relocation/link behavior is demonstrated.

### CBR.6 — Floating-Point Restoration

Restore historical READFLOAT and floating literal generation. Determine and obtain approval for the least intrusive feasible implementation (prefer Cambridge source and interpreter/library support over extending MR10 or INTCODE unnecessarily). Distinguish host-side literal conversion from generated target arithmetic. Remove the fatal demotion stub when replacement is verified.

**Acceptance:** Actual MVS native execution of compiled BCPL programs proves floating literals, arithmetic, comparisons, conversions, storage and procedure interfaces against independent expected results, including appropriate representable boundary and error cases; both supported object-generation paths are covered. Historical sources and accepted MR10 baseline remain intact.

### CBR.7 — Checking and Counting

Complete generator options C, K, P and CK, including relevant entry paths and historical reporting. Distinguish generator P (counting instrumentation) from first-phase Pnnn (workspace). Correct incomplete native combined-instrumentation support before executing such output. Establish permanent regression cases for valid execution, actual counts, reporting and checked overflow with verified frame-size handling. Investigate CP where relevant to the generator's combination semantics; do not claim untested combinations. Preserve the current default until a separate approved change is supported by evidence.

**Acceptance:** MVS native probes prove C, K, P and CK with appropriate independently expected results and diagnostics; combined checking/counting enforces stack bounds and preserves procedure entry invariants. Historical `/CK` is established as a supported configuration at the verified scope; changing default is separately approved.

### CBR.8 — Source Restoration and Native Compiler Construction

Reconcile the complete transformation inventory. Remove unjustified demotions, retire `bootstrap-host.bcpl` only after verified replacement of every required service, document justified remaining MR10-only transformations, and preserve historical source. Build the restored interpreter-hosted Cambridge Compiler and use it to compile its own source components into native System/370 object modules. Construct compiler-specific libraries as approved; resolve actual global and static external dependencies and link the native compiler with IEWL. Verify both generation paths on compiler components at appropriate scope; at least one complete static construction path must yield the native compiler load module. No execution of that load module is authorized by this march.

**Acceptance:** Source provenance and demotion audit; verified interpreter-hosted compiler error behavior including F; complete native compiler object inventory, IEWL map and successful static linkage with intended entry and no unresolved required symbols. Native compiler execution and self-compilation are explicitly unestablished.

### CBR.9 — Reconstruction, Regression and Acceptance

Integrate accepted changes into canonical unattended reconstruction, using existing tools and approved promotion boundaries. Reconstruct ICINT20, its libraries, the restored compiler and the native compiler load module. Run the applicable full existing production regression and all permanent new tests, including independent MR10/ICINT19 preservation and relevant installed/source-selected modes. Reconcile evidence, documentation and outstanding qualifications. Retain previous results and failures as historical records.

**Acceptance:** Authorized clean-room reconstruction and full supported regression pass, no unexplained failure or blocked required case, existing case 083 expected SKIP preserved unless separately resolved, all new required cases pass, and documented scope plus owner acceptance. The pre-milestone baseline is 219 PASS / 0 FAIL / 1 expected SKIP / 0 BLOCKED at its recorded revision; the expanded suite is not constrained to 219 passes. No release production or native compiler execution/self-compilation is implied.

## 4. Global acceptance and deferred scope

All five required results in decision 17 must hold: (1) ICINT20 and associated libraries reconstruct; (2) restored interpreter-hosted Cambridge Compiler constructs; (3) it compiles its own source into native object modules; (4) those modules statically link into a native compiler load module; (5) supported functionality is preserved by full regression. Canonical unattended reconstruction and independent target evidence are mandatory. No general historical feature completeness claim follows.

Native compiler execution and self-compilation, dynamic loading and overlays, historical load-and-go, additional target architectures, general library/extension expansion, hosted MVS integration, substantial release-driver development, public release production, Decimal Arithmetic, and unrelated historical postmortem/runtime work are excluded. Preserve published RC4 artifacts and prior qualifications, BCEX/BCRG, existing System Extensions, and Coroutine Support Library.

## 5. Governance

Prefer real BCPL, System/370 assembler and JCL verified using MVS, IFOX, IEWL and JES. Maintain independently testable component boundaries and proportional documentation updates under DR.6. Test before committing when possible. Obtain owner approval for major architecture choices, allocations, commits/pushes, destructive operations, installation/promotion and release production. Do not repeat accepted verification without scope change or demonstrated defect. The roadmap is approved; only CBR.0 is open. Opening does not authorize subsequent implementation marches, allocation decisions, MVS jobs, destructive operations or promotion.

## 6. Establishment review

A separately named official project charter could not be located in accessible repository or project sources during this review. The repository README, existing approved milestone/architecture records, and owner handoff established the basis of this roadmap; they are not represented as the missing charter. The owner subsequently authorized opening CBR.0. Locate and reconcile the charter if available during CBR.0, and report any remaining authority limitation before march acceptance. Repository documentation was reviewed at the recorded HEAD, with focused excerpts of the long references; detailed source-level audits are CBR.0 deliverables, not completed by this establishment record.

## 7. CBR.0 formal opening — 28 November 2026 EST

**Owner direction:** “Commit the documents, and open CBR0.”

**Disposition:** Cambridge Compiler Bootstrap Restoration OPEN; CBR.0 — Architecture and Dependency Reconciliation OPEN. CBR.1–CBR.9 remain NOT STARTED.

Begin with read-only, source-grounded dependency reconciliation and the inventory of existing allocations, instructions and demotion transformations. Establish the X-class registry foundation before any new instruction allocation; no replacement DEBUGINT global or X38/X39 assignment is authorized. Bring unresolved architecture choices to the owner individually. Preserve all accepted baselines, qualifications and historical sources. No MVS submission, runtime or compiler implementation, destructive operation, installation, promotion, release production or native compiler execution is authorized by this opening.
