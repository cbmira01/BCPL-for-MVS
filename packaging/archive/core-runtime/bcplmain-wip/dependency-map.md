# BCPLMAIN dependency and state-ownership map

Status: **source audit, 2026-10-10**. This is an architectural inventory, not a proposed ABI change or an assembler refactoring. Source basis: `asm/bcplmain-wip.asm` and its byte-identical lexical fragments `00` through `30`; independent `asm/bcplbyte.asm`; current stream contract and runtime dependency audit. Guest evidence: **120/120** native regressions with `BCPLBYTE_OBJECT=1`. No executable change accompanies this document.

## Current translation units and build identity

- `asm/bcplmain-wip.asm` is the authoritative executable BCPLMAIN source; `asm/bcplmain-wip/{00-contract,10-bootstrap-and-system,20-streams-and-services,30-control-data-and-end}.asmfrag` are ordered text fragments of **one assembler translation unit**, not four CSECTs. `tools/checks/check-bcplmain-modules.py` guards exact reconstruction.
- `asm/bcplbyte.asm` contains independent `BCPLBYTE CSECT` with `ENTRY GETBYTE,PUTBYTE`; its **two exported routines** use only caller registers and storage reached through their arguments, not BCPLMAIN private static labels. The default monolith still contains original copies.
- `BCPLBYTE_OBJECT=1` transforms a disposable combined regression assembler source: declares `EXTRN GETBYTE,PUTBYTE`, uses relocatable `=A(...)` global installations, removes embedded bodies, and separately assembles/links BCPLBYTE. Existing native object tests use a third object. **All 120 passed.** This is not yet a persistent object PDS or an unconditional source-level split.
- `BCPLMAIN_MODULAR_SOURCE=1` independently substitutes checked reconstituted source, not independent CSECT assembly.

## Executable boundary and register contract

Compiled module entry saves MVS R14–R12, obtains `BCPLMAIN` from its entry prefix, and passes the generated module base in R15. BCPLMAIN establishes a private `MSVSAVE` chain on R13, decodes module bounds and global trailer, acquires its global/stack allocation, loads G and S, installs runtime globals, and enters G!1 START.

| Register / convention | Dependency to preserve |
|---|---|
| R0 | Permanent zero in generated BCPL execution; unsafe to clobber across service calls |
| R1–R3 | Generated absolute-base constants 4096/8192/12288 once START runs |
| R4 | Caller branch/base register; native entries typically reload `L 4,0(5)` on return |
| R5 | Current BCPL procedure workspace P, with saved caller linkage |
| R6 | BCPL linkage / return address, service returns commonly `BCR 15,6` |
| R7–R10 | Argument/result registers; R7 first argument/result; R8/R9 following arguments |
| R11 | Executable system-vector base S; return / FINISH / stack services via fixed offsets |
| R12 | Global-vector base G, indexed at byte offset `4*N` |
| R13 | MVS save-area chain and BCPLMAIN static `USING MSVSAVE,13` addressability |
| R14/R15 | Scratch and MVS linkage; R15 is workspace W in generated BCPL code |

These are **observed integration constraints**, not a comprehensive general-purpose register preservation ABI for new CSECTs. In particular, a routine lifted into another CSECT cannot automatically address BCPLMAIN-local static symbols through R13, R11 or literal-pool base assumptions.

## Service-to-state dependency matrix

Abbreviations: `M` = MSVSAVE-relative runtime static storage; `G` = shared global vector; `S` = system vector; `D` = MVS DCB/QSAM state. Labels here are **current assembler labels**, not promised public symbols. Ownership assessments describe actual present usage, not isolated module ownership.

