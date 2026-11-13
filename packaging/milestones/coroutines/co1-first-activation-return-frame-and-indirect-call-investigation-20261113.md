# CO.1 — First activation, return-frame obligations and indirect entry

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Date:** 13 November 2026
**Reviewed GitHub main:** `fe521e461dea9cc73cdb2412531119c513bdeec9`
**Evidence:** SOURCE-OBSERVED, earlier-owner-reported native/compiler evidence, assistant host-only tests and DESIGN INFERENCE
**Status:** CO.1 IN PROGRESS; owner design gate OPEN; CO.2–CO.5 NOT STARTED

## Authority and boundary

This checkpoint extends [CO.1 native ABI investigation](co1-native-abi-and-stack-source-investigation-20261112.md) and [historical control-block review](co1-historical-native-control-block-and-abi-discrepancies-20261112.md) after the [JOB 5345 checked-call compiler-only result](co1-native-call-abi-jes-5345-compile-only-result-20261113.md). The [milestone authority](milestone-implement-coroutine-support-for-native-compiler.md) requires owner-approved first-activation and save/restore contracts **before CO.2 implementation**. Existing selections: Approach A valid/live pointer descriptors and S1 active safe-limit switching; descriptor fields/offsets, native public globals, entry alternative E1/E2, stack diagnostics D1/D2, first-entry linkage and complete save set are **not approved**.

No current native coroutine, worker stack or approved first-activation code is present. No synthetic frame described here was submitted to IFOX, IEWL or native GO.

## 1. Frame and register facts from source

Historical `richards-bcpltape/bcplib/bcpl/cghdr` maps R4 = `R.B` (callee), R5 = `R.P` (active BCPL P), R6 = `R.L` (continuation), R7–R10 = arguments (R7 also result), R11 = system-vector base, R12 = global-vector base, R14 = checked-entry link and R15 = `R.W` (new workspace).

The historical `CGAPPLY` first constructs R15 from caller R5, resolves the callee into R4, and issues `BALR 6,4`. The generated `CGSAVE` saves the incoming R4–R6 plus applicable formal-argument registers at `0(R15)`; for checked `/CN`, it calls `BAL 14,60(11)` with one inline **full frame size** word. The current `bootstrap-toolchain/asm/bcplmain.asm` `STKIMPL` establishes `R5=R15`, checks that size against `STKLIM`, restores R4 from `0(R15)`, advances R14 and resumes generated code.

The currently tracked native return routine is exact and order-sensitive:

```asm
RETIMPL  L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
```

Thus R6 (saved continuation) and R5 (saved caller P) are loaded from the **current callee frame**, but R4 is then loaded from word 0 of the **restored caller frame**. The order is not interchangeable. Ordinary generated `BCR 15,11` returns to this system-vector service.

## 2. Consequence for a never-run worker — requirement, not layout approval

For a worker entered through ordinary generated `CGSAVE`, the incoming R15 must designate a writable correctly aligned frame inside its own safe worker stack. The incoming R4 must identify the worker entry; the incoming R6 must designate a legitimate continuation after the worker returns; the incoming R5 must be a **valid synthetic caller-frame pointer**. On entry `STM 4,...,0(15)` stores these incoming values at offsets 0, 8 and 4 respectively.

On a **normal worker return**, `RETIMPL` will:

1. Read worker-frame `8(R5)` to restore the planned continuation into R6.
2. Read worker-frame `4(R5)` to restore the synthetic caller P into R5.
3. Read `0(R5)` of that **synthetic caller P** to restore R4, then branch to R6.

Therefore a proposed first-activation state cannot consist of just a worker entry and saved stack pointer, or only a saved R6. It must ensure that the synthetic caller frame remains addressable through the exit path. The chosen worker-exit continuation must also dispose of/transition the worker safely, without falling through into an arbitrary root continuation. The exact placement, ownership, initial R7 argument/result, bookkeeping, and handoff to the parent coroutine remain open for owner design.

This is a **necessary implication of the current reconstruction**, not proof that historical missing `KM10.COMAIN` used this layout. Historical `richards-bcpltape/km10/comacro` declares `COPSAVE`, `COENTRY`, `COBSEPTR`, `COEXIT`, `COHOLD`, `COLDPTR` and `COSTART`, but not their operative first-entry or return algorithm. Do not copy these macro offsets into the native descriptor without approval.

