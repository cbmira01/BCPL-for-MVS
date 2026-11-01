# M2.0 Gate A — Runtime Architecture Baseline

**Status:** Gate A source inventory COMPLETE; accepted as documentation-only baseline, 13 October 2026. Gate B is ready for a separately scoped implementation. No runtime source, MVS objects, or regressions were changed or executed by this audit.

## Scope and authority

Read canonical `asm/bcplmain.asm` (2,129 lines), `asm/bcplmem.asm` (205 lines), `asm/bcplbyte.asm` (37 lines), `asm/bcplapt.asm` (42 lines), `packaging/runtime-contract-v1.md`, `packaging/m1-9-runtime-contract-audit.md`, `packaging/m2-0-runtime-modularity-architecture.md`, and `tools/checks/externalize-bcplapt.py`. Line references below refer to current Git source, not an assembler listing or object-size measurement. M1.8 DEVOBJ acceptance remains the last established aggregate execution evidence: 123 PASS, zero FAIL, expected SKIP 083. No new test outcome is claimed.

## BCPLMAIN functional map

| Source lines (approx.) | Area and responsibility | Extraction / coupling |
| --- | --- | --- |
| 1–583 | Extensive WIP provenance, historical discoveries, limitations, and interface narrative; comments rather than machine instructions | Move or curate historical detail in documentation later; do not delete evidence casually |
| 584–657 | Main CSECT and ENTRY/EXTRN; preserve incoming generated-module base and MVS caller linkage; allocate 68,592-byte global/stack/clearance region; paint stack and guard metadata | Bootstrap/core ownership; stack preparation also feeds stack service |
| 658–723 | System-vector base; initialize 700-word global vector; scan application export trailer, import BLIB export trailer, establish START | Coordinator; retain in BCPLMAIN |
| 724–811 | Publish G6, bounds G52–55 and native service globals (including I/O, byte, heap, G40 APTOVEC, STOP, provisional DEBUGINT); bind MEMBIND to G6!48 | Single coordinator registry; future modules supply relocatable ENTRY addresses |
| 812–880 | Initialize/open SYSPRINT, generated-code base registers and frame, invoke START, recover from bootstrap errors | Startup and coordinated error unwinding; I/O service dependency |
| 885–924 | SYSV jump table, stubbed count services, stack safe limit STKLIM and diagnostic text | System-vector ABI and stack module extraction constraints |
| 925–1010 | Return, count stub, FINISH/STOP, QSAM flush/close, MEMDRAIN/MEMBIND and main storage FREEMAIN | Highly coupled lifecycle; BCPLMAIN should orchestrate service shutdown |
| 1011–1057 | Generated-frame STKCK validation, STKOVFL and stack-check/count stub | Candidate BCPLSTACK, but frame ABI, SYSV offsets, FINISH and output buffer are coupled |
| 1059–1094 | Local APTOVEC implementation, size limit and safe-stack comparison | Duplicate service; targeted first integration |
| 1097–1425 | FINDINPUT, FINDPARM, INPUT/SELECTINPUT, RDCH/UNRDCH, ENDREAD, EODAD; primary/secondary QSAM and PARM streams | BCPLIO candidate; shared register saves, per-stream state and lifecycle |
| 1428–1593 | WRCH, FINDOUTPUT, WRAPOUTPUT, OUTPUT/SELECTOUTPUT, ENDWRITE and alternate stream QSAM | BCPLIO candidate; shares FINISH flush/close and output state |
| 1595–1916 | Bootstrap WRITEF fallback, numeric conversion, formatting and output scratch | Keep historical BLIB G76 when exported; consider separately only if live fallback warrants it |
| 1919–1942 | Obsolete/local GETBYTE and PUTBYTE instruction bodies | Registration uses BCPLBYTE EXTRN already; dead/local code requires careful proof before removal |
| 1943–2005 | Historical GETVEC notes and DEBUGINT formatter/output | Allocator lives in BCPLMEM; DEBUGINT shares default output buffer |
| 2006–2129 | MVS save area, G6 compatible fields, module/trailer pointers, dynamic-allocation state, DCBs, controls, QSAM buffers, shared register save slots, PARM state | Ownership must move with services; currently substantial static-state coupling |

The executable CSECT starts at line 584; hence the first ~583 lines are mainly historical commentary (not independently assembled executable code). These ranges describe **source footprint**, not assembled CSECT byte length. M2.0 Gate D should measure assembler location counter / link map before asserting which section materially drives displacement pressure.

## Addressability and registers

BCPLMAIN establishes `BALR 10,0` / `USING *,10` at lines 593–594, `USING MSVSAVE,13` at 603 and `USING SYSV,11` at 892. Generated BCPL uses R11 for SYSV, R5 for current frame, R6 as BCPL return, and R7–R9 for arguments/results. Startup puts constants 4096/8192/12288 into R1/R2/R3 for generated code (826–840). Independent assembly must not seize these registers without a specified preservation discipline. S/370 RX-format displacement is 12 bits; segmentation into separate sources alone without distinct CSECTs and bases does not solve addressability. No claim is made here that a particular assembled instruction exceeds range: no assembler listing or CSECT object-length evidence was collected.

## Storage and lifecycle ownership

BCPLMAIN owns the initial GETMAIN area (`DYNLEN=68592`, lines 2037–2042), global vector, working stack, safe stack limit STKLIM (921), main save area, loaded-module boundaries and SYSV table. G6 points to provisional save-area-compatible storage; G6!29 is the load-list head and G6!48 is the published allocator-list head. BCPLMEM owns `VECLIST`, allocator accounting, per-vector 12-byte headers, GETVEC/FREEVEC, MEMDRAIN, MEMBIND and MEMSTAT. MEMBIND receives an address of G6!48 (or zero to unbind). BCPLMAIN calls MEMDRAIN, then MEMBIND(0), before freeing the main allocation (994–1006). BCPLBYTE has no private BCPLMAIN storage references. BCPLAPT owns its own APMAXN and APLIMIT and imports STKOVFL, but APLIMIT starts at zero.

