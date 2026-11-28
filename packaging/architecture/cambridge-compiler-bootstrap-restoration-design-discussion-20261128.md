# Cambridge Compiler Bootstrap Restoration — approved design discussion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 28 November 2026 EST  
**Review baseline:** `3db2daab9d2b016e2185e2340e05212bb675ec85`  
**Disposition:** Owner-approved architectural direction transcribed from the handoff; owner authorized commitment and opening of CBR.0 on 28 November 2026. The [governing milestone](../milestones/cambridge-compiler-bootstrap-restoration/milestone-cambridge-compiler-bootstrap-restoration.md) records the formal opening and march statuses.

## 1. Revised development direction

This record supplements [Post-Documentation Refactoring — development direction](post-documentation-refactoring-development-direction-20261128.md). Its native-running Cambridge Compiler sequencing is superseded: restore the interpreter-hosted Cambridge Compiler and supporting environment first, then compile and statically link the native compiler. Native execution and self-compilation are subsequent objectives. All unrelated dispositions and prior qualifications remain effective. The previously contemplated native-running compiler milestone was never established.

The governing objective is that construction of the native-running Cambridge Compiler should become a straightforward final step, rather than a separate major development effort.

The following sections preserve the approved architectural decisions and boundaries from the owner handoff. Decision numbers are not march identifiers.

## 2. Architectural philosophy

Maintain clear distinctions between:

- The MR10 Kit Compiler.
- The interpreter-hosted Cambridge Compiler.
- The future native-running Cambridge Compiler.

The two Cambridge Compiler execution environments should represent the same compiler, using common historical source wherever practical.

Preserve the historical source archive. Minimize unnecessary changes to MR10. Reduce source demotion and bootstrap-specific accommodations through restoration of appropriate runtime and library capabilities.

Prefer real BCPL, System/370 assembly and JCL implementation, supported by actual MVS verification.

Retain the interpreted Cambridge Compiler as a useful development and testing environment even after native compilation becomes available.

## 3. Approved design decisions

The following decision numbers identify discussion decisions, not march identifiers.

### Decision 1 — DEBUGINT relocation

Relocate DEBUGINT from G!150 to preserve the historical compiler allocation FORMTREE:150.

Retain DEBUGINT as a callable runtime service.

Investigate all dependencies and global allocations before selecting a replacement global number. Record the approved allocation permanently in the Global Number Registry.

No replacement number has been assigned.

### Decision 2 — Compiler-specific ABORT and COMPBLIB

Investigate the historical compiler-specific ABORT mechanism, COMPBLIB, STANDARDABORT:112 and the historical F compiler option.

Determine how compiler-specific error handling interacts with global initialization and runtime ABEND processing.

Investigate whether one library object with multiple entry points or separate library variants best satisfies the historical requirements.

Preserve ordinary BLIB behavior.

The owner approved separate BLIB and COMPBLIB build variants from common source on 28 November 2026. See the [CBR.0 COMPBLIB architecture](../milestones/cambridge-compiler-bootstrap-restoration/cbr0-compblib-architecture-20261128.md) for the controlling refinement, historical evidence and deferred implementation decisions. Prefer a common Core Runtime with link-edit-time library selection; detailed binding and ABEND dispatch design remain gated in CBR.4.

### Decision 3 — Both native object-generation pathways

Restore and verify both historical CG370 output pathways:

- Textual System/370 assembler through CODE and IFOX.
- Direct binary object decks through SYSGO and IEWL.

Preserve historical compiler option semantics, including L and N.

Verify ESD, TXT, RLD and END records, binary transport integrity, linkage and execution.

Other target code generators remain deferred.

### Decision 4 — Configurable stack and workspace

Investigate configurable runtime stack allocation in both interpreted and native execution environments.

Preserve the distinction between total runtime stack allocation and the Cambridge Compiler's P option, which reserves procedure stack space within the available workspace.

Determine appropriate capacity through actual compiler execution and MVS evidence.

### Decision 5 — Historical parameter handling

Restore historical EXEC PARM processing and FINDPARM.

Distinguish runtime initialization parameters from compiler options.

Replace the bootstrap-specific CAMBPARM accommodation where practical.

Preserve the MR10 Kit Compiler's historical OPTIONS DD interface.

### Decision 6 — Floating-point support

