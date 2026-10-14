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

### D2.2 first execution — JOB 1328 (14 October 2026)

Resident staging: SOURCE(BCIOPRB) JOB 1324, JCL(BCIOPRB) JOB 1325; launcher JOB 1327; payload **JOB 1328**. ASMPROB IFOX00 RC=0000, zero assembler diagnostic severity. LKED did not link: IEC141I **013-14** at `LKED/SYSLMOD`, followed by S013, so GO was flushed. Root cause in probe JCL: a freshly allocated temporary load-module dataset lacked an appropriate undefined-record DCB. Updated `jcl/bcplio-output-probe.jcl` in commit `9f05b49ce8eb468987c7a37fc389c10b245dc174` with `SPACE=(TRK,(5,5)),DCB=(RECFM=U,BLKSIZE=32760)` for `&&PROGLM`. This fixes the identified allocation mismatch; actual IEWL and GO success are **not yet proven**. Repeat after restaging JCL; no modification of BCPLIO object or production OBJ.

### D2.2 repeat JOB 1334: load-module dataset requires PDS member

After JCL replacement JOB 1329/1330/1331, payload JOB **1334** again assembled ASMPROB RC=0000 but abended IEWL `LKED/SYSLMOD` with **IEC141I 013-14**, S013; GO bypassed. `RECFM=U` sequential temporary `&&PROGLM` was insufficient. Comparison with repository's working `jcl/build-blib-object.jcl` (`&&PREPLD(BLIBPREP)` with three-part SPACE) identified the needed *partitioned load module member* allocation. Commit `0b9622a18cc3916cbfc51682587aee4bdccb8c14` changes the probe SYSLMOD to `&&PROGLM(BCIOPRB)` with `SPACE=(1024,(20,10,1)),DISP=(NEW,PASS)`. Retest still pending; no success claimed.

### D2.2 successful link-and-run checkpoint — JOB 1340

After SYSLMOD PDS-member JCL correction, operator replaced resident JCL(BCIOPRB) via JOB 1335 removal, JOB 1336 compression, JOB 1337 put. Launcher JOB 1339, payload **JOB 1340**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, JOB RESULT SUCCESS / highest RC=0000, and `dspal submit` shell exit 0. This confirms the independent probe can assemble, link-edit and execute against DEVOBJ(BCPLIO). **D2.2 final acceptance pending** inspection of the job report for exact `BCPLIO D2 PROBE` SYSPRINT record and IEWL MAP/XREF resolving IOINIT/IOWRCH/IOFIN. This milestone does not authorize BCPLMAIN redirection or a production OBJ change.

### D2.2 FINAL ACCEPTANCE — JOB 1340

Operator inspected `tools/dump-report-for-job 1340`. The GO SYSPRINT section contains a real output record `BCPLIO D2 PROBE` at report line 300 (distinct from the source listing). IEWL control and MAP/XREF record `INCLUDE OBJ(BCPLIO)`; load map lists BCPLIO at X'108' length X'20C', exports IOINIT X'108', IOFIN X'138', IOWRCH X'180'. Cross-reference resolves probe literal locations X'58' IOINIT, X'5C' IOWRCH, X'60' IOFIN to BCPLIO. Combined with ASMPROB/LKED/GO RC=0000 in payload JOB 1340, **D2.2 ACCEPTED** for the independent simple character/newline output path and lifecycle probe. This evidence does not validate overflow handling, register guarantees in all cases, multi-stream I/O, or any BCPLMAIN G-vector integration. Gate D remains open. Production OBJ unmodified.

## D2.3 hardening candidate — awaiting MVS verification

Commits `ad530e7b20470b59b9b6689ec5cb80b4af8afcc2` and `98ea1a549a9d6bd6fd304e8f95dd29476f207882` extend isolated BCPLIO and the BCIOPRB test. IOWRCH now saves R0-R9 and R11-R15 at entry across all paths (R10 explicitly clobbered, R4 restored from BCPL frame) and records a sticky output overflow status 12 rather than silently losing the indication. Native R14-linked IOSTAT reports status in R15. Probe first prints original marker and newline, then sends 133 EBCDIC X bytes against a 132-byte buffer, reads IOSTAT, requires 12 or exits RC=8; IOFIN flushes buffered record. Expected GO SYSPRINT: marker followed by a 132-X output record. **This does NOT yet reproduce STOP(12)** on overflow, and is deliberately NOT G14-ready. Call-sequence hardening and lifecycle sharing remain unaccepted pending MVS assembly/link/GO and explicit register sentinel verification. Production OBJ and BCPLMAIN unchanged.

### D2.3 first assembly/runtime probe — JOBS 1346 and 1352

Operator staged SOURCE(BCPLIO) in JOB 1341/1342/1343. BLDDEVI payload **JOB 1346**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, severity 0. Updated SOURCE(BCIOPRB) in JOB 1347/1348/1349, payload **JOB 1352**: ASMPROB RC=0000, LKED RC=0000, GO RC=0008. IEWL MAP/XREF resolves IOINIT, IOFIN, IOWRCH, IOSTAT from BCPLIO at X'148'; actual SYSPRINT contains `BCPLIO D2 PROBE` and a full 132-character X record. **The RC=8 is not yet valid evidence against IOSTATUS**: the probe erroneously performed the final R12-relative OVRESULT/load-literal comparison *after restoring R12 from the caller's savearea*. Probe corrected in `927349b793802520393b4a5b3ad33d6a8d6b05c6` to evaluate status before restoring R12, preserving final R15 result across epilogue. Repeat probe with only SOURCE(BCIOPRB) updated; DEVOBJ(BCPLIO) need not be rebuilt. D2.3 remains open.

### D2.3 JOB 1358: probe return-code epilogue defect

Updated SOURCE(BCIOPRB) staged by JOB 1353 (remove), 1354 (compress), 1355 (put). Launcher JOB 1357, payload **JOB 1358**: ASMPROB=0000, LKED=0000, GO=3680. Both expected actual SYSPRINT records present (marker and exactly 132 X characters); IEWL XREF resolves all four BCPLIO entries. Unlike the prior test's RC=8, decimal RC=3680 demonstrates an epilogue error: probe's `LM 14,12,12(13)` *also restores R15*, overwriting whichever return code was computed earlier. Commit `10825544910fe90e5e3b338ad581c1dbe394c5b2` fixes the probe with two explicit return paths, each restoring the caller's registers before setting the final R15 to 0 or 8. No change to BCPLIO or DEVOBJ needed. Await next GO result before claiming overflow-status validation.

### D2.3 overflow-status probe accepted — JOB 1364

Operator replaced SOURCE(BCIOPRB) through JOB 1359 rm, JOB 1360 compress, JOB 1361 put. Launcher JOB 1363, payload **JOB 1364**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; job success, highest RC=0000, submit exit 0. Probe specifically selects RC=0 only for native IOSTAT=12 after 133 character writes to 132-byte buffer, so this accepts overflow-status verification with the corrected R12/R15 epilogue. Previous JOB 1352/1358 reports show real marker and full 132-X record. **D2.3 remains open** for explicit register-sentinel proof; STOP(12) and BCPLMAIN lifecycle coordination remain subsequent integration work. Production OBJ unmodified.

### D2.3 register-sentinel validation candidate

