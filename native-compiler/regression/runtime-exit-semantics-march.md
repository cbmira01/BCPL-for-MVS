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

## FINISH/CLOSE promotion checkpoint — 2026-10-09

Regression 084's test-local CLOSE experiment passed on TK5 with
expected output `A` and normal GO completion. This confirms that
`CLOSE (BCPOUT)` can follow the pending-record PUT and precede
RELMEM on the tested path.

`asm/bcplmain-wip.asm` now executes the tested CLOSE in canonical
FINRETN. Regression 084 has been converted to a normal runtime test
(no longer injects CLOSE). New regression 085 covers FINISH with an
opened output DCB and no pending record: no PUT, then CLOSE, then
RELMEM. Its expected output file is intentionally empty; the
acceptance condition is normal ASM/LKED/GO completion.

The test-only instrumentation for regression 083 emits output *after*
RELMEM. Therefore its temporary assembler copy now omits canonical
CLOSE; this preserves its narrowly scoped storage-release counters
without attempting PUT against a closed DCB. Regression 083 does not
test production CLOSE; 084/085 do.

**Pending guest acceptance:** focused regressions 083–085, followed by
a full panel sweep if they pass. This march remains open. No STOP
semantics have been implemented or assumed.

## FINISH/CLOSE full-panel acceptance — 2026-10-09

The operator reran the entire TK5 native regression panel after the
canonical `CLOSE (BCPOUT)` promotion. Results: **86 PASS, 0 FAIL,
TOTAL 86**, cases 000–085 inclusive. Focused tests 083–085 had
also passed (3/3), and `tools/checks/check-native-runtime.py`
reported OK (source and BLIB injection).

The production FINISH path now flushes pending output, closes BCPOUT,
releases outstanding vector allocations, frees combined global/stack
storage, and returns normally to MVS. Regression 084 confirms the
pending-output path and 085 the zero-pending-output path; 083's
test-only instrumentation remains isolated from canonical CLOSE.

**FINISH/CLOSE submilestone complete.** The overall runtime-exit
semantics march remains open pending historical STOP (G!30) and
completion-code contract research and validation. This checkpoint
establishes the new 86/86 regression baseline.

## STOP historical evidence checkpoint — 2026-10-09

Surviving source establishes more than STOP's slot number:

- `richards-bcpltape/sys3/bcpl/libhdr` defines `STOP:30`.
  The MR10 kit's `blib` also identifies STOP as global 30.
- `richards-bcpltape/bcplib/bcpl/blib`, in
  `ABORT(CODE, ADDR, OLDSTACK, DATA)`, ends with `STOP(100)`.
  ABORT emits diagnostic/postmortem material first. This is direct
  evidence of **one positional argument** and a nonzero code (100).
  It strongly suggests STOP handles termination with a requested
  completion status; the exact MVS mapping is still not proven.
- `richards-bcpltape/km10/bcplmac` reserves `USATCBCC` for a task
  completion-code field and `TNUM/USATNUM` for tidy-up time, but
  neither gives the executable STOP entry or its return contract.

### Working hypotheses requiring TK5 probes

H1: `STOP(N)` terminates execution without returning to the caller.
H2: `STOP(0)` requests normal completion while `STOP(100)`
requests distinguishable nonzero MVS step completion.
H3: STOP shares FINISH's flush/CLOSE/RELMEM lifecycle, then chooses
the final completion code; normal FINISH keeps its established zero.

### Proposed next regression rungs

086: Test-only global G!30 adapter for `STOP(0)`, mirroring the
verified FINISH path; assert GO RC=0000.

087: Test-only global G!30 adapter for `STOP(100)`, isolate the
resulting MVS step condition code; because the ordinary native
runner treats nonzero GO RC as failure, this needs a dedicated
test driver or explicit expected-completion-code support. Do not
weaken the normal regression acceptance rules.

After these diagnostics, decide whether the MVS return-code mapping
matches the historical contract closely enough to promote G!30 to
canonical BCPLMAIN. The ABORT call supplies a valuable semantic
constraint but is not sufficient to prove a specific numeric mapping.