Restore historical Cambridge floating-point compilation functionality, including floating-point literals and the currently demoted READFLOAT routine.

Verify arithmetic, comparisons, conversions, storage, procedure interfaces and generated System/370 execution.

Investigate the least intrusive implementation strategy. Do not assume that full floating-point language support must be added to MR10 or INTCODE.

### Decision 7 — Reduction of source demotion

Inventory every transformation performed by `make-demoted.py`.

Remove transformations that are no longer necessary as historical functionality is restored.

Document and justify remaining transformations.

Do not alter preserved historical source material.

### Decision 8 — Minimize MR10 compiler changes

Avoid unnecessarily extending the MR10 Kit Compiler to incorporate later Cambridge language functionality.

Prefer, where technically appropriate:

1. Restoration within the Cambridge Compiler.
2. Interpreter and library capabilities.
3. Small, justified source adaptations.
4. MR10 compiler modifications only where demonstrated necessary.

Preserve the original MR10 implementation and executable baselines.

### Decision 9 — ICINT20

Develop ICINT20 as the successor development environment to ICINT19.

ICINT20 shall use:

- 32-bit interpreted words.
- Four-byte packing as its normal representation.
- Appropriate stack and program storage capacities.
- Historical textual INTCODE compatibility where applicable.

Review PROGVEC capacity, stack allocation, string representation, GETBYTE, PUTBYTE and associated machine-dependent library assumptions.

Preserve ICINT19 unchanged as an independently usable verified baseline.

Do not require a selectable two-byte packing mode in ICINT20.

### Decision 10 — Historical record I/O and allocation registries

Implement historical READREC and WRITEREC services through hand-written ICLIB interfaces and new implementation-dependent INTCODE X-class instructions.

Use existing MVS QSAM implementation knowledge and infrastructure where appropriate.

Preserve historical global allocations READREC:23 and WRITEREC:24.

Verify record lengths, EOF, errors, arbitrary binary data and independent dataset integrity.

Reconcile the Global Number Registry against effective compiler and library dependencies.

Establish an INTCODE X-class Instruction Registry before allocating additional instructions.

X38 and X39 were discussed as provisional candidates only. No assignments have been approved.

Do not conflate historical record I/O with the optional BCPLQSAM public API.

### Decision 11 — Internal ASCII representation

Retain ASCII as the internal character representation of ICINT20.

Localize character conversion at:

- MVS text I/O boundaries.
- Cambridge Compiler target-code generation boundaries.

Preserve raw binary record contents without character translation.

Distinguish interpreted host string representation from native target EBCDIC representation and logical control characters.

An EBCDIC execution mode for ICINT20 is not required.

### Decision 12 — Historical checking and counting options

Complete and verify historical compiler options:

- C — stack checking.
- K — procedure call counting.
- P — procedure call counting and counting instrumentation.
- CK — combined checking and counting.

Investigate historical reporting mechanisms and all associated entry paths.

Correct incomplete Core Runtime support for combined instrumentation.

Establish permanent native MVS regression coverage.

The historical `/CK` default should become a supported configuration only after verification. Do not prematurely change defaults.

### Decision 13 — Historical GET and PDS member support

Support historical `DDNAME(MEMBER)` input references through FINDINPUT in ICINT20 and the Core Runtime.

Preserve ordinary DDNAME access.

Remove corresponding GET-name demotion transformations where practical.

Verify nested GET operations, missing members, stream restoration and historical name handling.

### Decision 14 — Elimination of bootstrap host shims

Replace the accommodations currently implemented in `bootstrap-host.bcpl` with verified runtime services:

- DATE
- WRAPOUTPUT
- FINDPARM
- UNRDCH
- SKIPREC

Retire the bootstrap host module only after all required services have verified replacements.

DATE should remain a small, historically compatible built-in runtime service, sufficient for compiler-generated object headers and ordinary application use.

Determine the historical DATE string format.

BCPLTIME shall retain its existing public interface and optional System Extension status for more intensive time processing.

Investigate implementation reuse where appropriate, but do not introduce a dependency of the Core Runtime upon BCPLTIME.

### Decision 15 — Historical BLIBI reconstruction

Follow Martin Richards's historical INTCODE kit implementation strategy rather than requiring wholesale convergence between MR10 and Cambridge BLIB.