Commit `6489da421564e5b3e81758360c0caef6f048ccdf` extends the standalone BCIOPRB probe with a `CHECKWR` wrapper around *every* IOWRCH call (regular characters, LF-triggered PUT, 132-byte boundary, 133rd overflow). It saves register images immediately before/after calls, compares R0-R3, R5, R7-R9, R11-R12, R15, and checks R4 restored from the BCPL frame. R6 is the BCPL return register, R10 private BCPLIO base; R13/R14 are separately used for MVS savearea/probe wrapper linkage, not sentinel-checked. Nonzero BADFLAG returns GO RC=8, as does an incorrect IOSTAT (must be 12). **Not yet MVS tested.** No changes to BCPLIO, BCPLMAIN, or production OBJ; only restage SOURCE(BCIOPRB), then submit existing JCL(BCIOPRB).

### D2.3 independent register-sentinel acceptance — JOB 1370

Operator restaged SOURCE(BCIOPRB) by JOB 1365 (remove), 1366 (compress), 1367 (put). Launcher JOB 1369; payload **JOB 1370** executed ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, JOB RESULT SUCCESS, highest RC=0000, submit exit 0. The probe snapshots registers around every IOWRCH call and checks promised unchanged registers, R4 frame restoration, and overflow status 12; any detected mismatch exits RC=8. Thus the **D2.3 isolated-interface hardening checkpoint is ACCEPTED** for all exercised paths: character write, newline PUT, full buffer, overflow. Acceptance remains limited to the tested linkage and does not demonstrate STOP(12) routing, complete BCPLMAIN integration, or the future full I/O service set. No production OBJ changes.

## D3 — BCPLMAIN lifecycle and diagnostics coupling: implementation contract

**Status: architectural inspection performed; runtime integration not yet implemented.** D3 is a *portion of Gate D* within milestone M2.0, not a milestone of its own. Source inspected: current `asm/bcplmain.asm` and independently proven `asm/bcplio.asm` (D2.3 JOB 1370).

### Verified dependencies and retained semantics

- Startup: BCPLMAIN lines ~821–827 zero `OUTPOS`, blank `OUTBUF`, OPEN `BCPOUT` on `SYSPRINT`, and select `OUT1CTL`. BCPLIO's IOINIT independently OPENs its own `IODCB` also on `SYSPRINT`. **Never activate both as simultaneous owners**. The eventual integrated candidate must OPEN primary output exactly once.
- G14: installed at ~784–785 from local `WRCH`. At ~1416 onward, WRCH selects `OUTCURR`; secondary output `OUT2CTL` dispatches to `WROUT2` and DCB `BCPOUT2` for DD `BCPALT`. Candidate IOWRCH writes only SYSPRINT; indiscriminate G14 replacement breaks selected-stream behavior. Move ownership and stream selection together or provide a BCPLIO dispatch entry covering both.
- Normal FINISH and STOP: `FINIMPL` zeros STOPRC; `STOPENT` copies R7 into STOPRC; `FINEXIT` at ~963–987 flushes and CLOSEs primary, secondary, and conditional input DCBs before `RELMEM` (MEMDRAIN / FREEMAIN), restores MVS caller registers and returns STOPRC. IOFIN must preserve the selected result and run before memory release. Never close a DCB twice; retain selective close of lazily opened inputs.
- Stack overflow: `STKOVFL` at ~1046 directly copies `STACK OVERFLOW` into `OUTBUF`, sets OUTPOS, and branches to `FINIMPL`. **Notably this branch selects the FINISH RC path (0), rather than STOPENT(12)**. Preserve existing observed behavior until a deliberate, separately tested policy decision; do not silently relabel it STOP(12). By contrast, normal primary WRCH overflow branches to `STOPENT` with R7=12 (~1441). Both cases need explicit tests.
- Formatter and diagnostics: `WRITEST` uses OUTPOS/OUTBUF from ~1594/~1853; `DEBUGINT` uses them from ~1941. A simple G14 rewrite leaves these direct buffer writers behind. Provide one narrow internal append/record interface owned by BCPLIO and migrate both callers together (or migrate the complete formatting/diagnostic code).
- BCPLIO current IOSTAT is diagnostic-only and its 133rd-character path latches 12 without terminating. This cannot replace the current G14 overflow/STOP semantics. The D2.3 sentinel probe proves its isolated contract, not integrated STOP routing.
- Input and PARM remain owned by BCPLMAIN: BCPIN and BCPINB input state and EODAD, PARMLIST and G11/G13/G15/G39/G41/G42/G46/G47 still require a separately verified ownership transfer in Gate D. An output-only integration is not evidence that all BCPLIO extraction is done.

### Controlled D3 implementation order

1. **D3.a Interface definition**: Write BCPLIO module ABI for lifecycle (IOINIT/IOFIN), primary and secondary stream selection, overflow/STOP handoff, and a single internal formatter/diagnostic append API. Keep private DCB/data labels private. Decide and document preservation for R10 across calls in a context where BCPLMAIN itself uses R10 as base.
2. **D3.b Ownership preparation**: Introduce a separate DEVOBJ-only integrated candidate linkage path; do not modify production OBJ or activate a second SYSPRINT OPEN. Verify that STOPRC remains live through IOFIN and register preservation across MVS macros. Distinguish intentional final lifecycle events from premature termination.
3. **D3.c Functional wiring**: Migrate G14 stream-aware dispatch and both output DCBs/buffers; adapt WRITEST/DEBUGINT/stack-overflow diagnostics to the single interface; migrate conditional input cleanup and PARM handling with matching ownership. Update BCPLMAIN source and DEVOBJ assembly only once all references have an actual owner.
4. **D3.d Targeted proof**: IEWL MAP/XREF must resolve BCPLIO services independently. Focused tests: SYSPRINT primary, BCPALT secondary, newline/132-byte boundary, overflow RC=12, STOP(N) preserved after flush, FINISH RC=0, stack-overflow marker/legacy RC, formatter and DEBUGINT output, BCPIN/BCPINB EOF, and PARM. Run D4-focused native regressions after all of these pass.

**Safety:** D3 inspection/design is not an acceptance checkpoint. No BCPLMAIN or BCPLIO code changes, no resident MVS writes, and no production OBJ changes in this portion. Gate D remains open.

### D3 first implementation slice — lifecycle ABI candidate

Contract documented in `packaging/m2-0-d3-bcplio-linkage-contract.md` (commit `5c3843b`). BCPLIO `IOINIT` and `IOFIN` now preserve R0-R9 and R11-R15 across OPEN/PUT/CLOSE, with R10 explicitly clobbered; IOINIT avoids reopening while active; IOFIN retains conditional close (commit `ba71439`). Independent BCIOPRB now invokes IOINIT twice and IOFIN twice to exercise idempotency while retaining character/newline, overflow, and register-sentinel checks (commit `1e348fb`). **Candidate not yet assembled/validated on MVS; D3 remains open.** BCPLMAIN and production OBJ unchanged. No G14 redirection or duplicate SYSPRINT OPEN in integrated execution.

### D3 independent lifecycle checkpoint ACCEPTED — JOBS 1376 and 1382

Operator staged BCPLIO to SOURCE with JOB 1371 rm, 1372 compress, 1373 put; launcher JOB 1375, payload **JOB 1376**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, job SUCCESS, zero assembler statements flagged. Probe source staged via JOB 1377 rm, 1378 compress, 1379 put; launcher JOB 1381, payload **JOB 1382**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, job SUCCESS, zero flagged statements. This accepts **the first D3 isolated IOINIT/IOFIN lifecycle checkpoint**, including repeated calls within the probe plus retained output/status/sentinel assertions. It does **not** establish full integration, stream-aware G14, STOP(12), BCPALT, input/parameter ownership, or exact output-record count without inspecting GO SYSPRINT. BCPLMAIN and production OBJ unchanged. D3 and Gate D remain open.

