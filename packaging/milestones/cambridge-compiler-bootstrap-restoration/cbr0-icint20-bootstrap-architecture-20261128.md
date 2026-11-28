# CBR.0 — ICINT20 bootstrap architecture

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Cambridge Compiler Bootstrap Restoration  
**March:** CBR.0 — Architecture and Dependency Reconciliation  
**Date:** 28 November 2026 EST  
**Review baseline:** `c1c2198bf7009a283674d7b9fcddcc8005e33775`  
**Status:** Owner-approved architecture and commitment; implementation remains gated by CBR.1.

## 1. Authority and scope

This record refines decisions 4, 8, 9, 11 and 15 in the [approved design discussion](../../architecture/cambridge-compiler-bootstrap-restoration-design-discussion-20261128.md) and the [governing milestone](milestone-cambridge-compiler-bootstrap-restoration.md). Read with the [source demotion inventory](cbr0-source-demotion-inventory-20261128.md), [INTCODE X-class Instruction Registry](../../architecture/intcode-x-class-instruction-registry.md) and [runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md).

The owner rejected configurable PROGVEC allocation because ICINT20 is intended to support the Cambridge Compiler bootstrap and continuing compiler development, not to become a general-purpose INTCODE execution product. The owner explicitly retained storage checks at critical operations and approved the resulting direction for commitment. The earlier configurable PROGVEC proposal is withdrawn.

## 2. Approved representation and storage architecture

Derive ICINT20 from ICINT19 while preserving ICINT19, the original MR10 Kit Compiler and all accepted baselines independently.

| Property | ICINT19 | ICINT20 direction |
| --- | --- | --- |
| Physical/interpreted word storage | 32-bit fullword | 32-bit fullword |
| Packed characters per word | Two in the low halfword | Four, most-significant byte first |
| Internal text | ASCII | ASCII |
| Interpreted pointer | Host byte address divided by four | Preserve word addressing |
| Instruction encoding | Existing compact instruction and fullword long operand | Preserve unless a demonstrated requirement is separately approved |
| X-class instructions | X1–X37 | Preserve meanings; update representation-dependent implementations |
| Global capacity | 700 words | Initially retain 700 words |
| Program/stack/work storage | One contiguous 40,001-word PROGVEC | One contiguous, fixed-capacity PROGVEC allocated by GETMAIN |

Retain assembly-time PROGCNT and PROGLEN constants. Fixed capacity means fixed for a particular assembled interpreter, not statically reserved storage in its load module. Do not introduce an EXEC PARM option for PROGVEC sizing, runtime sizing machinery or a selectable two-byte packing mode. Select a sufficient fixed capacity using actual MVS measurements and documented headroom, not an unverified numerical target.

G!54 STACKBASE is the first free word after loading; G!55 STACKEND is the exclusive allocation limit. Derive startup reporting, diagnostics and bounds from the same capacity definitions. The Cambridge Compiler's first-phase Pnnn controls its reserved procedure workspace within the available storage; it is not a request to resize PROGVEC. This decision narrows the interpreted allocation investigation in decision 4; the separately approved native runtime stack allocation investigation and historical parameter restoration remain in scope.

Keep ASCII internally, convert MVS text at the host boundary, and preserve the distinct target-code conversion to native System/370 characters. Binary record services and their X-class allocations remain CBR.3 work. X38/X39 remain unassigned.

## 3. Targeted storage safety

Review of [ICINT19 assembler](../../../mr10-kit-compiler/asm/icintv19.asm) identifies the following critical operations. Preserve existing effective checks, correct obsolete limits and add only the checks needed for reliable compiler hosting; comprehensive checking of every interpreted memory access is not an objective.

| Operation | Source finding and required behavior |
| --- | --- |
| STW / STC | STW stores and advances P without an explicit load-capacity check; STC allocates words via STW. Detect exhaustion before any out-of-range write; cover multiword instruction and relocation operands, partial character words and alignment. |
| OP1 | Preserve the existing program/global store guard; derive its limits from actual allocated extents rather than duplicated literals. |
| OP6 | Check new call-frame link stores and address arithmetic against available program/stack storage before writing. |
| X35 (APTOVEC) | Check requested workspace and the resulting frame, including its linkage and arguments, before constructing it. |
| Global and label references | Check index bounds before access to GUSED, global and label vectors in loader and relevant reference paths; preserve existing label/fixup semantics and report malformed references. |
| STRING37 | STRTEMP is eight fullwords (32 bytes); the conversion loop uses the source length without a corresponding buffer bound. Check supported name length and capacity before copying, with defined failure rather than truncation or overflow. |
| MAPSTORE | Its frame scan still uses PROGWORD+19998 although PROGCNT is 40001. Use actual extents and check the complete frame fields inspected before dereferencing. |

