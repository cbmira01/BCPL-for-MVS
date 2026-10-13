# BCPL for MVS — Runtime Contract Specification v1.0

**Status:** M1.9 Gate F acceptance candidate, 13 October 2026.  
**Scope:** Five-component reconstructed System/370 BCPL runtime linked with native BCPL applications under MVS 3.8J TK5.  
**Normative meaning:** This specification describes *current demonstrated implementation*, not a complete reconstruction of historical Cambridge BCPLMAIN or a guarantee that every LIBHDR entry is implemented.

## 1. Source, execution and evidence authority

Git sources are authoritative: `asm/bcplmain.asm`, `asm/bcplmem.asm`, `asm/bcplbyte.asm`, `asm/bcplapt.asm`, and the mechanically demoted compiler input from `richards-bcpltape/bcplib/bcpl/blib`. Historical global names and numbers come from `richards-bcpltape/sys3/bcpl/libhdr`, selected by `config/dspal.yaml` as SOURCE(LIBHDR).

`HERC02.BCPL.DEVOBJ` is the candidate independently assembled five-member library. `HERC02.BCPL.OBJ` is the stable ordinary-application library. No implicit promotion is allowed. The M1.8 acceptance execution of the DEVOBJ regression panel was **123 PASS, 0 FAIL, 1 expected SKIP** among tests 000–123 (124 total). This is aggregate evidence; individual paths below have narrower proof.

**Evidence levels:** **S** source-verified implementation; **T** targeted executable regression asserted the named behavior; **A** aggregate M1.8 DEVOBJ panel accepted; **U** unsupported or unverified. **S** does not imply **T** and **A** is not a substitute for a fault-path test.

## 2. Runtime architecture and linkage

| Component | Linker-visible interfaces | Current responsibility |
| --- | --- | --- |
| BCPLMAIN | CSECT BCPLMAIN, ENTRY STKOVFL | MVS startup/return, global registration, stack initialization/check, stream I/O, termination |
| BCPLMEM | GETVEC, FREEVEC, MEMDRAIN, MEMBIND, MEMSTAT | Dynamic BCPL vectors, tracking and teardown |
| BCPLBYTE | GETBYTE, PUTBYTE | BCPL word-pointer to byte addressing |
| BCPLAPT | APTOVEC, APLIMIT | Separate temporary-vector implementation; see integration warning |
| BLIB | Compiler-generated global registration trailer | Historical BCPL library procedure implementations |

Compiled application and BLIB modules carry pairs of byte offsets into the BCPL global vector and relocated procedure addresses. BCPLMAIN reads the application trailer, imports the separate BLIB trailer, and installs native globals explicitly. The existence of a top-level procedure or LIBHDR name alone does **not** prove a particular compiled deck exports it. The historical BLIB source yields 21 LIBHDR-numbered top-level candidate exports and one unmapped helper, PRINTWIDTH; byte-level verification of all actual trailer pairs has not been made.

Normal native BCPL procedure linkage uses R5 as the current frame, R6 as return address, R7–R9 for arguments/results and R4 restored from 0(R5). Entry-specific assembler linkage is not interchangeable with this BCPL convention; private MEMBIND, MEMDRAIN and MEMSTAT use R14 return and their documented native registers. The generated-code system vector is based on R11.

### Selected public globals