### D3 two-stream output candidate — independent test pending

Added BCPLIO selected-output ownership candidate in `asm/bcplio.asm` (commit `3b6300b`): SYSPRINT primary retained, a separate BCPALT QSAM DCB and 132-byte buffer are owned by BCPLIO; native `IOSEL` accepts R1=1 or 2 and returns R15=0 or 8, opening BCPALT lazily on first selection. IOWRCH routes writes and LF PUT to selected DCB; IOFIN flushes/closes both active DCBs even if primary is selected. Same sticky status 12 is shared across streams, with no STOP integration. IOINIT initializes selected primary. This **candidate requires MVS IFOX/IEWL/GO verification**; do not call it accepted.

Added `asm/bcplio-two-stream-probe.asm` (resident SOURCE member BC2SPRB) and `jcl/bcplio-two-stream-probe.jcl` (resident JCL member BC2SPRB) to assemble, link from DEVOBJ(BCPLIO), and run independently. Expected GO output: SYSPRINT record `BCPLIO PRIMARY 1` from explicit LF plus partial `BCPLIO PRIMARY 2` flushed by IOFIN; BCPALT one partial `BCPLIO ALTERNATE` flushed by IOFIN. Probe fails RC=8 if IOSEL rejects valid streams. Acceptance requires both report output DD sections separately verified (not merely string literals in assembly listing), clean ASM/LKED/GO, and IEWL XREF showing IOSEL/IOWRCH/IOFIN/IOINIT resolved in BCPLIO. Current BCIOPRB normal/overflow/reg sentinel probe should be rerun to exclude regressions. No BCPLMAIN/G14 changes; production OBJ untouched.

This is only the first **independent two-stream** output candidate. BCPL-compatible FINDOUTPUT, SELECTOUTPUT, OUTPUT, WRAPOUTPUT and ENDWRITE entry conventions, STOP(12), WRITEST/DEBUGINT/stack diagnostics, and input/PARM ownership remain pending within Gate D.

### D3 two-stream candidate assembly/link/GO — JOBS 1388 and 1393

Operator staged new BCPLIO SOURCE with JOB 1383 rm, 1384 compress, 1385 put; BLDDEVI launcher JOB 1387, payload **JOB 1388**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000; SUCCESS, zero flagged statements. Staged two-stream SOURCE(BC2SPRB) JOB 1389 and JCL(BC2SPRB) JOB 1390. Launcher JOB 1392, payload **JOB 1393**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; SUCCESS, zero flagged statements. **Independent two-stream assemble/link/execute checkpoint PASS.** Final routing acceptance remains pending inspection of the GO SYSOUT DD sections to distinguish primary SYSPRINT records from alternate BCPALT records; RC=0 alone does not establish proper destinations. No BCPLMAIN or production OBJ change.

### D3 two-stream standalone checkpoint accepted — JOB 1393 output inspection

Operator extracted JOB 1393 report. Actual output records at lines 354–357: `BCPLIO PRIMARY 1`, `BCPLIO PRIMARY 2`, `BCPLIO ALTERNATE`. JES GO allocation includes both `SYSPRINT` and `BCPALT`, with distinct SYSOUT datasets `SO0104` and `SO0105`. IEWL cross-reference identifies IOINIT at X'188', IOFIN X'1DC', IOWRCH X'260', IOSEL X'326' in BCPLIO; references at X'B0', X'B8', X'BC', X'B4' resolve to BCPLIO. Combined with JOB 1388 ASMIO/PUTIO RC=0 and JOB 1393 ASMPROB/LKED/GO RC=0, **the independent two-stream output checkpoint is accepted**. Caveat: merged dump excerpt alone does not explicitly label individual record-to-DD association; retain a separate raw SYSOUT verification for strict routing assurance. This does not close D3 or Gate D: BCPL-compatible stream services, STOP(12), formatter/diagnostic ownership and BCPLMAIN integration remain pending. Production OBJ untouched.

### D3 BCPL-facing output stream ABI candidate — MVS test pending

Commit `102222f` adds five independent BCPL R6-linked exports to BCPLIO: IOFOUT (FINDOUTPUT: R7 points to word-addressed BCPL string, returns word-addressed module-owned stream handle or zero; lazily opens BCPALT), IOSOUT (SELECTOUTPUT: R7 handle), IOOUT (OUTPUT: returns current handle R7), IOWRAP (WRAPOUTPUT: PUT alternate record if selected), IOENDW (ENDWRITE: flush/close selected alternate, restore primary). Uses static BCPLIO IOCTL1/IOCTL2 handles and per-stream DCB buffers, with R4 frame restore; primary SYSPRINT remains owned by IOINIT/IOFIN. Compared current BCPLMAIN G41/G12/G17/G16/G47 semantics and BCPL string lengths 8/6, retaining stream-dependent behavior. This is **candidate code, not yet MVS-tested**, and not yet installed as G-vector entries.

Added `asm/bcplio-stream-abi-probe.asm` and `jcl/bcplio-stream-abi-probe.jcl` (resident member **BCSTRPB** in SOURCE and JCL). Its independent link-edit includes only DEVOBJ(BCPLIO). The probe checks FINDOUTPUT primary/alternate nonzero handles, OUTPUT current handle, SELECTOUTPUT alternate, WRAPOUTPUT alternate, ENDWRITE restores primary, and normal FINISH-style IOFIN. Expected actual output: SYSPRINT `BCPLIO HANDLE PRIMARY`; BCPALT `BCPLIO HANDLE ALT WRAP` and `BCPLIO HANDLE ALT END`. GO must return RC=0; RC=8 flags handle/routing assertion mismatch. Check both actual DD outputs and IEWL MAP/XREF; rerun earlier BCIOPRB/BC2SPRB probes after BCPLIO rebuild. **D3 remains open**: STOP(12) handoff, WRITEST/DEBUGINT and input/PARM ownership, BCPLMAIN DEVOBJ wiring not done. Production OBJ untouched.

### D3 BCPL-facing output ABI — JOBS 1399 and 1404 initial pass

Operator staged BCPLIO via JOB 1394 remove, 1395 compress, 1396 put. BLDDEVI launcher JOB 1398, payload **JOB 1399**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, zero flagged statements. Probe SOURCE(BCSTRPB) staged JOB 1400 and JCL(BCSTRPB) JOB 1401. Launcher JOB 1403, payload **JOB 1404**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, zero flagged statements. Probe explicitly checks primary/alternate FINDOUTPUT handles, OUTPUT current handle, alternate SELECTOUTPUT, and primary restoration after ENDWRITE; RC=0 means these assertions passed. **Acceptance of correct DD record routing remains pending** GO output inspection for primary and both alternate records, and IEWL MAP/XREF verification. D3 and Gate D remain open. BCPLMAIN and production OBJ untouched.

### D3 BCPL-facing stream ABI independent checkpoint ACCEPTED — JOB 1404

