# CO.1 — Historical native control blocks and ABI discrepancies: checkpoint 2

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Date:** 12 November 2026
**Reviewed source HEAD:** `cea3d362a7ad5b016644e51dc01964fdd5d5020b`
**Status:** CO.1 IN PROGRESS; source evidence and alternatives only; design gate OPEN
**Evidence class:** SOURCE-OBSERVED, supplemented by explicitly identified engineering inferences. No new native execution.

## Purpose and limits

Extend [CO.1 checkpoint 1](co1-native-abi-and-stack-source-investigation-20261112.md) with surviving **historical KM10 native** control-block evidence, a callable-versus-data stack-global conflict, a candidate native switch-entry seam, and profile-dependent overflow evidence. [CO.0 closure](co0-formal-closure-20261112.md), [milestone authority](milestone-implement-coroutine-support-for-native-compiler.md), [nomenclature](../../architecture/runtime-and-library-nomenclature.md), [runtime contract](../../architecture/runtime-contract-v1.md), [stack-check contract](../../architecture/stack-check-contract.md), and [Global Number Registry](../../architecture/global-number-registry.md) remain controlling. Owner-approved Approach A pointer descriptors and S1 active-limit switching remain **directions**, not approved offsets, register save sets, global assignments or native implementation.

## 1. KM10 COMACRO contains an explicit native coroutine control block

**SOURCE-OBSERVED:** `richards-bcpltape/km10/comacro`, `./ ADD ... NAME=COBASE` (approximately lines 47–90), defines a System/370 assembler `COBASE DSECT`. Distinct field names are:

| Historical macro field | Historical description |
| --- | --- |
| `COLINK` | Coroutine chain link |
| `COFATHER` | Activator, or zero if inactive |
| `COPSAVE` | Saved stack pointer |
| `COLBASE` | Local stack base, word address |
| `COLEND` | Local stack limit, word address |
| `COSTKLIM` | Local stack limit, byte address |
| `COENTRY`, `COBSEPTR`, `COEXIT` | Initial stack entry, base and exit-related words |
| `COHOLD`, `COLDPTR`, `COSTART` | First wait, old pointer and startup-related words |

The macro defines `CODATA` and `COMIN` sizing constants. The surviving definition supports historical *concepts* of per-coroutine saved stack pointers, bounds, parent relationships and initial wait state. **It does not prove `KM10.COMAIN` executes a particular switch order, save set, first-entry trampoline or safe-limit comparison.** The historical macro is not a license to copy offsets into the reconstructed native ABI. No claim of test execution follows from a DSECT declaration.

## 2. KM10 exposes coroutine-specific stack diagnostics; G54/G55 differ

**SOURCE-OBSERVED:** `richards-bcpltape/km10/coblib/cortn` declares `CSTKBASE:107`, `CSTKEND:108` and `CSTKHWM:109` (lines 1–8). Its `TRACECO` explicitly converts a coroutine BCPL word pointer into a byte pointer (`BCPLCOBASE << 2`) and calls `CSTKHWM(COBASE)`, `CSTKBASE(COBASE)` and `CSTKEND(COBASE)` (approximately lines 398–434).

The same source's `VALIDPOINTER` invokes `STACKBASE()` and `STACKEND()` as **functions** (approximately line 313). By contrast, the reconstructed `bootstrap-toolchain/asm/bcplmain.asm` installs G54 and G55 as **BCPL word-address data values** (approximately lines 210–222), not callable procedure addresses. This is a **real source-level ABI incompatibility if historical KM10 CORTN is linked unchanged**. The origin of the callable forms and their implementation is not established without the missing `KM10.COMAIN` and the precise historical combined-header/module configuration. Do not silently equate KM10's G107–109 with approved native global allocations: the current registry reserves assignment decisions for explicit owner review.

**Open diagnostic choice:**

| Alternative | Benefit | Cost / uncertainty |
| --- | --- | --- |
| D1 — Make current G54/G55 describe **active** coroutine; unchanged BLIB `STACKHWM` reads active paint | Reuses established G54–G56; no new public globals | Changes values seen while workers run; must preserve root values, paint/metadata and compatibility with existing consumers |
| D2 — Keep G54/G55 **root-only**, add explicitly named per-coroutine inspection API | Mirrors historical KM10's idea of querying a designated coroutine; existing root metadata stable | Requires API, registration, security/validity and new global-number review; worker-local plain `STACKHWM` would otherwise report root usage |

**No option is selected here.** The historical evidence **does not** show that KM10's G54/G55 semantics can be adopted directly in the reconstructed runtime.

## 3. Native assembler service seam: call frame and R6 continuation

**SOURCE-OBSERVED:** `richards-bcpltape/bcplib/bcpl/cg` `CGAPPLY` builds R15 from caller frame R5 and emits `BALR 6,4`; `CGSAVE` emits `STM` at `0(R15)` and can emit the checked-entry `BAL 14,60(11)` plus inline fullword. Register identities are set in `cghdr`: R4=`R.B`, R5=`R.P`, R6=`R.L`, R7–R10=arguments, R11=system vector, R12=global vector, R14=checked-entry linkage, R15=`R.W`.

