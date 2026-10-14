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

## Gate C execution strategy — smallest defensible slice

**First decision:** choose the next intended **native compiler component** and test it in isolation rather than promising execution of the full `SECTION "BCPL"` driver. The first slice might be one compiler phase with a deliberately constrained input/driver stub, but its contract and build route must be explicitly selected.

Recommended ordered investigation:

1. Determine what actual currently demoted Cambridge and resident compiler variants require, as distinct from the preserved `bcplib/bcpl` sources. Locate entry exports and dependencies in the generated INTCODE/OCODE/native compiler pipeline.
2. Determine exact historical DATE triple format, calling/return ownership and initialization. Obtain implementation evidence if available; otherwise explicitly identify an MVS adaptation.
3. Determine LEVEL/LONGJUMP frame and saved-program-state semantics, including register/BCPL W restoration and interaction with checked stack entry; identify negative-path test (recoverable syntax error) and positive-path tests.
4. Map compiler's logical SYSIN/SYSPRINT/OCODE/CODE/SYSGO roles onto BCPLIO/MVS DD statements, paying attention to record, character, and stream close semantics. Avoid treating alias additions as the complete solution.
5. Decide which loader/overlay/postmortem features can remain unsupported for a **nonoverlay, no-load-and-go** initial native compiler configuration.
6. Recommend at most one small code change at a time, with an executable regression that discriminates the exact historical behavior.

## Gate C acceptance criteria

- [x] Gate B formally accepted; D7 source/build/full regression evidence preserved.
- [x] Initial source-grounded compiler compatibility matrix recorded.
- [ ] Identify and formally choose the first bounded native compiler component/execution mode.
- [ ] Verify exact ABI/provider semantics of interfaces required for that component, or record them as unresolved with a reproducible evidence task.
- [ ] Define targeted executable tests for each *selected* contract; make code changes only upon a justified and explicit decision.
- [ ] Run impacted focused tests and the full D7 candidate suite after any runtime implementation.
- [ ] Record owner acceptance and close Gate C.

## Explicit exclusions

No arbitrary publication of historical globals, speculative date representation, full exception/postmortem facility, general-purpose MVS DD manager, comprehensive overlay loader, compiler-generator replacement, production OBJ promotion, or silently reusing the D6 runtime. Gate C may conclude with a documented **no-code** result if the selected next native compiler slice does not yet require new services.

**Gate C remains OPEN.** No assembler code, MVS source members, or native objects were changed to initiate this review.
