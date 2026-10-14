# M2.1 Gate C — Historical Runtime Compatibility

**Status: OPEN — 14 October 2026.** Gate B formally accepted and closed; DEVOBJ(BCPLM7) is the current M2.1 development candidate. No production object promotion.

## Objective

Identify **precisely which** surviving Cambridge compiler runtime contracts must be supported for a bounded native System/370 compiler integration step, without confusing the current INTCODE compiler with a native self-hosting compiler. This is a historical/source audit first, not authorization to implement every LIBHDR global.

## Executable baseline and distinction of stages

- The installed compiler **CAMBCOMP** still runs as INTCODE under **ICINT19**, per `native-compiler/mvs-resident-cambridge.md`. It generates native S/370 application code; it is **not** a native S/370 compiler load module.
- The approved D7 runtime DEVOBJ(BCPLM7) passed native application regressions 00–123 with **123 PASS, 0 FAIL, 1 expected SKIP (083)** after Gate B's stack overflow RC=12 correction; 052 and 093 both assert RC=0012.
- Application regression success does not establish compiler-driver or compiler-phase compatibility.

## Initial historical contract matrix

| Service / global | Concrete surviving compiler usage | Existing D7 native contract / evidence | Candidate status |
| --- | --- | --- | --- |
| G31 LEVEL and G32 LONGJUMP | `richards-bcpltape/bcplib/bcpl/syn`: FORMTREE saves `REC.P,REC.L := LEVEL(), L1`, nested readers save LEVEL and recovery labels, CAEREPORT synchronizes parser input and calls `LONGJUMP(REC.P, REC.L)`. | No G31/G32 native publisher identified in D7. Historical nonlocal transfer semantics, dynamic frame restoration and code-generator linkage must be established together; ordinary GOTO is not equivalent. | **Potential native SYN blocker**, particularly syntax-error recovery. No implementation yet. |
| G29 DATE | `richards-bcpltape/bcplib/bcpl/cg` CG370 creates module prefix using `LET D = DATE()`; it then emits `I!D` for I=0..2. | No D7 G29 provider established; return type is a pointer to at least three BCPL words, but their meanings/layout and storage lifetime remain unverified from the call alone. | **Potential native CG370 blocker** in exercised prefix generation. Avoid substituting date text or three invented values. |
| G41 FINDOUTPUT and G42 FINDINPUT | `richards-bcpltape/bcplib/bcpl/bcpl` driver requests SYSIN, SYSPRINT, OCODE, CODE, SYSGO. SYN opens nested GET source via FINDINPUT. | `asm/bcplio.asm` currently recognizes input BCPIN and BCPINB, and output SYSPRINT and BCPALT. Tested MVS adaptations differ from compiler DD naming. | **Concrete source-contract mismatch** if unmodified driver executes native. Requires stream role/DSN/record rules design before coding. |
| G39 FINDPARM and G11–17 stream/character procedures | Driver parses options and reads/outputs source; uses SELECTINPUT/SELECTOUTPUT, RDCH/UNRDCH, ENDREAD, ENDWRITE, WRAPOUTPUT. | Native BCPLIO publishes key services; regressions 084–119 establish selected behavior, but do not prove compiler's specific formats. | **Partially covered**; test compiler-specific workload before changes. |
| G40 APTOVEC, G85/86 bytes, G87/88 dynamic vectors | Driver uses APTOVEC workspace; phase code manipulates bytes/vectors. | Native candidate implementations exercised, 052/093 failure behavior tested. | **Implemented foundation**, real compiler workspace sizing untested. |
| Loader/segment operations | Driver declares `NEEDS "$LOAD$"`, may invoke LOADSEG/UNLOAD when OVERLAYING, LOADCODE for load-and-go. | No full corresponding native-loader contract proven. Overlay path depends on selected configuration and actual module exports. | **Conditional**; do not automatically require a general loader for the first native compiler component. |
| ABORT, MAPSTORE, logging and diagnostics | Driver has a local ABORT and optional MAPSTORE; logging fallback when SYSPRINT missing. | No justification for full historical postmortem subsystem from these references. | **Deferred**, except a demonstrated compiler-blocking path. |

## Source references and limits