Operator inspected complete JOB 1404 report: actual execution-output records at lines 420, 422–423 are `BCPLIO HANDLE PRIMARY`, `BCPLIO HANDLE ALT WRAP`, `BCPLIO HANDLE ALT END`. GO allocation includes SYSPRINT and BCPALT. IEWL MAP lists BCPLIO origin X'218', length X'718' and BCPL-facing entries IOFOUT X'446', IOOUT X'4D2', IOSOUT X'4DE', IOWRAP X'52E', IOENDW X'574'; relocation cross-reference maps probe references X'104'/X'108'/X'10C'/X'110'/X'114' to BCPLIO. Combined with JOB 1399 ASMIO/PUTIO RC=0000 and JOB 1404 ASMPROB/LKED/GO RC=0000 and the probe's checked handle/selection assertions, **independent BCPL stream ABI checkpoint ACCEPTED**. Merged report does not independently label each actual record with its output DD; treat strict DD provenance as an optional additional evidence check. This is not G-vector integration acceptance. D3/Gate D remain open; production OBJ unchanged.

### D3 opt-in STOP(12) overflow handoff candidate — MVS verification pending

BCPLIO now exports private native `IOBIND` to register a nonreturning caller-owned overflow callback. IOWRCH on the 133rd byte latches 12, restores promised registers, sets R7=12 and branches to caller's handler through scratch R10. Without a bound handler it retains the D2.3 sticky status behavior. Source commits `99e32e5`, `cb44c953`. Independent probe `asm/bcplio-overflow-handoff-probe.asm` + resident SOURCE(BCOVPRB), and JCL(BCOVPRB) link **only DEVOBJ(BCPLIO)**. Callback checks R7/IOSTAT=12, calls IOFIN, and exits GO **RC=0012 expected**; an early return or status failure returns RC=0008. Inspect GO SYSPRINT for exactly 132 X characters and linker IOBIND resolution. MVS execution is pending. The job-summary wrapper may label expected RC=12 as FAILURE; examine exact steps and records rather than treating success text as the criterion. Existing STKOVFL remains distinct and unchanged, as do BCPLMAIN and production OBJ. This does not close D3.

### D3 overflow handoff first run FAILED — JOB 1415

Operator staged updated SOURCE(BCPLIO) JOB 1405 remove, 1406 compress, 1407 put; BLDDEVI launcher JOB 1409, payload **JOB 1410**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, zero flagged statements. Staged SOURCE(BCOVPRB) JOB 1411 and JCL(BCOVPRB) JOB 1412. Launcher JOB 1414, payload **JOB 1415**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, **GO reported RC=6556**, NOT the expected RC=0012. Submit command exit status 1. **D3 overflow handoff checkpoint FAILED; do not accept or wire G14.** Need GO execution report (IEF completion/abend lines, register/PSW or dump, SYSPRINT 132-character output) before diagnosing cause and modifying code. Existing DEVOBJ(BCPLIO) now holds the unaccepted callback candidate; production OBJ untouched.

### D3 JOB 1415 diagnostic follow-up — probe return-base defect corrected, retest pending

Full report shows `IEF142I BCOVPRB GO - STEP WAS EXECUTED - COND CODE 9356` and a complete 132-X output record; no explicit S0C/PSW diagnostic appeared in the extracted grep. The anomalous 9356 (job-summary displayed RC=6556) is consistent with a bug in `asm/bcplio-overflow-handoff-probe.asm`: at RETMVS it restored caller R12 through `LM 14,12,12(13)` and *then* executed `L 15,RCVALUE`, which requires the probe's R12 base. This load therefore reads through the restored caller base, not the probe base. Fixed in commit `48587b7` by distinct RETGOOD/RETBAD sequences that restore caller registers and subsequently set R15 with register-immediate `LA 15,12` or `LA 15,8`, without R12-relative storage access. BCPLIO implementation unchanged. **Diagnosis plausible but unconfirmed until repeat MVS execution; D3 overflow checkpoint remains unaccepted.** Only SOURCE(BCOVPRB) needs restaging; DEVOBJ(BCPLIO) and JCL(BCOVPRB) are unchanged.

### D3 STOP(12) callback retest ACCEPTED — JOB 1421

Operator staged corrected SOURCE(BCOVPRB): remove JOB 1416, compress JOB 1417, put JOB 1418; launcher JOB 1420, payload **JOB 1421**. ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, **GO RC=0012 exactly as intended**, zero assembler statements flagged. The submission wrapper returned exit 1 and labeled job FAILURE because GO intentionally returned nonzero; this is an **expected result for this probe**, not a failed assertion. The probe validates the bound overflow callback, R7=12 and IOSTAT=12 assertions, callback-owned IOFIN and explicit 12 return for primary stream. Corrected probe return sequence fixed JOB 1415's anomalous GO completion code. JOB 1415 previously showed a full 132-character X output record; JOB 1421 actual output record has not yet been independently inspected. **D3 isolated primary overflow/STOP(12) callback checkpoint ACCEPTED** subject to optional renewed output-record inspection. This does not prove alternate overflow, BCPLMAIN STOP integration or STKOVFL behavior. D3/Gate D open. Production OBJ untouched.

### D3 primary diagnostic append boundary — candidate pending MVS verification

Added independent, bounded `IODIAG` to `asm/bcplio.asm` (commit `df96ed1`), with private native ABI R1=byte address, R2=length, R15=0/8/12, preserving R0–R9/R11–R14 and clobbering R10. Appends to SYSPRINT primary regardless of currently selected stream; output buffer and overflow status remain BCPLIO-owned. No output PUT or STOP callback occurs during IODIAG. This provides a single intended diagnostic transport mechanism without exporting DCB/buffer labels.

New isolated `asm/bcplio-diagnostic-probe.asm` and `jcl/bcplio-diagnostic-probe.jcl`, resident members SOURCE(BCDIPRB) / JCL(BCDIPRB), use DEVOBJ(BCPLIO), with SYSPRINT and BCPALT DDs in GO. Expected ASMIO, PUTIO, ASMPROB, LKED, GO all RC=0000; GO SYSPRINT record begins `BCPLIO DIAG PRIMARY` and is padded to 132; BCPALT remains unused output despite being opened by IOSEL. Probe verifies complete append, boundary 132, next-byte IODIAG return 12, and sticky IOSTAT=12.

**This does not yet adapt WRITEST or DEBUGINT or preserve STKOVFL's replacement semantics.** Such integration needs further design and separate DEVOBJ-only checks, especially the provisional WRITEST cursor and diagnostic policies. New candidate has not been run under MVS and is not accepted. Production OBJ untouched. Gate D/D3 open.

### D3 diagnostic append isolated build/run checkpoint — JOBS 1427 and 1432

Operator staged SOURCE(BCPLIO) via JOB 1422 remove, 1423 compress, 1424 put; BLDDEVI launcher JOB 1426, payload **JOB 1427**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, zero flagged statements. Staged SOURCE(BCDIPRB) JOB 1428 and JCL(BCDIPRB) JOB 1429; launcher JOB 1431, payload **JOB 1432**: ASMPROB IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, zero flagged statements. Probe's successful return supports its IODIAG full/overflow status assertions. **Independent assembly/link/run checkpoint PASSED**, pending actual GO SYSPRINT record inspection and IEWL IODIAG resolution before recording complete acceptance. BCPLMAIN and production OBJ unchanged; D3 remains open.

### D3 IODIAG independent checkpoint ACCEPTED — JOB 1432

