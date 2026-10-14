# M2.1 Gate D — Minimal Programmer Diagnostics

**Status: OPEN; source audit complete, awaiting owner acceptance — 14 October 2026.**

**Predecessor:** Gate C accepted and closed; Gate B D7 DEVOBJ(BCPLM7) full test panel 00–123: **123 PASS, 0 FAIL, 1 expected SKIP 083**. No production OBJ changes.

## Purpose and limits

Finish a useful, simple, historically oriented programmer diagnostic contract for the **runtime release itself**. No native compiler-phase execution, tracing framework, new logging subsystem, postmortem engine, or speculative runtime globals. The primary diagnostic evidence is actual BCPL output, MVS GO completion status, and targeted regression results.

## Current diagnostic mechanisms and evidence

| Facility | Source behavior and ownership | Evidence / limitation | Gate D disposition |
| --- | --- | --- | --- |
| Stack overflow | D7 BCPLMAIN STKOVFL invokes BCPLIO private IOREPL to replace the pending primary SYSPRINT record with `STACK OVERFLOW`, then routes via STOPENT/FINEXIT with **GO RC=0012**. IOREPL does not itself PUT; FINEXIT performs flush/close. | Tests 052 checked-frame and 093 APTOVEC pass with explicit RC fixture. Earlier buffered primary output is intentionally discarded; BCPALT buffer remains BCPLIO-owned. | **Accept**, document replacement side effect; no change. |
| FINISH | BCPLMAIN FINIMPL zeroes STOPRC and FINEXIT calls IOFIN, RELMEM. | Tests 084,085,086 and 119 plus full panel. | **Accept** GO RC=0000 for normal termination. |
| STOP(N) | BCPLMAIN STOPENT stores requested R7 in STOPRC then FINEXIT cleanup. | Tests 086–089, including nonzero and buffered output. | **Accept**; N is application-chosen and not automatically a runtime diagnostic classification. |
| Overlong buffered output | BCPLIO IOWRCH reports capacity failure; BCPLMAIN IOSTOP sets RC=12. | Test 113 exercises rejection; full D7 panel passed. | **Accept** capacity failure; share RC=12 with stack overflow but distinguish messages/trigger. |
| DEBUGINT G150 | D7 bootstrap decimal formatting calls BCPLIO private IODIAG, appending bytes to the **primary SYSPRINT buffer** even if BCPALT is selected. IODIAG can truncate at 132 chars and signals private status; no guaranteed standalone line/newline. | Numerous fixtures call DEBUGINT to expose values; no exact diagnostic-format specification or direct overflow-format assertion claimed. | **Retain as provisional programmer aid**; do not promote as historical LIBHDR API. |
| WRITEST fallback | D7 publishes bootstrap WRITEST at G76 **only when BLIB has not registered historical WRITEF**. | BLIB and formatted-output regressions 053–081 accepted; no claim of complete parity between fallback and historical BLIB. | **Retain fallback**, prefer BLIB G76. |
| STACKHWM G56 | Compiled historical BLIB scans painted stack sentinels; returns a **BCPL word address** or sentinel 0/1. | Regression 120 checks in-range only; no exact high-water displacement proof and process allocation varies. | **Retain** narrowly defined observable contract; avoid unsupported precision claims. |
| MEMSTAT | BCPLMEM private native R1 ABI gives four counters, no public BCPL global; tracks its own vector allocations only. | Source verified; no instrumented quantitative lifecycle test in accepted panel. | **Retain private**, not a programmer-facing standard runtime service. |
| Missing START / invalid frames / allocator failure | D7 returns existing RC 20/36/24 etc. in source-defined exceptional branches; STKFORM avoids generic teardown when frame is invalid. | No matched dedicated diagnostic/cleanup execution proof for each path. | **Document limits**; no unsafe generic unwind or optimistic cleanup claims. |
| ABORT/BACKTRACE/MAPSTORE/logging | Historical BLIB/LIBHDR sources contain names, but no complete native system intercept/LEVEL/LONGJUMP/postmortem contract proven. | Gate C classed absent/incomplete and deferred. | **Exclude** from M2.1 programmer diagnostic promise. |

## Observability and operator/programmer boundary

The **programmer** can use accepted character output/BLIB formatting, G150 DEBUGINT where appropriate, STOP(N) for a chosen GO return code, G56 STACKHWM within its tested limits, and JES reporting for completed steps. These are distinct from **operator telemetry**, debugging facilities in MVS, private counters and historical postmortem interfaces. Diagnostics are not required to deliver automated backtraces, runtime-wide logging, exact heap reports or every anomalous exit description.

**Stack-overflow semantics intentionally discard an unflushed default output record.** This is preferable to masking the failure message and is explicitly part of D7's current limit behavior, not a guarantee about prior application output completeness. No result in this gate establishes preservation of all buffered records across corrupt-frame or early startup failures.

## Test traceability and known gaps

- 052, 093: stack-overflow record + explicit **RC=0012**.
- 084–089, 119: FINISH/STOP cleanup and output finalization.
- 053–081: formatted output / independent historical BLIB.
- 120: STACKHWM initialized/in-range value only.
- 113: overlong record rejection.
- 083 remains expected SKIP requiring source-only instrumentation.
- Exact STACKHWM usage, DEBUGINT truncation, numerical MEMSTAT counters and malformed-frame survival are **not covered** by a focused committed acceptance test. Track those as limits or optional future regression improvements, not hidden Gate D requirements.

## Documentation drift noticed

`native-compiler/regression/120-stackhwm-initialized/README.md` retains an older suggestion to promote BCPLMAIN to production OBJ once source-mode testing passes. That suggestion predates the current strict production-promotion boundary and **is not authorized** for M2.1. Gate F should either fix this historical README or explicitly supersede the instruction in the versioned runtime contract.

## Gate D decision

The existing diagnostic surface is adequate for the accepted runtime subset and the project owner's minimalist, programmer-centric policy. **No Gate D assembler code changes recommended.** Expanding telemetry or implementing unproven historical ABORT/BACKTRACE would distract from completing the native runtime. A consolidated completion-code register and regression coverage matrix belong to Gate F.

## Acceptance checklist

- [x] Inspect D7 diagnostic paths, BCPLIO private diagnostic helpers and BCPLMEM private instrumentation.
- [x] Record supported programmer-visible behavior, completion codes and side effects.
- [x] Separate historically demonstrable functions from provisional or unsupported extensions.
- [x] Map test evidence and uncertainty without claiming comprehensive coverage.
- [x] Determine no evidence-backed code change is necessary.
- [ ] Obtain owner acceptance and formally close Gate D.

**Gate D: source audit complete; READY FOR OWNER ACCEPTANCE.** DEVOBJ(BCPLM7) remains unchanged. Production OBJ remains unchanged.