1. `richards-bcpltape/sys3/bcpl/libhdr`: `DATE:29; STOP:30; LEVEL:31; LONGJUMP:32`, `FINDOUTPUT:41; FINDINPUT:42`; numbering alone does not establish native behavior.
2. `richards-bcpltape/bcplib/bcpl/syn`, around lines 70–110 and 195–265: actual nonlocal recovery call sites and saved LEVEL values.
3. `richards-bcpltape/bcplib/bcpl/cg`, around lines 55–79: DATE result dereferenced as three words and emitted into generated module prefix.
4. `richards-bcpltape/bcplib/bcpl/bcpl`: SECTION BCPL, NEEDS "$LOAD$", driver input/output names and conditional overlay paths.
5. `asm/bcplio.asm`, IOFINDIN and static DCB/name data: supported MVS stream aliases; no generic DDNAME resolution implied.
6. `native-compiler/mvs-resident-cambridge.md`: execution-stage boundary.
7. `packaging/m2-1-gate-a-contract-reconciliation.md` and `packaging/m2-1-gate-b-termination-failure.md`: accepted baseline and Gate B evidence.

**Important:** This is a call-site and native-publication crosswalk, not complete whole-program static analysis. In particular, lack of a detected G29/G31/G32 publisher in D7 must be resolved against potential BLIB/object providers and selected build variants before claiming absolute absence.

## Revised Gate C boundary — runtime completion only

**Owner direction (14 October 2026):** finish runtime compatibility, diagnostics, integration and acceptance **before** beginning the native compilation or execution of Cambridge compiler phases. The original execution-strategy section in the initial Gate C charter is therefore **superseded**. This gate assesses the runtime as an independently deliverable MVS development facility. Compiler source call sites are historical evidence for documenting unsupported facilities; they are **not** a directive to attempt a compiler component during M2.1.

## Runtime compatibility audit — release disposition

Evidence codes: **S** = verified by currently tracked source; **T** = directly exercised by named regression; **A** = covered by the full D7 00–123 panel at tested scope; **U** = no established provider/contract; **D** = deliberately deferred; **M** = intentional MVS implementation adaptation. These codes do not imply measured statement/branch coverage.

| Runtime contract | D7 disposition | Evidence and qualification |
| --- | --- | --- |
| MVS entry, global registration, START, linkage | **Implemented S/T/A** | D7 BCPLMAIN, generated application/BLIB global-registration trailers; tests 00–26, 037, 067–069 and independently assembled linkage. Not a claim about every BLIB trailer pair. |
| Procedure frames, recursion, stack checking | **Implemented S/T/A** | Tests 013–019, 048–052; malformed metadata exit has source-known RC=36 but is not a tested safe recovery. |
| Stack exhaustion | **Implemented S/T/A** | D7 STKOVFL emits STACK OVERFLOW and routes via STOPENT/FINEXIT with **MVS RC=12**; tests 052 and 093 assert RC=0012. Historical ABORT system code X'0D3' is not reconstructed. |
| FINISH and STOP(N) | **Implemented S/T/A** | D7 FINEXIT, IOFIN, RELMEM; tests 082, 084–089 and 119; STOP(N) is application-chosen and must not be described as a reserved runtime RC. |
| GETVEC/FREEVEC and cleanup | **Implemented S/T/A; M** | BCPLMEM independently owns descriptors and MEMDRAIN; 027–032, 039, 082, 122–123. Exhaustive invalid-pointer behavior, MVS GETMAIN exhaustion and quantitative FREEMAIN balance are not proven. |
| GETBYTE/PUTBYTE | **Implemented S/T/A** | Independent BCPLBYTE, tests 038 and 070–071 (BLIB string consumers). |
| APTOVEC | **Implemented S/T/A** | Independent BCPLAPT is installed at G40; tests 091–093. Prior M1.9 internal-G40 limitation is resolved; not a general historical stack-size guarantee. |
| Historical BLIB surface | **Partially implemented S/T/A** | Linked BLIB object; tests 053–081, 120–123 selected helper functionality. Complete byte-by-byte export mapping and full postmortem routine behavior unverified. |
| QSAM character/record streams | **Implemented subset S/T/A; M** | Independent BCPLIO with BCPIN, BCPINB FB80 and SYSPRINT, BCPALT FB132; tests 094–119. Padding trim, synthesized newline, limited aliases and 132-byte output capacity are intentional MVS-specific contract, not universal LIBHDR I/O. |
| PARM and output wrapping | **Implemented subset S/T/A; M** | BCPLIO memory PARM stream/WRAPOUTPUT; tests 108,109. Compiler-specific option syntax is outside runtime contract. |
| STACKBASE, STACKEND, STACKHWM | **Implemented limited S/T/A** | D7 initial stack publication and BLIB STACKHWM test 120. High-water exactness in pathological patterns unverified; G55 is allocated end, not STKLIM. |
| MEMSTAT | **Private S; deferred public D** | BCPLMEM native R1 four-fullword snapshot, not a public BCPL global. No universal memory-statistics requirement. |
| DEBUGINT and WRITEST | **Provisional S/T limited** | G150 is reconstruction-specific; WRITEST G76 fallback only if BLIB's G76 is not imported. Keep minimal programmer-oriented diagnostic surface. |
| Exceptional startup/frame error exits | **Source-described S; narrow U** | NOSTART RC20, GTOOBIG RC16, GNOCORE RC24, STKFORM/BADRETN RC36; do not falsely claim tested cleanup across corrupted-frame and pre-IOINIT paths. No automatic rewrite judged necessary from currently recorded evidence. |
| DATE G29 | **U/D** | Historical CG source dereferences a three-word result. Native D7 G29 service and exact data layout are not established. **Excluded from completed runtime subset** pending historical ABI recovery. |
| LEVEL G31 / LONGJUMP G32 | **U/D** | Historical SYN parser uses both for nonlocal recovery. No verified D7 native provider or trustworthy reconstructed frame-restoration contract. **Excluded**, not silently stubbed. |
| Full historical compiler DD names | **U/D/M** | Current native stream names do not include driver SYSIN, OCODE, CODE, SYSGO. Historical compiler integration will need a separate I/O contract decision, not unreviewed alias additions. |
| LOAD/UNLOAD/overlay and load-and-go | **U/D** | Historical driver uses NEEDS "$LOAD$" and conditional LOADSEG/UNLOAD/LOADCODE. General loader absent/unproven; omitted from runtime release. |
| Full ABORT, BACKTRACE, MAPSTORE, logging, block-file, terminal/window, FORTRAN bridges, TIME/DATE | **U/D except individually confirmed BLIB portions** | Historical LIBHDR names are not proof of executable native interfaces. Neither automatic postmortem nor corresponding OS hooks promised. |
| CALL COUNT and stack-check counts | **U/D** | Source-documented system-vector counter entries remain stubs; do not advertise counters. |
| Reentrancy and concurrency | **Not supported** | BCPLIO and BCPLMEM are stateful static singletons; accepted runtime is single-application-instance oriented. |

