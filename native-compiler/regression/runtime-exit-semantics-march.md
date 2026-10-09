# BCPLMAIN runtime exit semantics march

Status: **OPEN — contract audit and test plan**

Starting baseline: **84/84 PASS** (regressions 000–083), confirmed on
TK5/MVS 3.8J 2026-10-09. The preceding storage reclamation march is closed.

## Scope

Reconstruct and validate the interface among FINISH, STOP, MVS step
completion codes, output DCB closure, and the existing common storage
teardown. Preserve the tested vector-before-main release ordering.
Do not treat early guesses about historical STOP as established fact.

## Source audit

1. In `asm/bcplmain-wip.asm`, the S.FIN system-vector entry at
   offset +40 branches to `FINIMPL`. On normal FINISH, the current
   implementation conditionally PUTs the partial `OUTBUF` record,
   calls `RELMEM`, restores the caller MVS registers and returns R15=0.
2. `RELMEM` drains `VECLIST` and FREEMAINs the combined main
   allocation, validated by test-only instrumentation in 083.
3. Startup performs `OPEN (BCPOUT,(OUTPUT))`. The normal finish path
   does not explicitly CLOSE `BCPOUT`. An earlier attempted CLOSE is
   described in the assembler source as looping until S322 (Job 956).
   Hence CLOSE requires an isolated diagnostic, not a speculative edit.
4. `richards-bcpltape/sys3/bcpl/libhdr` declares G!30 STOP.
   No STOP implementation is installed at G!30 in the current WIP.
5. `richards-bcpltape/km10/bcplmac` contains `USATCBCC` (task
   completion-code field), `TNUM/USATNUM` (tidy-up time), and
   descriptors for I/O close routines. These show historical runtime
   machinery existed; they do not establish STOP argument semantics
   or the mapping between BCPL values and MVS return codes.
6. Existing WIP bootstrap errors return nonzero R15 values (16, 20,
   24, 36); normal FINISH returns zero. The controlled stack overflow
   currently branches through FINIMPL; it is not a separately
   reconstructed ABORT termination contract.

## Proposed sequence

**First rung: FINISH lifecycle diagnostics.** Add a narrowly scoped,
test-only assembler instrumentation experiment to establish whether
BCPOUT can be explicitly closed safely *after* buffered output is
flushed and *before* the existing storage teardown. Capture IFOX
listing, IEWL result, GO completion/ABEND and visible output. The
probe must not change canonical BCPLMAIN. Guard against another
S322 and retain job report evidence.

**Second rung: FINISH close semantics.** Only if the diagnostic
supports it, implement an explicit CLOSE on normal FINISH. Verify
empty output, partial output, and multiple output records with
focused regressions, then preserve any correction in the runtime
source and preflight tooling.

**Third rung: STOP and completion codes.** Search additional
historical sources for STOP call signature, result code, and tidy-up
behavior. Define the intended contract in writing before wiring
G!30; independently exercise normal FINISH and nonzero termination.

**Closure:** targeted probes PASS, no unexamined cleanup regression,
and complete native panel (currently 000–083 plus new tests) PASS.

## Boundaries

- No claim of historical DCB CLOSE success without guest evidence.
- No guessed STOP signature, no unconditional ABEND/ESTAE support.
- Static checks in `tools/checks/` run in the assistant's environment
  before committing any executable assembler change; focused and full
  TK5 execution remain separate.
- Instrumentation must be test-local, not installed in production code.