| Global(s) | Service/data | Support classification |
| --- | --- | --- |
| G1 | START | Registered by application module |
| G6 | SAVEAREA | Published provisional MVS save-area-compatible word pointer |
| G11–17 | SELECTINPUT, SELECTOUTPUT, RDCH, WRCH, UNRDCH, INPUT, OUTPUT | Installed native stream services |
| G30, G33 | STOP, WRAPOUTPUT | Installed |
| G39–42 | FINDPARM, APTOVEC, FINDOUTPUT, FINDINPUT | Installed; G40 currently selects *internal BCPLMAIN APTOVEC* |
| G46–47 | ENDREAD, ENDWRITE | Installed |
| G52–55 | LOADPOINT, ENDPOINT, STACKBASE, STACKEND | Published word-address boundaries |
| G56 | STACKHWM | Historical BLIB; targeted limited test |
| G58–59 | INPROGRAM, VALIDPOINTER | Historical BLIB; selected test cases |
| G60–77 | Selected string, numeric and format routines | BLIB source/trailer; see LIBHDR and audit for exact named entries |
| G78 | MAPSTORE | BLIB routine; full behavior unverified |
| G85–86 | GETBYTE, PUTBYTE | BCPLBYTE |
| G87–88 | GETVEC, FREEVEC | BCPLMEM |
| G150 | DEBUGINT | Provisional project-specific native extension; not named in historical LIBHDR |

A global present in LIBHDR but omitted above is **not necessarily supported**. In particular LEVEL G31, FINDLOG G36 and WRITETOLOG G37 have no established standard native provider. G94 is assigned to both OPENBLOCKFILE and UPDATEBLOCKFILE in the tracked historical header; do not silently correct it.

## 3. Main storage and stack

BCPLMAIN obtains a single **68,592-byte** GETMAIN block comprising **700 global-vector words (2,800 bytes)**, **16,384 working-stack words (65,536 bytes)**, and **256 bytes reserved clearance**. The global vector base is used for global registration; DYNWORK starts the painted stack, STKLIM is DYNWORK+65,536, and DYNEND is STKLIM+256.

G54 STACKBASE is DYNWORK>>2 and G55 STACKEND is DYNEND>>2. Both are BCPL word addresses. **G55 is the allocated extent end, not the safe working-stack limit.** Checked-entry S.STKCK at R11+60 validates generated inline frame-size metadata, then compares next-frame end with STKLIM. Malformed frame metadata exits with R15=36 outside the usual FINEXIT cleanup path.

BCPLMAIN paints 8,192 EVENSTACK/ODDSTACK marker pairs into the 64-KiB working region and stores end metadata in the clearance. Historical BLIB G56 STACKHWM scans backward to return a **word address** or a sentinel (0 OVERFLOW, 1 UNSET). Regression 120 establishes an in-range result, **not** exact high-water accuracy across all workloads or marker corruption. S.COUNT (R11+20) and S.STKCKCOUNT (+80) are stubs which skip inline operands; do not advertise call counts.

G40 currently calls **BCPLMAIN's in-module APTOVEC**, which invokes a BCPL function with a temporary N+1-word vector and the size argument, and enforces STKLIM. Independent BCPLAPT is included as an object but **is not selected** by canonical G40. Its exported APLIMIT is initialized to zero in its source and is initialized correctly only by a separate test-local externalization transformation. This is B-APT-01, a deferred integration gap.

## 4. Dynamic BCPL vectors

BCPLMEM GETVEC(N) accepts N in R7; negative or excessive N and MVS GETMAIN failure return R7=0. An accepted request allocates **4(N+1)+12 bytes** (12-byte private descriptor followed by N+1 words). The result is a BCPL word pointer, the allocated byte pointer+12 divided by four. The source limit is N ≤ 4,194,299.

Each descriptor retains its word pointer, byte length and next descriptor byte pointer. FREEVEC(V) matches exact returned word pointers, unlinks and FREEMAINs known allocations; zero or unknown pointers are no-ops. This allocator is static and **not reentrant**. MEMBIND installs the G6!48 published descriptor-list-head address; MEMDRAIN frees remaining allocations, updates the head and counters, and runs on normal FINISH/STOP termination.

MEMSTAT is **private native assembler ABI**, not a callable BCPL global: R1 points to a 16-byte writable area containing, in order, current live-vector count, peak live-vector count, currently allocated byte count and peak byte count. Bytes include 12-byte private headers. The quiescent-singleton and R10-clobber assumptions apply. The values do **not** represent all MVS process storage. Regression 082 demonstrates normal completion with outstanding vectors, not measured FREEMAIN quantities.