Operator inspected the complete JOB 1432 report. GO output record at line 345 begins `BCPLIO DIAG PRIMARY`. IEWL map lists BCPLIO origin X'1D8', length X'7FC', IODIAG entry X'5C2'; cross-reference maps probe offset X'A0' to IODIAG in BCPLIO. Combined with JOB 1427 ASMIO/PUTIO RC=0000 and JOB 1432 ASMPROB/LKED/GO RC=0000, the probe's boundary-132 and IOSTAT=12 assertions, **D3 independent primary diagnostic append checkpoint ACCEPTED**. No WRITEST, DEBUGINT or STKOVFL integration has yet been proved; output stream DD provenance is inferred from selected-stream test and the primary-only append implementation. D3 and Gate D remain open; BCPLMAIN and production OBJ unchanged.

### D3 coordinated integration candidate — batch implementation, MVS verification pending

Four development elements were implemented as a single **isolated candidate**, not sequentially accepted checkpoints. Canonical `asm/bcplmain.asm`, its DEVOBJ(BCPLMAIN), and production `HERC02.BCPL.OBJ` have **not** been changed.

- `asm/bcplio.asm`: new private `IOREPL` operation (native R14, R1=byte source, R2=length 0..132, R15=0/8) replaces the pending primary record, preserving selected BCPALT. Callback handoff now restores interrupted BCPLMAIN R10 from `IOSAVE+40` and branches through R14 instead of leaving R10 as private BCPLIO base. These changes require retest of the existing overflow probe.
- `asm/bcplmain-d3-candidate.asm`: exact canonical BCPLMAIN source copied as a *separate source* then adapted. Startup calls IOINIT with saved EXEC PARM, installs IOBIND callback, and skips BCPLMAIN's old SYSPRINT OPEN. G14/G41/G12/G16/G17/G47 output operations install external BCPLIO entry addresses. FINISH/STOP runs IOFIN before existing input-close and memory drain. `STKOVFL` invokes IOREPL with `STACK OVERFLOW` then retains existing FINIMPL RC policy. Provisional WRITEST retains its existing formatter logic, writes into local WFBUF staging only, and transports completed bytes with one IODIAG call. DEBUGINT similarly uses a private DBGBUF and one IODIAG transport per integer. Both save/restore machine registers across native calls. Inert legacy output labels/DCBs still appear in candidate source but are not opened or installed in active output G-vector; remove them after verifying integrated routing rather than prematurely altering unrelated BCPLMAIN addressability.
- `jcl/build-dev-bcplmain-d3.jcl`: assemble SOURCE(BCPLM3) into **DEVOBJ(BCPLM3) only**; this deliberately does not overwrite canonical DEVOBJ(BCPLMAIN) or production OBJ. The source CSECT remains named BCPLMAIN so IEWL can link the candidate from member BCPLM3 explicitly.

**No MVS build, linkage or GO execution has occurred for the combined candidate.** Integration may still have assembler, register, lifecycle, formatting or QSAM errors; do not claim it accepted. Required evidence: (1) BCPLIO build zero diagnostics, prior BCIOPRB/BC2SPRB/BCSTRPB/BCOVPRB/BCDIPRB probes rechecked, (2) BCPLM3 independent ASM/PUT to DEVOBJ only, (3) IEWL map explicitly includes OBJ(BCPLM3) and OBJ(BCPLIO) and no unwanted production BCPLMAIN, (4) focused end-to-end regression for primary/alternate output, STOP=12 and FINISH, DEBUGINT, WRITEST, stack diagnostic, and input/PARM preservation. Only thereafter consider D3 accepted or D4. The combined batch reduces development passes, not test obligations. Gate D remains open.

### D3 integrated candidate readiness and register repair

Commit `f2168aa` fixes a critical prerequisite for callback transfer: `IOWRCH` captured R10 only *after* using it for the BCPLIO private assembler base; it now copies the **incoming** R10 into R4 before its BALR and saves that value in IOSAVE+40. On nonreturning overflow the callback receives the restored BCPLMAIN base in R10. Commit `fb6ac26` also makes the BCPL-facing IOWRCH/IOFOUT/IOSOUT/IOOUT/IOWRAP/IOENDW entries restore caller R10 on ordinary return, whereas previously they clobbered it. These are untested changes; re-run all independent probes.

**Integration build only, no acceptance yet:** stage `asm/bcplio.asm` as SOURCE(BCPLIO), run existing BLDDEVI and confirm ASMIO/PUTIO RC=0. Stage `asm/bcplmain-d3-candidate.asm` as SOURCE(BCPLM3); stage `jcl/build-dev-bcplmain-d3.jcl` as JCL(BLDD3MN) and submit. Require ASMMMAIN/PUTMAIN RC=0 and assembled symbol external-reference inventory. Then construct separate IEWL link/run evidence for the target tests with `INCLUDE OBJ(BCPLM3)` (not OBJ(BCPLMAIN)) and `INCLUDE OBJ(BCPLIO)`; do NOT run ordinary production-PDS regression expecting it to select the candidate automatically. Unvalidated integration, provisional WRITEF/DEBUGINT formatting, stack overflow RC, and external module ABI are not yet accepted. In particular the candidate *retains dormant old output routines and DCB declarations*: only successful linkage and integration tests can establish they never become active.

Added `jcl/bcplio-d3-integration-link.jcl` as resident JCL(D3LINK): IEWL-only, explicit INCLUDE DEVOBJ(BCPLM3), DEVOBJ(BCPLIO), DEVOBJ(BCPLMEM), DEVOBJ(BCPLBYTE), DEVOBJ(BCPLAPT), DEVOBJ(BLIB), ENTRY BCPLMAIN, MAP/XREF. No GO step, no production OBJ access. Require LKED RC=0000, no unresolved EXTRNs, and map verifying the BCPLIO output entries resolved independently. Does not substitute for integrated BCPL application execution.

### D3 first combined BCPLIO assembly failed — JOB 1438; base repair pending retest

Operator staged SOURCE(BCPLIO) JOB 1433/1434/1435; BLDDEVI launcher JOB 1437 payload **JOB 1438**, ASMIO IFOX00 RC=0008, PUTIO bypassed. IFOX diagnosed exactly three **IFO209 addressability** errors, assembler statements 458, 461, 463; no DEVOBJ replacement occurred. The IOREPL entry established `USING *,10` at its own BALR base, but its branches to earlier IODIAG-owned `IODRET` and EX template `IODMOVE` refer *backwards before that base*, which cannot be encoded in a nonnegative 12-bit S/370 displacement. Commit `dd69c65` supplies IOREPL-local `IORRET` and `IORMOVE` forward within its USING scope, preserving the same shared save area and status behavior. This is a source-based diagnosis of the three failures, **not yet verified by a new assembler listing**. Repeat SOURCE staging and BLDDEVI; do not run BCPLM3 or D3LINK until ASMIO/PUTIO succeed. Production OBJ untouched.

### D3 combined candidate BCPLIO assembly recovered — JOB 1444

Operator synchronized corrected SOURCE(BCPLIO) using JOB 1439 remove, 1440 compress, 1441 put. BLDDEVI launcher JOB 1443, payload **JOB 1444**: ASMIO IFOX00 RC=0000; PUTIO IEBGENER RC=0000; zero assembler statements flagged, highest severity 0, job SUCCESS. This verifies commit `dd69c65` fixed JOB 1438's three IFO209 addressability errors; corrected independent BCPLIO object installed in DEVOBJ(BCPLIO), production OBJ untouched. **BCPLIO assembly checkpoint ACCEPTED**, but independent runtime regression of changed R10 handling/IOREPL and integrated BCPLMAIN candidate not yet tested. Proceed to isolated BCPLM3 assembly next. D3/Gate D remain open.