**No executable STOP change has been made in this checkpoint.**

## STOP test-adapter probes ready — 2026-10-09

Regressions 086 and 087 implement **test-local** G!30 STOP adapters.
The adapter is added to the generated combined assembler only; it
checks R7 against the intended argument, installs its entry at G!30,
and shares the verified FINIMPL flush/CLOSE/RELMEM path. The normal
FINISH return remains unchanged. For 087 the temporary assembler
selects MVS return code 100 after the normal MVS register restoration.

- 086 STOP(0): expected output `S` and GO RC=0000.
- 087 STOP(100): expected output `S` and GO RC=0100.
  The runner accepts that RC **only** for regression 087, with
  successful ASM/LKED and an exact output assertion.

**Critical evidence distinction:** These probes establish whether the
proposed STOP calling/lifecycle/return-code adapter runs on TK5.
They do not prove that the lost historical STOP used an identical
argument-to-RC mapping. Historical source supports `STOP(100)` from
BLIB ABORT, not an exact MVS return-code implementation.

Status: **PENDING TK5**. Full panel deferred pending focused 086–087.

## STOP adapter focused acceptance — 2026-10-09

Operator executed `python3 tools/checks/check-native-runtime.py`:
**OK (source and BLIB injection)**. Focused `tools/run-native-regression
86 87 --show-output`: **2 PASS, 0 FAIL**. Both emitted `S`.

Regression 086's test-only STOP(0) adapter completed normally with
GO RC=0000. Regression 087's test-only STOP(100) adapter was accepted
by the narrow GO RC=0100 rule. This validates the proposed test
adapter's calling convention and MVS return-code feasibility, not
the unknown historical numeric-mapping contract.

**Next gate:** decide whether to promote STOP to canonical BCPLMAIN,
retaining its tested FINISH/CLOSE/RELMEM path, and convert these
regressions from adapter tests to production tests. Run focused tests
before the full panel. No canonical STOP implementation yet.

## Primary-source resolution: STOP(N) completion-code contract

**Evidence status: HISTORICALLY DOCUMENTED (not merely inferred).**
Martin Richards, *The BCPL Programming Manual*, University of
Cambridge Computer Laboratory, **November 1974**, section **2.8.2**
("Other useful subroutines"), printed **page 19** (PDF page index 22),
states:

> STOP(N) will terminate the job step, returning a completion code N.

Primary-source facsimile:
https://www.softwarepreservation.org/projects/BCPL/cambridge/richards-manual-1974.pdf

The same manual's section 3 ("Using BCPL on the 370") describes the
Cambridge System/370 environment, and its library-global list assigns
`STOP:30` (section 3.1.1). This is a direct contemporary specification
of the intended **BCPL job-step completion-code contract**:

`STOP(N)` terminates the job step with completion code `N`.

This **supersedes the historical-contract uncertainty** stated above
under "Working hypotheses", "STOP historical evidence checkpoint",
and "STOP adapter focused acceptance". That uncertainty was justified
before consulting this manual but is now resolved for ordinary,
representable completion-code values.

Independent evidence already in the repository:
- `richards-bcpltape/bcplib/bcpl/blib` calls `STOP(100)` at the
  conclusion of `ABORT`.
- TK5 isolated regressions 086 and 087 (2 PASS / 0 FAIL) show that
  our *test-local* adapter can terminate with MVS step RC=0000 for
  `STOP(0)` and RC=0100 for `STOP(100)`, respectively.

**Limits:** The manual does not specify how to handle negative
arguments, integers outside the MVS completion-code range, or the
implementation's underlying register/cleanup mechanics. Test-local
regression success does not mean STOP has been installed in canonical
`asm/bcplmain-wip.asm`; production promotion and full-panel validation
are still pending. FINISH retains the validated RC=0 behavior.

**Engineering decision:** Use the manual's direct `N` mapping for the
canonical STOP interface, subject to a separately documented decision
on out-of-range values. Do not treat the mapping as a discretionary
installation convention.