| Service and entry labels | Calls / published entry | Key shared state and cross-service dependencies | MVS interface | Extraction status |
|---|---|---|---|---|
| Bootstrap, global merge, START (`BCPLMAIN`, `GINIT`, `GSCAN`, `GINST`, `GIDONE`) | MVS/compiled module entry; installs G!1 and native globals | `MSVSAVE MODBASE MODEND TRAILER DYNBASE DYNWORK DYNEND DYNLEN STKLIM GLOBCNT`, G and S, module trailer; must retain startup ordering | `GETMAIN EC`, QSAM `OPEN BCPOUT` | **Keep in BCPLMAIN**: central initializer and owner of runtime lifetime |
| System-vector dispatch (`SYSV`, `RETIMPL`, `CNTIMPL`, `STKIMPL`, `STKCIMP`) | S+0/+20/+60/+80; S+40 is FINISH | R11-based executable layout, P/W, R14 inline frame size, `STKLIM STKMSG`, termination branch; COUNT / STKCKCOUNT provisional | None for normal return/check; error exits touch termination | **Map before splitting**: executable displacement ABI must stay unchanged |
| Termination / STOP (`FINIMPL`, `STOPENT`, `FINEXIT`, `RELMEM`, `BADRETN`, etc.) | S+40; G!30; startup error branches | `STOPRC RELRET VECLIST DYNBASE DYNLEN OUTPOS OUTBUF OUT2POS OUT2OPEN INOPEN IN2OPEN`; owns closure and teardown ordering; shared input/output state | QSAM `PUT/CLOSE`; `FREEMAIN R` | **Keep coordinated in BCPLMAIN** until ownership/exit protocol formalized |
| Word-vector allocation (`GETVEC`, `FREEVEC`, `RELMEM`) | G!87 / G!88; startup and exit invoke reclaim | `VECLIST GVRMAX GVRLEN GVRADDR GVRSAVE GVRPSAVE GVRLSAVE GVRWSAVE FVRSAVE FVPSAVE FVLSAVE FVWSAVE`; per-block three-word records; must interoperate with exit traversal | `GETMAIN EC`, `FREEMAIN R` | **Stateful candidate**, only after shared allocator control-block and reentrancy contract defined |
| APTOVEC (`APTOVEC`, `APMAXN`) | G!40 | R5/R15 frame convention, R7 procedure R8 length; `STKLIM`; calls BCPL function through R4/R6; stack check/overflow | No direct allocation in current implementation | **Medium-risk candidate**: few private symbols but sensitive to stack ABI |
| Byte primitives (`GETBYTE`, `PUTBYTE`) | G!85/G!86 via standalone `BCPLBYTE` | R7 BCPL word pointer, R8 byte index, R9 stored byte; restore caller R4 via P; no private static state | None | **Extracted / 120-test validated** |
| Input discovery/control (`FINDINP`, `PARMENT`, `INPENT`, `SELINP`, `ENDRDENT`) | G!42, G!39, G!16, G!11, G!46 | `INCTRL IN2CTRL INCURR INOPEN IN2OPEN`; per-input state and `IOSAVE IORESULT`; close/reset paths | QSAM `OPEN/CLOSE` for `BCPIN/BCPIN2` | **High coupling**: split only with explicit stream-owned state |
| Input characters (`RDCHENT`, `UNRDCHEN`, `INATEND`, `IN2ATEND`) | G!13/G!15; DCB EODAD branch targets | `INBUF IN2BUF INPOS IN2POS INRECLEN IN2LEN INNL IN2NL INEOF IN2EOF INPUSH IN2PUSH INLAST IN2LAST INSEEN IN2SEEN INENDVAL IOSAVE IORESULT`; selected handle | QSAM `GET`, EODAD | **High coupling** with input control and DCB placement |
| Output discovery/control (`FINDOUT`, `OUTENT`, `SELOUT`, `ENDWENT`, `WRAPENT`) | G!41/G!17/G!12/G!47/G!33 | `OUT1CTL OUT2CTL OUTCURR OUTRES OUT2OPEN OUTPOS OUT2POS OUTBUF OUT2BUF OUTSVREG`; FINISH flush state | QSAM `OPEN/PUT/CLOSE` | **High coupling** with WRCH, termination and DCB state |
| Output characters (`WRCH`, `WROUT1`, `WROUT2`) | G!14, shared G!76 formatting and G!150 debug | `OUTCURR OUTPOS OUT2POS OUTBUF OUT2BUF OUTMAX OUTLF OUTSVREG`; may enter `STOPENT` on overflow | QSAM `PUT` | **High coupling**: same output ownership as control and exit |
| Bootstrap formatted output (`WRITEST` and `WF*` helpers) | Fallback G!76 only if BLIB did not install its export | `WFREGSV WFARGS WFARGIX WFWIDTH WFSIGN WFREM WFFMTP WFDECPK WFDECZN` etc.; writes `OUTPOS/OUTBUF` directly | Output eventually through FINISH/WRCH buffering | **Do not crystallize**: BLIB should own G!76 in production; bootstrap fallback is provisional |
| Diagnostic integer output (`DEBUGINT`, `DBG*`) | G!150 | `DECPACK DECZON OUTPOS OUTBUF`; shared output record state | Output through QSAM during exit | **Low functional priority**, output-state dependent; test helper rather than production boundary |

## Static data ownership: present versus target

1. **Bootstrap core** — `MSVSAVE`, module/trailer pointers, global-vector/stack allocation addresses, and startup constants. Current owner BCPLMAIN; target owner BCPLMAIN core, with explicit exports or context pointer only if required by others.
2. **Allocator** — `VECLIST`, allocation control fields and saved registers. Currently shared between GETVEC/FREEVEC and RELMEM. Target BCPLMEM *after* termination can call a defined teardown entry; otherwise keep together.
3. **Output** — `BCPOUT/BCPOUT2`, `OUTBUF/OUT2BUF`, positions, selected output, open flags, saved register block. Currently shared among startup, WRCH/selection, WRITEF/DEBUGINT and termination. Target one BCPLIO owner with defined `init/flush/close` interface, not raw cross-CSECT references.
4. **Input** — `BCPIN/BCPIN2`, two record buffers, cursor/EOF/pushback flags, selected handle, shared `IOSAVE`. Target BCPLIO owner; note `IOSAVE` is **one shared static register-save image** (non-reentrant).
5. **Formatting/diagnostics** — `WF*` and `DEC*` globals and direct `OUTBUF` writes. Their presence complicates extracting output ownership and highlights the temporary fallback nature of `WRITEST`.
6. **System/stack** — `SYSV` is executable, **not** a pointer table; `STKLIM/STKMSG` and frame conventions are accessed by different sections. Retain S offset layout even if bodies move.