### D3 combined BCPLMAIN candidate assembly ACCEPTED — JOB 1449

Operator staged SOURCE(BCPLM3) JOB 1445 and JCL(BLDD3MN) JOB 1446. Launcher JOB 1448, payload **JOB 1449**: ASMMMAIN IFOX00 RC=0000, PUTMAIN IEBGENER RC=0000; assembler flagged statements 0, severity 0. Combined with JOB 1444 successful BCPLIO ASMIO/PUTIO, both modules now independently assemble and reside in DEVOBJ as BCPLM3 and BCPLIO, leaving canonical BCPLMAIN DEVOBJ and production OBJ unchanged. **Combined D3 assembler/installation checkpoint accepted.** The candidate has not yet been linked with the other runtime modules or executed. Next verify JCL(D3LINK) against DEVOBJ-only and inspect IEWL map and unresolved references. Gate D/D3 open.

### D3 combined candidate integrated link-edit — JOB 1453 PASSED

Operator installed JCL(D3LINK) via JOB 1450 and submitted launcher JOB 1452, payload **JOB 1453**. LKED IEWL RC=0000; job SUCCESS, highest RC=0000. Link-only JCL explicitly includes DEVOBJ(BCPLM3), DEVOBJ(BCPLIO), DEVOBJ(BCPLMEM), DEVOBJ(BCPLBYTE), DEVOBJ(BCPLAPT) and DEVOBJ(BLIB), without a GO step or production OBJ. **Integrated link-edit checkpoint PASSED.** IEWL MAP/XREF and potential LET-tolerated unresolved references still require inspection before claiming complete symbol-resolution acceptance; no integrated runtime execution yet. D3 and Gate D remain open.

### D3 integrated candidate MAP/XREF ACCEPTED — JOB 1453

Operator inspected complete JOB 1453 report. All explicit INCLUDE directives from DEVOBJ reported IEW0000; IEWL RC=0000, no displayed unresolved warnings. Map CSECTs: BCPLMAIN (DEVOBJ member BCPLM3) X'0000' length X'1730'; BCPLIO X'1730' length X'08AC'; BCPLMEM X'1FE0' length X'2AC'; BCPLBYTE X'2290' length X'26'; BCPLAPT X'22B8' length X'6C'; BLIB X'2328' length X'1BB0'. XREF resolves IOINIT, IOFIN, IOWRCH, IOBIND, IODIAG, IOREPL, IOFOUT, IOSOUT, IOOUT, IOWRAP and IOENDW all to BCPLIO, and STKOVFL to BCPLMAIN. **D3 integrated link MAP/XREF checkpoint ACCEPTED**; no GO execution or BCPL behavior acceptance yet. Production OBJ untouched.

### D3 five-probe independent regression PASS — JOBS 1456–1468

Operator reran all five isolated probes against rebuilt DEVOBJ(BCPLIO): BCIOPRB JOB **1456** ASMPROB/LKED/GO RC=0000; BC2SPRB JOB **1459** all RC=0000; BCSTRPB JOB **1462** all RC=0000; BCDIPRB JOB **1465** all RC=0000; BCOVPRB JOB **1468** ASMPROB/LKED RC=0000, GO **RC=0012 expected**. All IFOX flagged statement counts zero. **Existing isolated BCPLIO regression checkpoint ACCEPTED** on code containing the D3 R10 return/overflow changes. No direct test of new IOREPL is included among these five, and integrated BCPLMAIN/BCPLM3 GO is still untested. D3 and Gate D remain open; production OBJ untouched.

### D3 candidate-only first integrated GO harness prepared — PENDING JES

Native regression 00 will compile normally through Cambridge on MVS and assemble the generated application only, then link exclusively from HERC02.BCPL.DEVOBJ with **BCPLM3** (exports BCPLMAIN), **BCPLIO**, BCPLBYTE, BCPLAPT, BCPLMEM and BLIB. Implementation: `tools/checks/prepare-runtime-pds-regression.py` now accepts opt-in `BCPL_RUNTIME_CANDIDATE=1`, which requires `BCPL_RUNTIME_LIBRARY=DEVOBJ` and selects INCLUDE OBJ(BCPLM3), INCLUDE OBJ(BCPLIO) in that order instead of OBJ(BCPLMAIN). `native-compiler/regression/run-test.sh` rejects candidate use unless `BCPL_RUNTIME_PDS=1` and `BCPL_RUNTIME_LIBRARY=DEVOBJ`. Normal production regression configuration is unchanged. No production OBJ writes, and regression-generated JCL uses temporary SYSDA objects.

Operator command (individual invocation, no shell &&):

```bash
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression 0 --show-output
```

Expected: Cambridge compile succeeds; native ASMAP/LKED/GO all RC=0000; case 00 has no BCPL output. The GO job report and map should independently identify CSECT BCPLMAIN from DEVOBJ(BCPLM3) plus BCPLIO. **This test has not yet run.** Preserve D3 open until actual MVS evidence, and expand to output/STOP cases only after case 00 passes.

### D3 first integrated candidate BCPL regression PASS — test 00

Operator ran `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression 0 --show-output` after syncing commit `999fdcd`. Native regression **00-most-degenerate-bcpl-program PASS**; summary PASS 1, FAIL 0, SKIP 0. This first actual integrated execution uses the explicitly selected DEVOBJ(BCPLM3) + DEVOBJ(BCPLIO) candidate, together with supporting runtime objects. Case 00 exercises startup/START/FINISH/return without BCPL output. The supplied console summary does not include the underlying JES job number or step-level RCs, which remain in the per-case regression log if needed. **First integrated candidate GO smoke checkpoint ACCEPTED on runner-level evidence**. D3 remains open pending output, diagnostics, STOP and stack behavior; production OBJ untouched.

### D3 first integrated functional expansion — regressions 01–04 PASS

Operator explicitly ran `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression 1 4 --show-output` following prior 00 PASS. Results: **01-one-procedure-call PASS, 02-local-zero-test PASS, 03-single-character-output PASS, 04-string-output PASS**; runner summary PASS 4, FAIL 0, SKIP 0. Alongside regression 00, total integrated DEVOBJ candidate functional evidence **5 PASS, 0 FAIL**. Character and string output successfully traverse externalized BCPLIO. No separate JES job numbers/step RCs supplied; logs reside under workarea/native-regression/logs. **D3 integrated baseline 00–04 checkpoint ACCEPTED**. D3 still open pending formatter, dual-stream, STOP/diagnostics and overflow execution.

### D3 candidate integrated regressions 05–14 PASS

Operator executed `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression 5 14 --show-output` after syncing `4d35cd7`. All ten cases **05–14 PASS**, runner summary PASS 10, FAIL 0, SKIP 0. These cover variable output, local/global state, local vectors, nonzero and variable subscripts, vector argument and callee mutation, and two-/three-argument linkage. Cumulative sequential integrated D3 candidate evidence: **00–14, 15 PASS, 0 FAIL**. Source/output service selection remains DEVOBJ(BCPLM3)+DEVOBJ(BCPLIO); production OBJ untouched. **Integrated regression 05–14 checkpoint ACCEPTED.** D3 remains open for formatter, streams, STOP/overflow and IOREPL validation.

### D3 integrated candidate regressions 15–24 PASS

