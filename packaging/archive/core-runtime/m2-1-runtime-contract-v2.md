# BCPL for MVS — Native Runtime Contract v2.0 (M2.1 D7)

**Candidate specification — 14 October 2026.** Applies to `asm/bcplmain-d7-candidate.asm` installed as DEVOBJ(BCPLM7), independently linked with DEVOBJ(BCPLIO), (BCPLMEM), (BCPLBYTE), (BCPLAPT), and (BLIB). Supersedes M1.9's `runtime-contract-v1.md` **for this D7 candidate only**; v1 remains historical evidence. No production OBJ promotion.

## Public and private boundaries

- Entry and startup: generated application CSECT and BCPL global-export trailer, BCPLMAIN initialization and dispatch to G1 START; compatible application and BLIB trailers registered by runtime. System-vector services use generated-code register R11; normal native BCPL procedures use R5 frame, R6 return and R7–R9 arguments/results. `SAVEAREA` G6 and extended FREEBASE publication are supported at tested scope only.
- Stream global subset: G11–17 SELECTINPUT/SELECTOUTPUT/RDCH/WRCH/UNRDCH/INPUT/OUTPUT; G33 WRAPOUTPUT; G39 FINDPARM; G41–42 FINDOUTPUT/FINDINPUT; G46–47 ENDREAD/ENDWRITE, provided by independent BCPLIO.
- Recognized MVS input DD names BCPIN, BCPINB (FB80); output SYSPRINT, BCPALT (FB132). Program records are character-oriented EBCDIC, record padding trimmed, synthetic newline on input. Unrecognized stream names fail rather than resolving arbitrary DDNAMEs. No claim of fully compatible historical compiler SYSIN/OCODE/CODE/SYSGO naming.
- Memory/bytes: G87 GETVEC/G88 FREEVEC from BCPLMEM, private MEMDRAIN/MEMBIND/MEMSTAT; G85 GETBYTE/G86 PUTBYTE from BCPLBYTE; G40 APTOVEC from independent BCPLAPT with STKLIM initialized. MVS GETMAIN/FREEMAIN and singleton static descriptors are implementation adaptations; not reentrant.
- Stack: 16,384-word working stack with clearance, G54 STACKBASE and G55 STACKEND as word addresses of allocated extent; checked procedure frames verify encoded frame size before crossing STKLIM. BLIB STACKHWM G56 yields in-range word address or documented sentinel at tested scope (not an exact peak meter).
- Historical BLIB as an **independently linked compiler-generated object** provides tested formatting, strings and selected helpers. Its presence does not make every LIBHDR global supported. G150 DEBUGINT is a provisional nonhistorical programmer aid; G76 bootstrap WRITEST fallback applies only absent BLIB WRITEF.
- FINISH returns GO RC=0000; STOP(N) returns application-selected N after normal stream close/flush and memory teardown. D7 stack exhaustion (checked frames or APTOVEC) emits STACK OVERFLOW, replacing unflushed primary output, and returns **GO RC=0012** with shared normal cleanup. Output buffer-capacity failure also returns 12; reason cannot be inferred from RC alone.
- Startup/global/invalid-frame exceptional exits use source-defined RC16/20/24/36 with path-dependent cleanup; not all are fault-injection tested or guaranteed to preserve buffered output.
- Private native interfaces are not automatically callable BCPL globals; diagnostic MEMSTAT does not describe every MVS allocation. Static state means no thread/reentrancy guarantee.

## Deliberately excluded or unresolved

G29 DATE return triple; G31 LEVEL/G32 LONGJUMP nonlocal recovery; general module/overlay loader, compiler-specific stream adapters, block/file/terminal and FORTRAN interfaces, full ABORT/BACKTRACE/MAPSTORE/logging, automatic postmortem or precise heap/stack instrumentation, calling-counter stubs and exhaustive exception recovery. Historical source references are evidence of possible future requirements, **not native availability**. See Gate C and Gate D records for provenance.

## Validation and acceptance limit

The source review, D7 IFOX/IEWL RC=0000 payloads (2989/2992), Gate E native independent-object JOB 3646 MAP/XREF and GO RC=0000, and Gate E full 00–123 panel **123 PASS, 0 FAIL, 1 expected SKIP 083** substantiate the bounded subset. This is integration evidence, not measured line or branch coverage or native execution of the Cambridge compiler. Current compiler CAMBCOMP still runs as INTCODE under ICINT19.

Related: `packaging/m2-1-gate-b-termination-failure.md`, `packaging/m2-1-gate-c-historical-runtime-compatibility.md`, `packaging/m2-1-gate-d-programmer-diagnostics.md`, `packaging/m2-1-gate-e-application-integration.md`, `packaging/m2-1-runtime-completion-codes.md` and `packaging/m2-1-runtime-coverage-matrix.md`.
