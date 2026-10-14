# M2.0 Gate D — BCPLIO extraction boundary and plan

**Status:** Gate D design/selection complete; implementation and MVS acceptance **pending**. 14 October 2026.

## Choice

**Select BCPLIO before BCPLSTACK.** This is a substantive runtime subsystem with coherent stream/DCB state and substantial code footprint, but the current BCPLMAIN implementation couples it to startup, FINISH/STOP, STKOVFL, DEBUGINT and provisional WRITEST. Moving its code wholesale would change too many contracts at once. Gate D must be implemented as a staged extraction with independently assembled objects and demonstrable linkage, not a source split retaining BCPLMAIN's single CSECT.

## Measured and mapped baseline

The existing independently linked modules have verified sizes: JOBs 1269–1273 show BCPLAPT X'6C'; JOBs 1283–1295 show BCPLBYTE X'26' and BCPLMEM X'2AC'. Prior canonical BCPLMAIN (Gate B, before Gate C local GETBYTE/PUTBYTE removal) assembled to X'15A8' (JOB 1266). **This is not the post-Gate-C BCPLMAIN measurement.** Obtain its current size from JOB 1280 assembly ESD or post-Gate-C link map before reporting a precise current figure.

Current canonical BCPLMAIN source (post Gate C) is 2,078 lines. The main runtime CSECT starts at line 584. Executable I/O code starts with FINDINPUT at ~1076, PARM/selection/RDCH and QSAM input through ~1395; WRCH and output functions at ~1416–1583. Provisional WRITEST formatting lives at ~1585–1880 and DEBUGINT at ~1915. I/O static control/stream buffers and DCBs live at ~1995–2071. These are *source line locations*, not byte footprints. Retain provenance commentary even after refactoring; it documents provisional versus historical capabilities.

## Critical coupling / safety inventory

1. **Entry wiring:** BCPLMAIN publishes local assembler labels SELINP, INPENT, OUTENT, PARMENT, WRAPENT, RDCHENT, UNRDCHEN, FINDINP, FINDOUT, SELOUT, ENDWENT, ENDRDENT and WRCH into G11/G16/G17/G39/G33/G13/G15/G42/G41/G12/G47/G46/G14. Use EXTRN and relocated addresses once each routine moves; do not leave duplicate private implementations masquerading as external modules (lessons from Gates B/C).
2. **Bootstrap output:** BCPLMAIN currently clears OUTPOS, initializes OUTBUF, OPENs BCPOUT, and sets OUTCURR to OUT1CTL before START. BCPLIO must own these and expose a small **native-private IOINIT** entry. It must be called before any generated BCPL execution/diagnostic output and after the runtime state needed by IO is available.
3. **Termination:** FINISH/STOP flushes both output buffers, CLOSEs BCPOUT/BCPOUT2 and lazily opened BCPIN/BCPIN2, then drains BCPLMEM and frees the main allocation. BCPLIO must expose a native-private **IOFIN** entry, called from BCPLMAIN before MEMDRAIN and FREEMAIN, preserving the selected STOP return code. Avoid any access to freed storage during QSAM OPEN/CLOSE.
4. **Overflow:** STKOVFL currently writes directly into OUTBUF and sets OUTPOS before branching into FINIMPL. BCPLIO needs a bounded narrow private diagnostic interface or BCPLMAIN should call an existing BCPLIO output service with a documented register contract; the simplest consistent message remains `STACK OVERFLOW`. Changing RC/diagnostic behavior is out of scope.
5. **Bootstrap formatter / DEBUGINT:** WRITEST and DEBUGINT currently write to OUTBUF and OUTPOS directly. Moving the buffers without moving or adapting those clients breaks their private data references. Prefer retain existing output semantics while moving the formatter and DEBUGINT together with I/O, or add **one** private byte/record-append interface; avoid proliferating cross-CSECT shared-data exports. Historical BLIB WRITEF should remain preferred when exported.
6. **EODAD relocation:** BCPIN and BCPIN2 DCBs specify EODAD=INATEND/IN2ATEND. The DCBs and their EODAD handlers must be in the same BCPLIO ownership boundary and independently relocated. The external secondary DDNAME is **BCPINB**, never BCPIN2 (which is only the DCB assembly label).
7. **PARM bridge:** PARMENT currently reads PARMLIST saved at MVS entry by BCPLMAIN. Provide the original MVS PARM pointer once through IOINIT instead of exposing BCPLMAIN's private PARMLIST field.
8. **Registers/addressability:** The independent CSECT must establish its own base register strategy while preserving the generated-code invariants R0=0, R1/R2/R3 constants, R4 restoration from frame, R5/R6/R7..R9 calls, R11 SYSV, R12 G, R15 workspace. Private IOINIT/IOFIN use explicitly documented MVS R14 linkages and preservation. Particular care is needed with existing 16-register STM/LM save areas and nonreentrant global state, whose alignment and base-relative addressing currently rely on BCPLMAIN/MSVSAVE/SYSV USING scopes.
9. **Single owner:** BCPLIO owns DCBs, buffers, stream handles, EOF/pushback flags, output cursors and save areas; BCPLMAIN retains bootstrap storage/global registration, SYSV/FINISH, STOPRC and allocator release. Do not export random internal DCB/data labels to conceal a split ownership boundary.