## 3. Preservation caveat: R10, runtime helpers and the switch boundary

R10 is the fourth BCPL argument register **at a call boundary**. The current `bootstrap-toolchain/asm/bcplmem.asm` uses `BALR 10,0` for its private base in `GETVEC` and `FREEVEC` and does not restore the incoming R10 in the displayed GETVEC path. Therefore **do not assume** every ordinary native runtime call preserves R10 just because compiler-generated procedure calls carry four arguments in R7–R10. A native switch must define exactly which registers and values are live at the **suspend/resume boundary**; it should not silently treat a general-purpose callee-clobber assumption as historical convention. A complete machine register snapshot, if adopted, also needs explicit R14, R15, R11/R12, R13-save-area and possible PSW-condition-code policy.

`BCPLMEM` identifies its allocator as a nonreentrant singleton. No source proves that suspending inside its GETMAIN/FREEMAIN operations is safe. Keep any future coroutine allocation and cleanup outside a partially executed allocator call, and never release the currently executing or reachable suspended stack.

For existing S1 direction, both `STKLIM` and the independent `BCPLAPT APLIMIT` limit must describe the active stack before any checked entry or temporary-vector call can run. G54/G55 versus worker inspection remains D1/D2 pending. This checkpoint changes no installed stack limits.

## 4. New isolated compiler-only procedure-valued entry probe

Committed:
- `packaging/milestones/coroutines/probes/co1-indirect-entry/source.bcpl`: `SUM2(A,B)`, `CALLIND(F,A,B) = F(A,B)`, `NEST(F,X) = CALLIND(F,X,20)`, and `START()` calling `NEST(SUM2,22)`. The BCPL expression's expected arithmetic result is 42, **not an observed native GO output**.
- `packaging/milestones/coroutines/probes/co1-indirect-entry/cambridge-parm.txt`: one 80-column `/CN` fixture (checked entry, no binary deck).
- `tools/bootstrap/probe-co1-indirect-entry.py`: one-job resident compiler invocation, job name `CO1IND`; recovered assembler source-oracle only.
- `tools/checks/test_co1_indirect_entry.py`: isolated host-only verifier tests.

The oracle requires at least **four** complete +60 entries with unique positive aligned frame-size definitions, one `STM 4,9,0(15)` for the three-formal `CALLIND`, at least three `BALR 6,4` calls, normal `BCR 15,11` return, R15 frame formation, and no +20/+80 counted entries. These are **structural checks**, not a proof that the actual callee address was fetched from formal `F`; detailed emitted assembly must be inspected before claiming that specific instruction or full indirect-call native behavior.

The probe only executes `tools/bootstrap/compile-mvs` (resident Cambridge `ICINT19` compilation and textual CODE recovery). **No IFOX, IEWL, native GO, installed object or permanent MVS dataset modification.** It writes `compiler.log`, `generated.s370.asm` and `summary.json` to a new directory under `workarea/co1-indirect-entry/`, recording the revision, compiler RC, JOB ID if available, structural counts and explicit `assembled:false`, `linked:false`, `native_go:false`. Its console output is concise.

## 5. Verification and owner gate

**Host-only verified in the assistant's separate workspace:** 16/16 unit tests PASS, Python `py_compile` PASS, and one synthetic end-to-end invocation PASS (fake `JOB 8124`; **not MVS evidence**). Fixtures are ASCII, no record exceeds 80 columns, and the four staged GitHub code/fixture blobs are byte-identical to the locally tested files. An independent **21/21** current-GitHub-source assertion audit confirmed CGHDR/CGSAVE/CGAPPLY, RETIMPL order, checked entry, allocator R10 usage, BCPLAPT, historical KM10 fields and the earlier JOB 5345 scope.

**New MVS JOB evidence:** NOT YET AVAILABLE. The owner can authorize/execute the compile-only probe separately; do not treat a compile PASS as successful first activation or coroutine implementation.

**Still required before CO.2:** owner-reviewed first worker entry and exit-frame design, E1/E2 switch interface and R7/R6 transfer, exact save set, descriptor and allocation contract, S1 stack installation (including APLIMIT), and native module/global ownership. The recommended next step is review of a concrete native first-activation frame **after inspecting emitted code**, then an isolated candidate-only IFOX/IEWL/GO verification under a separate MVS authorization.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