## 5. Character streams and record I/O

| BCPL interface | Current MVS behavior |
| --- | --- |
| FINDINPUT | Recognizes BCPIN and BCPINB fixed 80-byte QSAM DDs; lazy OPEN; unknown name returns 0 |
| RDCH | Returns EBCDIC input characters, a synthetic newline (10) after each record, and -1 at EOF |
| UNRDCH | Per-source one-character replay of most recent read result |
| FINDPARM | Separate stream of up to 100 MVS EXEC PARM bytes, then newline and EOF |
| SELECTINPUT / INPUT | Selects recognized input handle / reports current handle |
| FINDOUTPUT | SYSPRINT or BCPALT; BCPALT is lazily OPENed |
| WRCH | Writes into selected 132-byte record; newline triggers QSAM PUT |
| SELECTOUTPUT / OUTPUT | Selects recognized output handle / reports current handle |
| WRAPOUTPUT | Flushes alternate BCPALT record |
| ENDREAD / ENDWRITE | Reset/close selected input or alternate output; alternate pending bytes flushed on ENDWRITE |

Fixed input-record padding spaces are **trimmed**; interior spaces survive. Thus the input interface is not binary-faithful for arbitrary FB80 data. A non-newline character written to a full 132-byte output buffer enters STOP(12), rather than extending the record. The historical LIBHDR's many record, terminal, library and block-file services are not thereby provided.

## 6. Termination and MVS completion status

| Condition | Current completion | Explicit cleanup path |
| --- | --- | --- |
| FINISH (S.FIN) | 0 | FINEXIT flush/close, MEMDRAIN, MEMBIND(0), main FREEMAIN |
| STOP(N) | N in R15 | Same FINEXIT cleanup |
| Output buffer capacity failure | 12 via STOP | Same FINEXIT cleanup |
| Stack overflow (STKOVFL) | **0** with `STACK OVERFLOW` message on SYSPRINT | Via FINIMPL/FINEXIT, but previous default buffered output is overwritten |
| Oversize exported global | 16 | RELMEM; not FINEXIT |
| Missing START | 20 | RELMEM; not FINEXIT |
| Initial GETMAIN failure | 24 | Direct MVS return; no block acquired |
| Invalid frame metadata | 36 | Direct return bypassing normal stream and explicit memory cleanup |
| Unexpected START return | 36 | RELMEM; not FINEXIT |

These codes are source-derived unless specifically covered by a focused test. A normal RC=0 **does not rule out stack overflow**. MVS address-space termination may release remaining task resources but does not establish application-level buffer flushing on early-return branches.

## 7. Observability contract

| Mechanism | Caller/trigger | Destination/meaning | Verification boundary |
| --- | --- | --- | --- |
| STACKHWM G56 | BCPL program | Word-address high-water or 0/1 sentinels | Regression 120 in-range result; exact precision unverified |
| STACKBASE/STACKEND G54/G55 | BCPL program | Published allocated extent, **not** STKLIM | Source verified |
| STKOVFL | Checked-entry/temporary-vector limit failure | `STACK OVERFLOW` to SYSPRINT, RC=0 | Test 093 selected behavior; no automatic backtrace |
| DEBUGINT G150 | BCPL program (provisional) | Decimal digits appended to default SYSPRINT buffer | Source-verified call wiring; silent capacity drop, direct test not identified |
| MEMSTAT | Native assembler private caller only | Four counter fullwords at R1 target | No supported BCPL or operator exposure |
| G6!48 + VALIDPOINTER G59 | Application/BLIB | Allocator descriptor-list head and selective pointer predicate | Tests 121–123 in constrained cases; not a general heap-map contract |
| ABORT G3 / ERRORMESSAGE G5 | Historical BLIB entry | Formatting/postmortem; logging fallback may call unsupported globals | Not automatic MVS intercept; full call behavior unverified |
| BACKTRACE G4 | Historical BLIB entry | Frame dump requires LEVEL G31 | Standard provider unestablished; not supported diagnostic |
| MAPSTORE G78 | Historical BLIB entry | Stack/global/program/module reports | Full output unverified |
| USERPOSTMORTEM G79 | Optional application callback | Only conditionally invoked from ABORT | No automatic invocation contract |