## Implementation sequence

- **D1 — Independent module contract + skeleton:** Create `asm/bcplio.asm`, a named BCPLIO CSECT with a concise header (public BCPL entries, private IOINIT/IOFIN, register and lifecycle ABI, provisional behavior). Integrate separate SOURCE and DEVOBJ assembly route using reproducible resident JCL *before* modifying BCPLMAIN dispatch. Do not write production OBJ.
- **D2 — Migrate cohesive data and I/O service code:** Move input and output handlers plus their data/DCBs, associated EODAD paths and save arrays; update BCPLMAIN G installation to `=A(external symbol)` rather than local LA. Ensure BCPLIO can assemble with its own USING/LTORG boundaries; preserve existing fixed DD names, record and newline behavior.
- **D3 — Close all lifecycle dependencies:** Move/adapt WRITEST and DEBUGINT or supply a *single* narrow cross-module output API, port STKOVFL message and FINISH/STOP to IOFIN. Initialize with saved MVS PARM pointer using IOINIT. Maintain error return and existing QSAM ordering.
- **D4 — Install candidate / focused acceptance:** Confirm resident text round-trip for new BCPLIO source and modified BCPLMAIN; independently assemble and install **only DEVOBJ** members; verify IEWL MAP/XREF includes BCPLIO with external service references resolved to it. Run focused PDS regressions for output/string, named output, BCPIN/BCPINB and PARM input, STOP and overflow; compare exact expected records and step RCs. The full 124-case suite remains Gate F, not Gate D.
- **D5 — Record evidence:** Include actual assembled CSECT sizes, job numbers and list of accepted focused tests. Gate D only closes when independent dispatch, initialization, normal/error cleanup and regressions are evidenced.

## Disposition

**BCPLIO selected.** No assembler implementation change and no resident MVS dataset write in this planning step. Gate D **remains open**. BCPLSTACK is deferred until I/O extraction stabilizes. Do not treat the plan as evidence of a runnable independent BCPLIO.

## D1 implementation checkpoint

Added asm/bcplio.asm: independent CSECT with native-only IOINIT and IOFIN. IOINIT stores original EXEC parameter address from R1; IOFIN clears private state. R10 is clobbered as an independent base register; other general registers are preserved. This is a static nonreentrant skeleton, not yet a working stream service.

Added jcl/build-dev-bcplio.jcl: IFOX00 assembler and conditional IEBGENER installation targeting DEVOBJ(BCPLIO) exclusively. BCPLMAIN and runtime dispatch remain unchanged. Operator assembly verification is pending; the full Gate D remains open.

## D1 independent MVS assembly acceptance — 14 October 2026

