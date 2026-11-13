# CO.1 — Indirect CALLIND target R4 origin: source review and compile-only audit preparation

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026
**Reviewed GitHub main:** `367a6fb5a2790caa559acd25bf99c67f3b7e1086`
**Evidence class:** SOURCE-OBSERVED and ASSISTANT HOST-ONLY TESTED; stronger MVS target-emission result PENDING
**Status:** CO.1 IN PROGRESS, owner design gate OPEN; CO.2–CO.5 NOT STARTED

## Purpose

After the [owner-reported JOB 5346 compiler-only PASS](co1-indirect-entry-jes-5346-compile-only-result-20261113.md), close a *source-analysis gap* without overclaiming that result. JOB 5346 established four +60 checked entries, one three-formal save, and four `BALR 6,4` calls, but its structural oracle did **not** associate the call inside `CALLIND(F,A,B)` with the formal procedure argument `F`.

The [first-activation/continuation investigation](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md) established that native first-entry and normal return require a legitimate saved caller P and R6 exit continuation. This focused call-target inquiry does not approve an actual worker-entry layout or change the switch interface.

## Historical code-generator evidence

Source anchors: `richards-bcpltape/bcplib/bcpl/bcpl`, option handling and `CODESTREAM` selection; `richards-bcpltape/bcplib/bcpl/cg`, `CGENTRY`, `CGSAVE`, `CGAPPLY` and `GENLAB`; `richards-bcpltape/bcplib/bcpl/cghdr`, register mapping; `bootstrap-toolchain/asm/bcplmain.asm`, `STKIMPL`.

- Code-generation option `/CN` enables checked entry, disables the binary deck and produces **textual CODE listing**. The compiler enables `LISTING` when it obtains the CODE output stream. `CGENTRY` prints a label resembling `Lnn EQU * ENTRY TO CALLIND`. The seven-character `CALLIND` name fits the historical heading field.
- `CGSAVE` saves R4–R6 and incoming argument registers into the new frame at `0(R15)`. With three formals, `STM 4,9,0(15)` saves R7 (formal `F`) at **byte offset 12**. Subsequent `MOVESTOR` associates the first formal with BCPL `P!3`. The checked entry makes `R5=R15`.
- `CGAPPLY` resolves the function expression into R4 and issues `BALR 6,4`. A legitimate indirect call in this small fixture can use `L 4,12(5)` (saved first formal) or, if R7 has not been overwritten since entry, `LR 4,7`. These are **narrow accepted emitted-code shapes**, not asserted universal code-generator behavior.

## Versioned new candidate audit

The new `tools/bootstrap/probe-co1-indirect-target.py` calls the *existing* `tools/bootstrap/probe-co1-indirect-entry.py` to perform one fresh real MVS compiler-only `ICINT19` run of the unchanged `SUM2/CALLIND/NEST/START` fixture with `CAMBCOMP` and private `/CN`. It does not run IFOX, IEWL, native GO, install an object, or edit a permanent MVS dataset.

The new `tools/bootstrap/co1-indirect-target-audit.py` isolates the `CALLIND` procedure from the recovered textual assembly and requires:

1. Exactly one named `ENTRY TO CALLIND`, one checked `BAL 14,60(11)` and one three-formal `STM 4,9,0(15)` in that procedure.
2. Exactly one associated `BALR 6,4` within its procedure region.
3. The **last identifiable R4 definition** before that call must load `F` either from `12(R5)` or directly from R7 with **no earlier identifiable R7 modification**.
4. No intervening branch, multi-register load or later R4 overwrite that would obscure the target; the target definition must be within eight listing lines of the call.

This is a deliberately fail-closed *bounded textual check*. Other valid optimizer sequences may fail classification. A FAIL requires reviewing the retained local listing; it is **not automatically a compiler defect**. Even a PASS proves only the emitted R4-call-site relationship as recognized, **not execution** of the target or coroutine first activation. The audit does not attempt general instruction-level register dataflow or PSW condition-code analysis.

The wrapper verifies that the prior structural probe's exact JOB, counts and zero driver RC agree with its saved `summary.json`. It retains `compiler.log`, `generated.s370.asm` and `summary.json` from that fresh run, plus `target-probe.log` and `target-audit.json` in the same `workarea/co1-indirect-entry/<run-id>/` directory. The latter records the entry label, accepted R4 instruction, attributed origin, listing line numbers, source revision and SHA-256 of the recovered listing. Only concise status, JOB, origin and evidence path are printed.

## Checks performed on the assistant's own workspace

- **29/29** local Python unit tests PASS: target provenance, prologue and checked-entry scope, duplicate or absent calls, R4/R7 clobbers, intervening branches or LM, incorrect formal offset, distant target, and driver/summary mismatch detection.
- Python syntax compilation passed; a synthetic end-to-end wrapper run produced `CO.1 TARGET PASS` with **fake JOB 8125** and a retained `target-audit.json`. JOB 8125 is **not real MVS/JES evidence**.
- Four staged Python blobs (auditor, wrapper and two test modules) are byte-identical to the assistant's tested workspace files. **16/16** additional source-contract assertions passed against the authoritative GitHub revision.

**Next verification:** owner-executed, guarded, quiet **MVS-facing compile-only** run of `tools/bootstrap/probe-co1-indirect-target.py`. Preserve both PASS and FAIL reports. Report only its actual JOB, status, target origin and workarea path; do not claim the previously accepted JOB 5346 has been upgraded retroactively.

## CO.1 design transfer

A source-verified pointer call is one prerequisite for a worker-entry design, not a native coroutine. First activation still needs an owner-approved synthetic caller frame, R6 exit continuation, frame alignment and R15, valid entry R4, saved-switch register/PSW policy, R7 value delivery, Approach A lifecycle and S1 coordination of `STKLIM` with `BCPLAPT APLIMIT` (and the D1/D2 diagnostics decision). `STKCIMP` at +80 remains a separate defective counted/checked service pending review.

**No first-worker frame or switch implementation, no new global allocation, no runtime change, and no milestone closure. CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