The QSAM DCBs, buffers, stream handles, OPEN/EOF flags, pushback state, PARM cursor and two wide register save arrays remain in BCPLMAIN. START is invoked only after global/service registration and initial SYSPRINT OPEN. FINISH and error paths flush and close streams before allocator drain and main GETMAIN release. A separate BCPLIO requires explicit initialization and shutdown ordering; it must not assume access to BCPLMAIN's private labels.

## Critical correction — secondary input stream

The external secondary input **DDNAME is BCPINB**, not BCPIN2: `IN2NAME DC CL6'BCPINB'` (2092) and `BCPIN2 DCB DDNAME=BCPINB` (2103). `BCPIN2` is the local assembler DCB label used by OPEN/GET/CLOSE. M1.9 contract/audit narrative calling the recognized stream `BCPIN2` was erroneous; update the documentation, not assembler semantics.

## BCPLAPT: exact first integration boundary (Gate B proposal, not implementation)

At 807–808 BCPLMAIN writes its own **local** `APTOVEC` label into global G40 (byte offset 160), although the independent BCPLAPT module exports APTOVEC/APLIMIT. Merely including the module in DEVOBJ/link-edit does not make its code execute. Local APTOVEC at 1067–1093 compares against BCPLMAIN STKLIM; independent BCPLAPT at lines 4–41 compares against its separately allocated, initially-zero APLIMIT and imports STKOVFL.

Gate B should: (1) declare `EXTRN APTOVEC,APLIMIT` in canonical BCPLMAIN, preserving the existing STKOVFL export; (2) publish the relocated external address `=A(APTOVEC)` in G40; (3) initialize the exported **data** word APLIMIT to BCPLMAIN's actual STKLIM before START can call G40; (4) retire the duplicate local routine/APMAXN without modifying the ABI; and (5) verify G40 **actually reaches** BCPLAPT, not just that link-edit succeeded. `tools/checks/externalize-bcplapt.py` illustrates precisely this transformation in a disposable combined source; its preconditions expect one BCPLMAIN CSECT, one local APTOVEC/APMAXN and the existing two-line G40 installation. Review its duplication of `ENTRY STKOVFL` against canonical source before applying anything: canonical already has that ENTRY. Focus tests 091, 092, 093 (normal nested calls and overflow); verify independent member resolution and limit boundary. Keep DEVOBJ only; do not touch production OBJ.

## BCPLMEM and BCPLBYTE (proposed Gate C)

BCPLMEM is an independent, deliberately nonreentrant static singleton. BCPL-visible exports are GETVEC/FREEVEC (G87/G88); private assembler interfaces MEMDRAIN/MEMBIND/MEMSTAT must not be mistaken for BCPL entry points. BCPLBYTE exports GETBYTE/PUTBYTE (G85/G86), uses the BCPL return convention, and has no BCPLMAIN private-storage references. BCPLMAIN still carries local GETBYTE/PUTBYTE bodies (1919–1942) but explicitly registers external BCPLBYTE addresses at 792–795. Gate C should verify there are no unexpected alternate references before any local deletion and confirm independent object/member resolution.

## Major extraction assessment and sequence

**Recommended order:** Gate B externalize BCPLAPT first (small, well-defined discrepancy); Gate C validate BCPLMEM/BCPLBYTE independence; Gate D prefer **BCPLIO before BCPLSTACK**, conditionally upon an assembly map and dependency review. I/O has large contiguous service regions (1097–1593) and a substantial state cluster (2051–2122), and BCPLMAIN's coordination can call a small explicit initialization/flush/close API. However, the existing FINISH/error paths and WRITEF/DEBUGINT output calls must be remapped carefully. BCPLSTACK's checked-call ABI is narrower but tightly tied to SYSV, STKLIM, frame linkage and STKOVFL's direct output/FINISH path: extracting it first would compound APTOVEC's just-repaired stack boundary and exceptional-exit coupling. Reevaluate if the assembler map shows a different urgent addressability constraint.

**Candidate BCPLIO boundary:** own QSAM DCBs, stream control blocks and buffers; export BCPL-facing stream entry points for G11–17, G33, G39, G41–42, G46–47; expose small private initialization/shutdown entry points so BCPLMAIN remains the coordinator. Define preserved registers, error semantics, calling contract and reentrancy explicitly before moving code. Defer bootstrap WRITEF and DEBUGINT changes unless required by the proven output dependency.

## Open items, gates, acceptance

No unresolved **architecture-policy** choice prevents Gate B. Evidence to obtain during later implementation includes (a) actual assembled CSECT sizes, active USING/base coverage and linker map; (b) proof of independent BCPLAPT execution including its overflow boundary; (c) detailed BCPLIO shutdown/error API and ownership; (d) an audit of dormant local byte bodies and of WRITEF fallback; and (e) any historical semantics not recovered. These are engineering verification tasks, not reasons to enlarge Gate A.

**Gate A acceptance decision:** ACCEPTED as source-grounded architecture inventory and implementation plan, without claiming a new executable regression result. **Gate B:** READY TO START, but **not started** here. No production HERC02.BCPL.OBJ promotion, no MVS dataset writes, no assembler edits. This decision accepts only Gate A, not M2.0 overall.