Storage exhaustion, malformed indices and invalid host string lengths must produce meaningful diagnostics and controlled termination or documented service failure, as appropriate, rather than storage corruption or an MVS abend. Check arithmetic used to calculate bounds for overflow. Retain program size, allocated capacity, available space, stack bounds and global-use reporting. Exact diagnostic codes and implementation details are to be settled and verified in CBR.1. The checks above do not imply full memory safety for arbitrary INTCODE.

## 4. Least-circular bootstrap construction

1. Keep the verified ICINT19/MR10 construction path as the seed. Assemble and link a separate ICINT20 candidate using IFOX and IEWL, without replacing installed ICINT19.
2. Run independent hand-written textual INTCODE fixtures under ICINT20 without BLIBI. Verify packing, arithmetic, control flow, relocation, stack and storage limits.
3. Generate a compatible candidate BLIBI from maintained BCPL source using the preserved MR10 compiler; stage the corresponding hand-written ICLIB separately. The historical MR10 BLIB PACKSTRING uses N/2 and two-byte padding and cannot be assumed compatible. Establish the minimal library needed for bring-up, then complete library and host-service restoration in CBR.2.
4. Use the existing MR10 compilation path to generate an applicable Cambridge compiler textual deck with the representation-dependent demotions reconciled. Test the candidate interpreter-hosted Cambridge Compiler and its generated native programs in CBR.2. Do not require a working ICINT20-hosted MR10 compiler to produce the first compatible library.
5. If word-dependent assumptions or textual-deck incompatibilities prevent this path, document the evidence and seek approval for the minimum necessary adaptation. Preserve historical source and executable decks.

Historical [bootstrap description](../../../richards-bcpltape/mr10/text/bstrbcpl) and [INTCODE specification](../../../richards-bcpltape/mr10/text/intcode) explicitly permit implementation-dependent word/byte packing. MR10 TRN serializes string length and character values, and CGI emits individual numeric C directives. Thus C3 C65 C66 C67 should load as X'03414243' in ICINT20; the corresponding ICINT19 words are X'00000341' and X'00004243'. This does not establish compatibility of arbitrary existing decks containing representation-dependent D constants, counts, initializers or code assumptions.

## 5. Verification and isolation

Use the existing [run-intcode](../../../tools/mr10/run-intcode) source-selected private assembly/link/run mechanism where practical. The installed MR10 compile-and-run path is explicitly ICINT19; do not silently redirect it. Candidate source, generated decks, load modules and evidence must remain separate from accepted components. Exact staging names, JCL region and promotion arrangements remain subject to review; no installation or MVS submission is authorized by this record.

CBR.1 verification shall include:

- Independent expected hexadecimal words and padding for character lengths 0, 1, 3, 4, 7, 8 and 255, including word/label/segment boundaries and continuation records.
- X36/X37 byte access at all four positions, crossing words, preserving adjacent bytes and validating the supported byte-value contract.
- Textual INTCODE instruction encoding, long operands, forward/backward labels, fixups, global initializers and segment handling.
- Signed 32-bit arithmetic, comparisons, shifts, control flow, calls, recursion, return and APTOVEC behavior.
- Exact boundary success and controlled failure for loader capacity, frame/workspace capacity, label/global bounds and host name buffer limits. Include MAPSTORE diagnostics above the obsolete 19,998-word boundary.
- Measured program occupancy and remaining stack/workspace, including realistic compiler workloads when available; select fixed capacity from evidence.
- Independent preserved ICINT19/MR10 smoke or applicable regression evidence at changed scope, followed by canonical reconstruction and full regression in CBR.9.

Use independent expected results, not solely self-consistent pack/unpack round trips. Record source revision, build and job identity, IFOX/IEWL/JES results and actual output. Historical capacity evidence includes [JOB 883](../../archive/bootstrap/job-883-capacity.md) and [JOB 893](../../archive/bootstrap/job-893-master-global-capacity.md). Those records explain earlier capacity changes but do not establish an ICINT20 capacity.

## 6. Qualifications and status

This is a source-grounded architecture decision, not an implementation or verification report. No ICINT20 code, JCL, allocation, installation, MVS execution or production promotion has been performed. Exact fixed capacity, complete word-dependent library/deck audit, detailed diagnostics and candidate isolation arrangements remain open. Full repository global collision audit, historical literal-splitting cause and separately named project charter remain qualified as recorded in earlier CBR.0 work.

CBR.0 remains OPEN; CBR.1–CBR.9 remain NOT STARTED. No change to the approved march sequence or acceptance requirements is authorized. Subsequent implementation requires the appropriate march opening and owner approval.