**SOURCE-OBSERVED:** `bootstrap-toolchain/asm/bcplmem.asm` provides a **direct assembler BCPL-callable** example. `GETVEC` does not enter `STKIMPL`; it preserves caller R5/R6/R15 as needed for its operation and returns via `L 4,0(5)` / `BCR 15,6`, with result in R7. `bootstrap-toolchain/asm/bcplapt.asm` provides a *different* model: `APTOVEC` saves linkage at `0(R15)` and executes `LR 5,15` because it needs a new BCPL frame for its nested call. These are **different valid integration patterns**, not interchangeable routines.

**Candidate entry choices to investigate (not an approved `CHANGECO` ABI):**

| Approach | Positive | Verification required |
| --- | --- | --- |
| E1 — Direct assembler primitive analogous to `GETVEC` | Can retain caller frame R5 and suspend at the R6 continuation while returning delivered value in R7 | Capture/restore actual R4/R5/R6 and other live state; define current-context record and safe atomic S1 installation |
| E2 — Compiled BCPL wrapper with private machine-dependent switch | BCPL-level lifecycle and a normal compiled activation record can host control logic | Prove the wrapper's extra frame, continuation and R7 delivery; avoid suspending a nonreentrant helper half complete |

The source does not prove what the final switch must preserve in R10/R14/PSW condition code. It also does not establish the worker's never-run frame: historical `COENTRY`/`COHOLD`/`COSTART` are suggestive only. A candidate first-entry trampoline must be tested using **actual native CG370-generated** code and checked `STKIMPL`, rather than reproducing MR10 INTCODE `P/C` offsets.

## 4. S1 stack-limit implications beyond STKLIM

**SOURCE-OBSERVED:** `bootstrap-toolchain/asm/bcplmain.asm` uses `STKLIM` for checked entry and initializes external `BCPLAPT` `APLIMIT` at startup. `BCPLAPT` tests the dynamic vector end against `APLIMIT` and separately rejects `N > 16380` using constant `APMAXN` (in `bcplapt.asm`). This hard `APMAXN` cap is **not derived dynamically** from the incoming coroutine's capacity.

**Inference:** With independently sized worker stacks, coordinating `STKLIM` and `APLIMIT` is essential, but larger worker allocations would still be subject to the legacy `APMAXN` policy. Define initial worker sizes and whether keeping this cap is acceptable; no relaxation is authorized. Both stack-limit updates, any G54/G55 updates, and saved context restoration must form one no-BCPL-call transition. For invalid or busy targets, reject *before* mutating active state. No general asynchronous or thread safety is inferred from cooperative scheduling.

## 5. Native acceptance qualifications from existing regression records

`tests/bootstrap/01-one-procedure-call/README.md` records first minimal native call/return acceptance in JES JOB 950 (6 October 2026), with IFOX, IEWL and GO RC=0000. Its quoted `RETIMPL LM 4,6,0(5)` reflects the **older test-era source**; current `bootstrap-toolchain/asm/bcplmain.asm` uses `L 6,8(5)`, `L 5,4(5)`, `L 4,0(5)`, then `BCR 15,6`. The historical test record is bounded evidence for its test-era build, **not** verification of the current coroutine context switch or a saved current-HEAD listing.

`tests/bootstrap/093-aptovec-stack-overflow/README.md` describes profile-specific expected returns. The tracked `expected-go-rc-bcplm6.txt` contains `0000` for BCPLM6/D6; the tracked generic `expected-go-rc.txt` contains `0012` for D7/BCPLM7. Both require `STACK OVERFLOW` and no execution of the designated callee. Do **not** set a universal expected native overflow RC in CO.1 or silently change accepted per-profile fixtures. Future candidate probes must name the exact linked runtime/profile and verify actual JES return and diagnostic behavior.

## 6. Suggested next isolated evidence and owner decisions

1. **Offline actual-listing inspection:** obtain and analyze current-revision CG370-native assembly for a two-argument procedure and a nested-call/suspend-shaped application. Label `CGAPPLY`, `CGSAVE`, return, live R7–R10, frame metadata, and any spills. No archived test-era snippet may substitute for this.
2. **Entry-seam owner choice:** select E1 or E2 after the listing analysis; settle precise R6/R5, first-entry trampoline, result-in-R7, and save-set contracts.
3. **Active bounds owner choice:** decide D1 vs D2 and consistency of `STKLIM`, `APLIMIT`, and `APMAXN`; document root ownership and restore policy.
4. **Design gate:** approve descriptor/stack layout, lifecycle/cleanup, native global registry and candidate-only IFOX/IEWL/GO/JES probe sequence; then separately authorize native tests and CO.2 implementation as applicable.

**Verification classification:** Source string/fixture assertions and Git document consistency checks only; no native coroutine IFOX, IEWL, GO, JES or installed MVS result. **CO.1 stays IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