- Preserve original MR10 BLIB and BLIBI.
- Adapt machine-dependent BLIB routines for ICINT20.
- Regenerate BLIBI from maintained BCPL source.
- Extend hand-written ICLIB interfaces where required.
- Reuse historical Cambridge BLIB routines where appropriate.
- Verify MR10 behavior and restored Cambridge functionality.

Maintain the historical division of responsibilities between BLIB, BLIBI, ICLIB and ICINT.

The principal historical reference is:

`richards-bcpltape/mr10/text/bstrbcpl`

Also consult:

`richards-bcpltape/mr10/text/intcode`

### Decision 16 — SECTION and NEEDS

Restore and verify historical SECTION and NEEDS processing.

SECTION identifies a named compilation section, corresponding to an assembler CSECT or an object-deck section definition.

NEEDS declares an external symbol dependency, corresponding to assembler EXTRN or an object-deck external reference.

Verify:

- Multiple sections within a single source member.
- Named control sections.
- External symbol declarations.
- Associated relocation records.
- Textual and direct binary generation.
- Static linkage through IEWL.
- Appropriate unresolved-dependency diagnostics.

External source splitting remains acceptable for MR10 bootstrapping.

Dynamic loading and overlays remain deferred.

### Decision 17 — Native compiler construction readiness

The milestone shall culminate in:

1. Successful reconstruction of ICINT20 and its associated libraries.
2. Successful construction of the restored interpreter-hosted Cambridge Compiler.
3. Successful compilation of the Cambridge Compiler's own source into native System/370 object modules.
4. Successful static linkage of those modules into a native compiler load module.
5. Preservation of existing supported functionality through full regression testing.

Execution and self-compilation of the native-running Cambridge Compiler are subsequent objectives, not acceptance requirements for this milestone.

## 4. Historical source authorities

Use the preserved sources under:

- `richards-bcpltape/bcplib/bcpl/`
- `richards-bcpltape/bcplib/asm/`
- `richards-bcpltape/bcplib/jcl/`
- `richards-bcpltape/sys3/bcpl/libhdr`
- `richards-bcpltape/sys1/userproc/`
- `richards-bcpltape/mr10/bcplkit/`
- `richards-bcpltape/mr10/text/`
- `richards-bcpltape/mr10/print/manual`

Consult `richards-bcpltape/INDEX` when establishing historical provenance and availability.

Distinguish historical documentation, historical source behavior, reconstructed implementation behavior and actual target-system evidence.

Do not infer missing historical implementation details without documenting the inference.

## 5. Verification philosophy

Preserve the current accepted reconstruction and regression baselines.

The most recent accepted full production regression established:

- 219 PASS
- 0 FAIL
- 1 expected SKIP
- 0 BLOCKED

The expected SKIP is the existing MR10 fixed-stack case 083.

Retain existing independent verification oracles and accepted evidence.

Develop permanent regression tests alongside implementation. Exercise actual MVS facilities, IFOX, IEWL, JES and BCPL compiler behavior.

Maintain independently testable boundaries between ICINT20, ICLIB, BLIBI, the Cambridge Compiler and native runtime components.

Ensure successful canonical unattended reconstruction of the resulting system.

Do not repeat previously accepted verification operations without changed scope or demonstrated defects.

## 6. Explicitly deferred work

The following remain outside the milestone unless separately approved by the owner:

- Native compiler execution and self-compilation.
- Dynamic module loading and overlays.
- Historical load-and-go functionality.
- Additional compiler target architectures.
- General expansion of Standard Libraries and System Extensions.
- Hosted MVS integration.
- Substantial new release-driver development.
- Public release production.
- Decimal Arithmetic.
- Unrelated historical postmortem and runtime feature reconstruction.

Preserve BCEX/BCRG contracts, accepted System Extensions, Coroutine Support Library, published RC4 artifacts and existing milestone qualifications.

## 7. CBR.0 refinement — ICINT20 storage architecture (28 November 2026 EST)

The owner approved fixed assembly-time PROGVEC capacity with targeted storage checks, rejecting runtime-configurable PROGVEC allocation. This refines decisions 4 and 9 for the interpreted environment; compiler workspace options and the native runtime stack allocation investigation remain distinct. See the [approved ICINT20 bootstrap architecture](../milestones/cambridge-compiler-bootstrap-restoration/cbr0-icint20-bootstrap-architecture-20261128.md) for the controlling detail and verification requirements. No implementation or march transition is authorized.
