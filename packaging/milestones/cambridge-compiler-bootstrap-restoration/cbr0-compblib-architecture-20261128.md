# CBR.0 — COMPBLIB architecture

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Cambridge Compiler Bootstrap Restoration  
**March:** CBR.0 — Architecture and Dependency Reconciliation  
**Date:** 28 November 2026 EST  
**Review baseline:** `8fc0cc0c52e62a00d3850ec9e0fafb32d8eaf198`  
**Status:** Owner-approved architectural decision; implementation remains gated.

## 1. Authority and scope

This record refines decision 2 of the [approved design discussion](../../architecture/cambridge-compiler-bootstrap-restoration-design-discussion-20261128.md) and the [governing milestone](milestone-cambridge-compiler-bootstrap-restoration.md). The owner approved separate BLIB and COMPBLIB build variants from common source and authorized documentation commitment. Read with the [Global Number Registry](../../architecture/global-number-registry.md), [nomenclature](../../architecture/runtime-and-library-nomenclature.md) and [runtime interface conventions](../../architecture/runtime-interface-conventions-and-contracts.md).

## 2. Historical evidence

- [LIBHDR](../../../richards-bcpltape/sys3/bcpl/libhdr) declares ABORT:3.
- [MAKEOBJ](../../../richards-bcpltape/bcplib/jcl/makeobj), lines 19–24 and 44–54, builds COMPBLIB from ordinary BLIB source with an additional LIBHDR declaration, `GLOBAL $( ABORT : 112 $)`.
- [MAKELIB](../../../richards-bcpltape/bcplib/jcl/makelib), lines 18–21 and 60–63, links COMPBLIB into the compiler root rather than ordinary BLIB.
- The [compiler master](../../../richards-bcpltape/bcplib/bcpl/bcpl), lines 7–13, 51–91, 110 and 152, declares STANDARDABORT:112, defines its own ABORT at G!3, expects it to be installed during global initialization, and assigns ABORT := STANDARDABORT for first-phase F. Compiler ABORT terminates through STOP(16).
- Historical [BLIB](../../../richards-bcpltape/bcplib/bcpl/blib), lines 118–174, implements ABORT(CODE, ADDR, OLDSTACK, DATA), including diagnostic/postmortem services, and terminates through STOP(100).
- The historical [tape index](../../../richards-bcpltape/INDEX) records the original BCPLMAIN assembler source and COMPBLIB object module as missing. Exact historical machine-code dispatch and initialization details are therefore not established by these sources.

## 3. Reconstructed behavior and dependency

Current [BCPLMAIN](../../../bootstrap-toolchain/asm/bcplmain.asm) imports application globals at GINST before importing BLIB at BLIMP. BLIMP writes the exported address into the global vector without rejecting an existing application owner. Ordinary BLIB linked into a compiler image would therefore overwrite its G!3 handler. The owner ledger used by optional extension registration is not a remedy for this import order.

The current MR10 BLIBI and [ICLIB](../../../mr10-kit-compiler/source/iclib.int) do not provide standard ABORT or STANDARDABORT. Current Core Runtime fault processing does not automatically route ABEND through G!3. Historical standard ABORT depends on postmortem facilities that are incompletely reconstructed.

## 4. Approved architecture

| Execution context | G!3 | G!112 |
| --- | --- | --- |
| Ordinary native application | Ordinary BLIB ABORT | No compiler-specific binding required |
| Compiler image, before first-phase F | Compiler master ABORT | STANDARDABORT |
| Compiler image, after first-phase F | STANDARDABORT (assigned by compiler) | STANDARDABORT |

Build ordinary BLIB and compiler-specific COMPBLIB as separate variants of common source, following the historical arrangement. Do not link both variants indiscriminately into one executable. Preserve ordinary BLIB and the accepted production baseline.

Prefer a common Core Runtime with library selection at link-edit time. The specific external symbol/trailer binding mechanism and initialization ordering require detailed design and verification in CBR.4. Do not infer a requirement for separate Core Runtime binaries or silently change ordinary global import behavior.

The interpreted compiler requires a suitable interpreted STANDARDABORT implementation. Establish its practical behavior and construction with the interpreted library work, respecting the ICINT20 bootstrap architecture and preserving MR10/ICINT19. Do not require comprehensive historical postmortem reconstruction for this milestone; any behavioral limitations must be explicit. Historical ABEND dispatch, early initialization error handling, argument availability and recursion/fallback behavior are separate CBR.4 investigations.

## 5. Verification obligations

- Inspect candidate object exports and IEWL maps to establish the intended library selection and global ownership; verify actual bound G!3 and G!112 with targeted MVS probes.
- Demonstrate ordinary BLIB behavior is preserved, compiler-specific ABORT is not overwritten, and explicit compiler-handler and standard-handler calls follow their documented diagnostics and return-code contracts.
- Verify first-phase F and applicable compiler-dependent error paths in the interpreter-hosted compiler by CBR.8; do not execute the native compiler during this milestone.
- Define and test the runtime ABEND dispatch contract separately within CBR.4; distinguish normal calls, recoverable runtime faults and MVS ABENDs. Do not claim full historical postmortem behavior or universal ABEND recovery without evidence.

No implementation, MVS job, global allocation, promotion or march transition is authorized by this record.