- Initial source BUILD JOB 1301 failed: ASMIO IFOX00 RC=0008, IFO188 undefined IOSR10 after R10 register contract was deliberately changed to clobbered. PUTIO correctly did not execute. Corrected in Git commit `c00101f2b4da1f65f65ba422b5d68952cf95efe4` by removing stale `L 10,IOSR10`.
- Operator synchronized `HERC02.BCPL.SOURCE(BCPLIO)`: removal JOB 1303, compression JOB 1304, put JOB 1305, source readback JOB 1306. Readback confirmed BCPLIO CSECT, ENTRY IOINIT/IOFIN and no IOSR10 references.
- Submitted resident `JCL(BLDDEVI)` launcher JOB 1308, payload **JOB 1309**. `ASMIO` IFOX00 RC=0000, `PUTIO` IEBGENER RC=0000; no flagged assembler statements and highest severity zero. ESD: BCPLIO SD length **X'21' (33 bytes)**, IOINIT LD offset X'00', IOFIN LD offset X'0C'. Binary FB80 object installed to DEVOBJ(BCPLIO), not production OBJ.
- **D1 assembly checkpoint ACCEPTED.** This is not independent application linkage or functional I/O proof: BCPLMAIN has not yet been rewired and the skeleton does not handle streams. D2/D3 remain required; Gate D remains open.

## D2.1 independent output-service candidate — source committed

Commit `d49fa9023d68be32af8608529f3884488801bfe6` expands `asm/bcplio.asm` from a no-I/O D1 skeleton into an independent **candidate** output module. BCPLIO now owns one `SYSPRINT` QSAM DCB, a 132-byte output buffer, cursor, register save block and `IOACTIVE` flag. IOINIT opens the output DCB and blanks the buffer; IOFIN flushes a nonempty partial record and closes it. A new BCPL-convention `IOWRCH` append/newline entry is exported. The existing `jcl/build-dev-bcplio.jcl` builds it to `DEVOBJ(BCPLIO)` independently.

**Deliberate safety boundary:** BCPLMAIN, installed G14, STOP and FINISH remain unchanged. No application link or runtime I/O correctness is claimed. IOWRCH currently does not route overflow to STOP(12); when its 132-byte buffer is full it drops additional bytes. This is an explicit **unaccepted candidate limitation** and must be corrected before wiring G14 to BCPLIO. Likewise, IOINIT/IOFIN register preservation and OPEN/PUT/CLOSE effects must be validated under IFOX/MVS before being called by BCPLMAIN. D2.1 is a separate-object assembly checkpoint, not Gate D acceptance. No production OBJ changes.

## D2.1 MVS assembly checkpoint — 14 October 2026

Operator synchronized candidate SOURCE(BCPLIO): remove JOB 1316, compress JOB 1317, put JOB 1318, readback JOB 1319. Readback confirmed BCPLIO CSECT, three exports IOINIT/IOFIN/IOWRCH, and owned IODCB SYSPRINT definition. BLDDEVI launcher JOB 1321 and payload JOB 1322: ASMIO IFOX00 RC=0000; PUTIO IEBGENER RC=0000; zero assembler statements flagged and zero highest severity. DEVOBJ inventory now has six members: BCPLAPT, BCPLBYTE, BCPLIO, BCPLMAIN, BCPLMEM and BLIB. **D2.1 independent assembly checkpoint ACCEPTED.** No integrated BCPLIO application run, I/O semantics check or G14 transition was performed; Gate D remains open. Do not conflate successful assembly with QSAM OPEN/PUT/CLOSE runtime proof.

## D2.2 direct I/O probe, pending MVS validation

Added `asm/bcplio-output-probe.asm` (BCIOPRB standalone assembler entry) and `jcl/bcplio-output-probe.jcl` (independently assembles probe, IEWL INCLUDE DEVOBJ(BCPLIO), GO with SYSPRINT). It calls native IOINIT, emits `BCPLIO D2 PROBE` plus a newline using BCPL-style R5/R6/R7 IOWRCH calls, then calls native IOFIN. Expected output is one record containing `BCPLIO D2 PROBE`; all assembly, linkage and GO condition codes must be zero. Verify that IEWL XREF associates IOINIT, IOWRCH and IOFIN with BCPLIO, and that the output appears in the GO SYSPRINT section. This is a diagnostic first-run probe: failures will expose QSAM register/return linkage issues. It does not alter BCPLMAIN or production OBJ. Acceptance pending operator execution.