An MVS operator observes selected application output in SYSPRINT/JES reports and step completion code, not automatically collected stack/heap/backtrace metrics. Historical BLIB procedure presence must not be equated with automatic fault interception.

## 8. Historical compatibility and accepted deviations

Implemented portions of LIBHDR numbering, BCPLBYTE byte primitives, BLIB formatting, global trailer registration and STACKHWM sentinel scheme resemble the surviving Cambridge contract. The 80/132-byte QSAM streams, main GETMAIN layout and BCPLMEM allocator are MVS adaptations. Historical block/library I/O, LEVEL, logging fallback, full ABORT-based postmortem, and call counters are omitted or not established. Separate BCPLAPT activation, nonzero overflow status, and general diagnostic exposure remain engineering gaps rather than requirements silently satisfied by M1.9.

## 9. Traceability and unresolved items

| Contract section | Source anchors | Focused evidence where present |
| --- | --- | --- |
| Global registration/link | BCPLMAIN GSCAN/GINST/BLIMP; LIBHDR; BLIB; build-dev-blib.jcl | 067–069, 075–081; full DEVOBJ panel |
| Storage, vectors | BCPLMAIN GETMAIN/RELMEM; BCPLMEM | 027–032, 082, 121–123 |
| Frames, APTOVEC | BCPLMAIN STKIMPL/APTOVEC; BCPLAPT; externalize-bcplapt.py | 048–052, 091–093 |
| Stack high-water | BCPLMAIN STKPAINT; BLIB STACKHWM | 120 |
| Input/output | BCPLMAIN FINDINP/RDCHENT/WRCH/FINDOUT/ENDWENT | Historical regressions 094–119; per-case assertion map not exhaustively reviewed |
| FINISH/STOP | BCPLMAIN FINIMPL/STOPENT/FINEXIT/RELMEM | M1.8 panel; 093 for overflow diagnostic |
| Diagnostics | BCPLMAIN DEBUGINT/STKOVFL; BCPLMEM MEMSTAT; BLIB ABORT/BACKTRACE/MAPSTORE | 093, 120–123; explicit gaps elsewhere |

**Open dispositions:** B-APT-01 separate object not active; B-STK-02 stale 16KB comment; B-STK-03 high-water exactness; B-MEM-01/D-OBS-01 private statistics; B-MEM-02 FREEMAIN accounting; C-EXIT-01/D-OBS-02 overflow RC=0; C-EXIT-02 uneven exceptional cleanup; C-TEST-01 incomplete per-test fixture matrix; D-OBS-03 DEBUGINT semantics; D-OBS-04 LEVEL/BACKTRACE; D-OBS-05 log fallback; D-OBS-06 MAPSTORE; D-OBS-07 USERPOSTMORTEM; complete binary BLIB trailer unresolved. These are **documented exclusions/deferred engineering decisions**, not accepted implementations.

## 10. Milestone acceptance boundaries

This versioned specification is the M1.9 audit deliverable. Acceptance means all five modules have a concrete source-grounded interface classification, diagnostic exposure is accurately distinguished from instrumentation, historical claims are limited to actual evidence, and unresolved items have dispositions. Acceptance **does not** certify historical runtime equivalence, trigger an MVS production library promotion, or authorize a new runtime implementation project.

For the full investigation, source citations, historical alternatives and individual gate decisions, see [M1.9 runtime audit](m1-9-runtime-contract-audit.md). For verified resident builds and suite baseline, see [M1.8 build acceptance](m1-8-reproducible-runtime.md).