Operator ran `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression 15 24 --show-output`; all ten tests 15–24 PASS, FAIL 0, SKIP 0. Coverage: 4-argument linkage, function return, nested calls, recursion, locals across calls, pointer return/store/reload, signed arithmetic, control flow, callable global dispatch. Cumulative candidate results **00–24: 25 PASS, 0 FAIL, 0 SKIP**. Runner-level evidence only; JES step summaries not supplied. D3 remains open pending focused I/O, formatting, stream, STOP and IOREPL validation. Production OBJ untouched.

### D3 integrated candidate regressions 25–34 PASS

Operator repeated 15–24 (10 PASS) and executed `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression 25 34 --show-output`: all ten cases 25–34 PASS, FAIL 0, SKIP 0. Includes separately compiled BCPL/native modules, GETVEC/FREEVEC and allocator error paths, dynamic vectors/pointers, caller base after return, VALOF/RESULTIS. Cumulative candidate sequence **00–34: 35 PASS, 0 FAIL, 0 SKIP**. Console runner summary only; underlying JES summaries remain in local logs. Gate D/D3 open. Production OBJ untouched.

### D3 full installed-candidate native regression panel PASS — 00–123

Operator ran `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 tools/run-native-regression --show-output` against D3 integrated DEVOBJ(BCPLM3)+DEVOBJ(BCPLIO) candidate. Reported **NATIVE REGRESSION 00..123 (124 tests); PASS 123; FAIL 0; SKIP 1; TOTAL 124**. Only skip was **083-instrumented-storage-reclamation**, explicitly source-only instrumentation unavailable in installed-PDS mode. Tests cover basic startup/calls, external objects, allocation, stack overflow, WRITEF and BLIB formatting, FINISH/STOP, dual-output streams, overflow boundaries, input lifecycle, saveareas, etc. This is operator-supplied full-panel runner evidence, not independent step-by-step JES audit. **D3 full native regression panel ACCEPTED**, with no failures among runnable cases. Do not construe as final Gate D closure: directly verify new private IOREPL semantics and intended BCPLMAIN diagnostic/overflow paths before final acceptance. Production OBJ remains untouched.

### D3 IOREPL direct behavioral probe prepared — MVS execution pending

Added `asm/bcplio-replacement-probe.asm` and `jcl/bcplio-replacement-probe.jcl` (PDS members SOURCE(BCRPPRB), JCL(BCRPPRB)). Probe standalone DEVOBJ(BCPLIO) assembles via IFOX, links via IEWL, GO with SYSPRINT and BCPALT. It buffers `ALT INTACT` on alternate, uses IODIAG to buffer `OLD PRIMARY MUST NOT APPEAR` on primary while alternate is selected, verifies IOREPL length 133 returns R15=8, then replaces primary with `STACK OVERFLOW` via IOREPL and expects R15=0; verifies IOSTAT=0 and output handle reflects preserved alternate selection; IOFIN must flush both. Expected visible record text: `STACK OVERFLOW`, `ALT INTACT`; old primary diagnostic must **not** be present. Expected ASMPROB/LKED/GO RC=0000. No MVS execution yet; do not close D3. Production OBJ untouched.

### D3 IOREPL standalone probe execution PASS — JOB 1793

Operator staged SOURCE(BCRPPRB) JOB 1789 and JCL(BCRPPRB) JOB 1790; launcher JOB 1792, payload **JOB 1793**. ASMPROB IFOX00 RC=0000, zero flagged statements; LKED IEWL RC=0000; GO RC=0000; JOB SUCCESS. This accepts the probe's internal behavioral assertions (IOREPL invalid length 133 returns 8, valid replacement returns 0, IOSTAT 0, alternate selection preserved), and confirms successful IOFIN. **Output text inspection still pending:** expected `STACK OVERFLOW` and `ALT INTACT`, absent `OLD PRIMARY MUST NOT APPEAR`. Integrated BCPLMAIN STKOVFL->IOREPL path is not yet directly asserted by this independent probe. D3/Gate D open; production OBJ untouched.

### D3 IOREPL GO record inspection ACCEPTED — JOB 1793

Operator inspected `tools/dump-report-for-job 1793`: assembler listing lines 179/278–282 echo all source literals, but actual emitted GO records are **line 408 `STACK OVERFLOW`** and **line 410 `ALT INTACT`**. The superseded `OLD PRIMARY MUST NOT APPEAR` does not appear as an emitted GO record (its listing occurrence at line 278 is not output). With JOB 1793 ASMPROB/LKED/GO RC=0000, **standalone IOREPL state-and-record checkpoint ACCEPTED**. The next outstanding verification is integrated BCPLMAIN STKOVFL-to-IOREPL handling; do not conflate standalone with integrated coverage. Production OBJ untouched.

### D3 integrated STKOVFL diagnostic acceptance — JOB 1648

Operator inspected retained full-panel candidate run `workarea/native-regression/52-controlled-stack-overflow/job-report.txt`: JES **JOB 1648 RG052R** ASMAP IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000 (report lines 5–12), and an actual `STACK OVERFLOW` output record at report line 350. This job was run under `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1`, selecting DEVOBJ(BCPLM3)+DEVOBJ(BCPLIO). Coupled with independent IOREPL probe JOB 1793 (primary replacement and alternate preservation), this **ACCEPTS D3 integrated STKOVFL diagnostic + legacy FINIMPL RC=0 evidence**, not STOP(12) for stack overflow. Native full panel already 123 PASS/0 FAIL/1 expected SKIP. D3 *output/lifecycle diagnostic validation* has met its focused evidence threshold. **Gate D remains open** under original plan because input handlers, input EODAD/DCBs, PARM and remaining stream-state ownership still reside within BCPLMAIN; D4/D5 and final extraction decision must account for this explicitly. Production OBJ untouched.

## D4 first slice — transfer EXEC PARM pointer ownership (candidate only)

D3 runtime/output/lifecycle accepted on 123 PASS / 0 FAIL / 1 expected SKIP plus JOB 1793 IOREPL and JOB 1648 integrated STKOVFL; **do not change accepted D3 DEVOBJ(BCPLM3)**. Original Gate D scope also includes BCPIN/BCPINB input and EXEC PARM stream ownership. D4 begins with a deliberately narrow ownership seam, not a premature wholesale relocation of QSAM EODAD/DCBs.

Inventory: D3 BCPLIO(IOINIT) already stores incoming MVS PARM-list R1 in its private `IOPARM` field. D3 BCPLMAIN also stores the same R1 in its local `PARMLIST` and PARMENT reads that duplicate. New BCPLIO private native R14 entry `IOPMGET` returns its captured pointer in R15; R10 becomes private BCPLIO base; R0–R9/R11–R14 retained. New **separate** `asm/bcplmain-d4-candidate.asm` modifies only PARMENT to call IOPMGET and restore BCPLMAIN R10; all input stream state and existing original startup remain in BCPLMAIN for now. This removes PARMENT's dependence on BCPLMAIN's duplicate PARMLIST without silently moving the QSAM input engine. The duplicate startup storage remains for IOINIT and compatibility until an independently tested later slice.