### Corrective action determination

**No further assembler code is justified by the evidence available in Gate C.** M2.0 resolved independence, Gate B fixed the demonstrated stack-overflow success RC, and the remaining genuine gaps either require missing historical ABI evidence or belong to compiler-stage-specific integration. Creating plausible but speculative G29/G31/G32 entries would degrade historical fidelity. Likewise, renaming BCPLIO DDs without proving source/record semantics would be an untested compatibility claim.

Runtime **compatibility audit is complete at the declared subset boundary**, not a claim of full Cambridge BCPLMAIN equivalence. Gate D should finalize programmer-facing diagnostics; Gate E should independently link/run representative applications; Gate F should publish the completion-code registry, versioned current contract and regression interface-coverage matrix. M2.1 closes after those gates, before any compiler phase is compiled natively.

## Gate C acceptance and closure criteria

- [x] Runtime completion (rather than native compiler-phase execution) established as Gate C scope.
- [x] Compared currently accepted D7 modules with M1.9 v1 and accepted M2.0/B changes.
- [x] Recorded implemented, limited, intentional MVS adaptations, unknown and deferred historical services.
- [x] Recorded source-grounded contracts for G29, G31/G32 and compiler DD-name mismatches without invented ABI.
- [x] Determined that no evidence-backed Gate C assembler correction is presently required.
- [x] Owner accepted the bounded runtime-only compatibility audit by directing progression to Gate D on 14 October 2026.

**Gate C ACCEPTED AND CLOSED — 14 October 2026.** Owner directed progression to Gate D; no code changes were required. Historical gaps remain explicitly unsupported/deferred.

## Explicit exclusions

No compiler-phase compilation, no native compiler driver integration, no arbitrary publication of historical globals, speculative DATE triple, full exception/postmortem facility, general-purpose MVS DD manager, comprehensive loader, replacement compiler/code generator, production OBJ promotion, or silent D6 substitution. The first native compiler component will be chosen in a later compiler-focused milestone, *after* runtime M2.1 closure.