All DCBs, buffers, and saved-register images are currently **static, singleton, not reentrant**. No independent per-invocation or per-task context layout has yet been established. Merely adding `EXTRN` to these labels does not solve state ownership or base-register addressing.

## Directed dependency edges and extraction implications

- **BCPLMAIN startup -> every global-vector service**: publishes callable addresses; output setup happens before START; storage setup before global installation.
- **Generated BCPL -> G and S**: existing G slots and S executable offsets are ABI and must not move.
- **BLIB G!76 -> output implementation**: formatted output may invoke character/stream functions; fallback WRITEST instead directly edits runtime output state. These are *different ownership paths*.
- **Input services -> BCPIN/BCPINB static descriptors -> EODAD branch labels**: a DCB move must relocate EODAD targets and controls as a coherent unit.
- **Output services -> BCPOUT/BCPOUT2 state -> FINISH/STOP**: both selected buffers must be drained and all open DCBs closed on exit, including error paths.
- **GETVEC/FREEVEC -> VECLIST <- RELMEM**: detached allocation records are freed before the main global/stack allocation; cannot independently move allocator data without changing the exit interface.
- **APTOVEC/stack-check -> STKLIM and generated P/W discipline**: extraction touches internal runtime control transfers, not only exported G slots.
- **BCPLBYTE -> only caller-supplied registers/storage**: no incoming runtime-private symbol edges; reason it was the first safe independent object.

## MVS interface inventory

| Macro or service | Current callers / ownership implications |
|---|---|
| `GETMAIN EC` | Startup combined global/stack allocation; GETVEC allocation. Separate failure and ownership lifetimes |
| `FREEMAIN R` | FREEVEC and RELMEM; teardown ordering is tested and must remain |
| `OPEN` / `CLOSE` | Startup, FINDINPUT/FINDOUTPUT, ENDREAD/ENDWRITE, FINISH/STOP; DCB/control ownership shared |
| `GET` + `EODAD` | RDCH input stream bodies and `BCPIN/BCPIN2` DCBs |
| `PUT` | WRCH output paths and finish/flush paths |
| MVS caller linkage / save area | BCPLMAIN entry and termination; do not infer independent standard MVS ABI for G-called primitives |

## Extraction ranking and gates

| Candidate | Risk | Prerequisite | Decision |
|---|---|---|---|
| BCPLBYTE | Low | External relocation and BCPL caller register ABI | **Done; maintain source-driven object build** |
| APTOVEC | Medium | Explicit stack-limit and overflow-path interface; preserve S/P/W invariants | Good next **analysis** candidate, not automatic move |
| GETVEC/FREEVEC | Medium–high | Own `VECLIST` and define RELMEM -> allocator-teardown call | Possible BCPLMEM boundary |
| System-vector helpers | Medium–high | Preserve S offsets, R11 addressability, error exits and inline operands | Delay until callers/control branches characterized |
| Stream input/output | High | One stream-control owner, context interface, DCB and EODAD relocation, exit cleanup API | Map/control-block redesign before extraction |
| WRITEST and DEBUGINT | High architectural ambiguity | Decide BLIB ownership and shared output append interface | Avoid making them permanent BCPLMAIN public members |
| BCPLMAIN startup, loader and abnormal recovery | High/unknown | Native compiler resident-image requirements and historical contract recovery | Keep integrated / defer |

## Recommended next work (without executable changes now)

**Close this map as a baseline**, then conduct a narrow **APTOVEC and allocator/termination boundary review**, producing concrete proposed callable interfaces and state-transfer rules *before* authoring another independent assembler CSECT. In parallel, use the native compiler dependency audit to prioritize work on the compiler-sized resident image, DATE/FINDPARM, and stream semantics. Do **not** create BCPLMAIN object PDS members merely to give names to currently coupled code.

### Verification and limits

This map was produced by inspection of current canonical assembler fragments and the repository's dated dependency/stream documents. It identifies assembler labels and direct shared-state use; it is **not** a mechanically complete call graph, control-flow proof, formal clobber analysis, reentrancy certification, or proof that the current implementation matches the lost historical runtime. Some early comments in march documents predate later regressions; use the current assembler and latest 120/120 guest run as the implementation baseline. Preserve all existing checks in `tools/checks/` and the full 120-test gate on any future executable extraction.