Candidate assembly routes: `asm/bcplio.asm` to DEVOBJ(BCPLIO) using existing BLDDEVI; **new** source member SOURCE(BCPLM4), job `BLDD4MN`, target DEVOBJ(BCPLM4); independent link job `D4LINK` includes BCPLM4 + BCPLIO + other DEVOBJ runtime objects. Regression generator now allows explicit `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM4` only with candidate mode and DEVOBJ, retaining BCPLM3 as default. **No MVS assembly/link/GO evidence yet.** Recommend first rebuild BCPLIO and BCPLM4; inspect D4LINK map/XREF for IOPMGET then run 00 and 108 (FINDPARM) against BCPLM4; ultimately run complete panel. No writes to production HERC02.BCPL.OBJ. D3 candidate source and DEVOBJ(BCPLM3) untouched.

Remaining D4 work: independently relocate BCPIN and BCPINB DCB/EODAD pairs, input stream handle selection, RDCH/UNRDCH/ENDREAD state, and PARM pseudo-stream; remove BCPLMAIN duplicate storage only after validated input ownership. Gate D **open**.

### D4 first PARM pointer ownership slice ACCEPTED — JOBS 1797, 1802, 1806

Operator installed revised BCPLIO SOURCE via JOB 1794 and BLDDEVI payload **1797** (ASMIO IFOX00 RC=0000, PUTIO RC=0000, zero flagged statements). Installed BCPLM4 SOURCE JOB 1798 and BLDD4MN JCL JOB 1799, payload **1802** (ASMMMAIN IFOX00 RC=0000, PUTMAIN RC=0000, zero flagged statements). D4LINK JCL JOB 1803, IEWL payload **1806** (LKED RC=0000). Explicit DEVOBJ BCPLM4 candidate regressions **00 PASS** and **108 FINDPARM PASS** (both 1 PASS/0 FAIL). **D4 first-slice assemble/link/functional checkpoint ACCEPTED**, subject to confirming IOPMGET's BCPLIO provider in IEWL MAP/XREF. D4 still open for full input state/DCB/EODAD migration and full candidate panel; DEVOBJ(BCPLM3) and production OBJ not intentionally changed.

### D4 first-slice full-panel acceptance — JOB 1806 XREF and 123/0/1

Operator inspected JOB 1806 IEWL map: BCPLMAIN from DEVOBJ(BCPLM4) origin X'000000' length X'173C'; BCPLIO origin X'001740' length X'08B4'; IOPMGET exported by BCPLIO at X'001C4A', BCPLMAIN external reference to IOPMGET resolved to BCPLIO (map XREF line 129); all shown INCLUDE directives IEW0000, no unresolved diagnostics. Operator then ran entire `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM4 tools/run-native-regression --show-output`: **00–123, PASS 123, FAIL 0, SKIP 1, TOTAL 124**. Only skip regression 083 source-only storage-reclamation instrumentation. This **accepts D4 first-slice PARM-pointer ownership link and complete candidate native regression checkpoint**. Input DCBs, EODAD, state machines, selected handles and PARM pseudo-stream remain BCPLMAIN-owned and Gate D stays open. Production OBJ untouched.

## D5 full input-service ownership extraction candidate — SOURCE COMMITTED, MVS UNTESTED

Building upon accepted BCPLM4 full-panel baseline (123 PASS/0 FAIL/1 expected SKIP), moved BCPL input service logic into the already independent `asm/bcplio.asm` CSECT. D5 is the next implementation *portion* of existing Gate D, not a new milestone.

- BCPLIO exports BCPL-facing `IOFINDIN` (G42), `IOINP` (G16), `IOSELIN` (G11), `IOPARMST` (G39), `IORDCH` (G13), `IOUNRD` (G15), and `IOENDRD` (G46). All use the original BCPL R6/R7 calling convention and restore R4 from the BCPL frame.
- Entire BCPIN/BCPINB QSAM input DCB, buffers and stream state, EODAD entry handlers, RDCH/UNRDCH/ENDREAD control logic, and EXEC PARM pseudo-stream state relocated to BCPLIO. IOPARM remains BCPLIO's private IOINIT-captured original MVS parameter pointer. Input handlers retain existing static singleton/nonreentrant behavior. G mappings now resolve to external linker addresses.
- BCPLIO IOFIN closes lazily opened BCPIN/BCPINB before clearing IOPARM; BCPLMAIN no longer closes or directly accesses input DCBs. I/O cleanup precedes RELMEM as before.
- New assembler entry wrapper saves incoming BCPLMAIN R10 to private IINBASE, establishes BCPLIO-local USING R10, and restores caller R10 before R6 return. Previous use of R10 as internal input scratch changed to R3; full-register save/restore paths must validate generated constant-register preservation. Input save/result cells `IINSAVE`/`IINRESULT` are distinct from output module internals. **This is an implementation hypothesis requiring assembly/link/execution evidence, not accepted behavior.**
- `asm/bcplmain-d5-candidate.asm` is a separate D5 candidate with the relocated routines/static input state removed. Accepted D4 BCPLM4 source and installed DEVOBJ(BCPLM4) are not intentionally changed. D5 source is staged as SOURCE(BCPLM5) to DEVOBJ(BCPLM5) with resident `BLDD5MN` JCL. `D5LINK` link deck references DEVOBJ(BCPLM5)+BCPLIO+other DEVOBJ members. Regression tooling accepts explicit `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM5` but leaves D3 as default and requires DEVOBJ opt-in. Production OBJ never a target.
- **MVS tests pending:** rebuild DEVOBJ(BCPLIO) from current source, assemble DEVOBJ(BCPLM5); inspect IFOX diagnostics and IEWL MAP/XREF (no unresolved); run native regressions 00, 094–100, 104, 107–108, 117–118 and 119; then full 124-case panel, expected 123 PASS/0 FAIL/1 source-only instrumentation skip. Any failure requires stopping and diagnosing before accepting D5. No runtime verification claimed by repository commits.

**Do not close Gate D or promote D5 to production pending MVS evidence.**

### D5 first build — BCPLIO assembly failure JOB 2060; BCPLM5 PASS JOB 2065

Operator staged revised SOURCE(BCPLIO) JOB 2057 and ran BLDDEVI payload **JOB 2060**: ASMIO IFOX00 **RC=0008**, highest severity 8; PUTIO bypassed. **Do not claim new BCPLIO installed**: existing DEVOBJ(BCPLIO) remains previous D4 version. Independently, SOURCE(BCPLM5) staged JOB 2061, BLDD5MN staged JOB 2062, payload **JOB 2065** ASMMMAIN RC=0000, PUTMAIN RC=0000, zero flags; DEVOBJ(BCPLM5) installed. D5 link/regression intentionally **blocked pending exact assembler diagnostics from JOB 2060**; root cause not established from summary alone. Production OBJ untouched.

### D5 JOB 2060 IFOX diagnostics: partial source correction, retest pending

Operator extracted exact IFOX error table: **IFO236** illegal character in expression statements 558,560,702,706,734,738,790,794 (8); **IFO209** unresolved base/displacement statements 888,890 (2); **IFO016** invalid name field statement 989 (1); assembler RC=0008. Static source review found **9-character field name `IINRESULT`**, illegal under 8-character IFOX labels; all usages renamed `IINRES` (commit 5ed9f839). Review also identified missing BCPLMAIN R10 restoration at IOSELIN and IOUNRD returns; added returns and preserved R3 temporary in IOUNRD (commit 1b9ad858). **IFO209 precise operand/cause remains to be located in assembler listing**; no claim all errors are resolved. Retest BCPLIO assembly with updated source and inspect the error table; D5 linkage/regression still blocked. DEVOBJ(BCPLM5) build JOB 2065 accepted; production OBJ untouched.
