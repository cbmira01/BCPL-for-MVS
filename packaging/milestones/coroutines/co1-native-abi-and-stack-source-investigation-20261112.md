# CO.1 — Native ABI and Stack Architecture: source investigation checkpoint 1

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Status:** IN PROGRESS; design gate OPEN
**Date:** 12 November 2026
**Source HEAD:** `cb2620293e0efd7bbd6f71b00469646c02b845b1`
**Evidence class:** SOURCE-OBSERVED unless marked as inference/proposal; no new native MVS execution.

## Scope and authority

The owner authorized CO.1 **investigation and documentation**, and a GitHub `main` commit. [CO.0 formal closure](co0-formal-closure-20261112.md) remains accepted with qualifications; CO.2–CO.5 remain NOT STARTED. The [governing milestone](milestone-implement-coroutine-support-for-native-compiler.md) requires an owner-reviewed **native design and isolated probe plan before implementation**. No native `CHANGECO`, descriptor offsets, global assignments, resident MVS changes, JES submission or native acceptance is authorized by this checkpoint.

Keep the owner-selected **Approach A** (opaque valid/live descriptor pointers; arbitrary/stale/freed pointers unsupported; managed handles deferred) and **S1** (independent stacks with switching of the active safe limit; S2 deferred). A native Core Runtime switch and separately compiled BCPL coroutine library are the architectural direction; historical BLIB modification is not assumed. The [nomenclature](../../architecture/runtime-and-library-nomenclature.md), [runtime contract](../../architecture/runtime-contract-v1.md), [stack-check contract](../../architecture/stack-check-contract.md), [Global Number Registry](../../architecture/global-number-registry.md) and [research gates](coroutine-research-and-design-gates.md) remain authoritative.

## 1. Actual CG370 call and return evidence

Source anchors: `richards-bcpltape/bcplib/bcpl/cghdr` lines 163–165; `richards-bcpltape/bcplib/bcpl/cg` lines 652–675, 688–731, 2238–2255; `bootstrap-toolchain/asm/bcplmain.asm` lines 344–373, 464–475, 548–589.

| Register | SOURCE-OBSERVED role | CO.1 question |
| --- | --- | --- |
| R1–R3 | Generated section addressing constants 4096/8192/12288 | Preserve code addressing across transfers |
| R4 | CG370 `R.B`, callee entry; restored from word 0 of frame | Initial frame and suspended frame linkage |
| R5 | `R.P`, active BCPL frame | Distinct persistent activation chains |
| R6 | `R.L`, return continuation set by `BALR 6,4` | Resume point for suspended call |
| R7–R10 | `R.A1`–`R.A4` arguments; R7 also result | Prove liveness, including R10 |
| R11 | `R.S`, system vector; stack check at +60 | Restore system-vector identity |
| R12 | `R.G`, global-vector base | Preserve global access |
| R13 | MVS save-area register in BCPLMAIN | Not available as arbitrary coroutine scratch |
| R14 | `R.A`, checked-entry linkage to inline frame-size word | Separate from R6 return linkage |
| R15 | `R.W`, candidate next-frame/workspace address | Separate from R6 continuation |
| Condition code | No complete coroutine-visible contract identified | Examine generated branches and probe |

`CGAPPLY` computes R15 from the current R5 and call-site displacement, installs callee address in R4, then emits `BALR 6,4`. `CGSAVE` emits an `STM` from R4 at `0(R15)`; with stack checking it emits `BAL 14,60(11)` and an inline fullword set by `GENSTKCK2` to `BASEFRMSIZE*4`. The runtime `STKIMPL` loads that full *callee* frame size, performs the bound check, sets R5 from R15, restores R4 and skips the inline fullword. The native `RETIMPL` sequence restores R6 from `8(R5)`, R5 from `4(R5)`, R4 from `0(R5)` and branches to R6. The first native activation/trampoline must obey these contracts; **MR10's INTCODE synthetic-frame offsets are not a native ABI**.

This source trace does **not** select a coroutine save set or establish R14/PSW behavior at arbitrary suspension points. Use actual generated listing evidence before declaring either.

## 2. Material S1 finding: two active stack-limit consumers

Source anchors: `bootstrap-toolchain/asm/bcplmain.asm` lines 69–104, 210–222, 317–324, 564–575; `bootstrap-toolchain/asm/bcplapt.asm` lines 13–49.

The current tracked BCPLMAIN obtains 68,592 bytes: 2,800 for globals, a 65,536-byte painted root stack, and 256-byte reserved clearance. It sets `DYNWORK`, `STKLIM=DYNWORK+65536`, `DYNEND=STKLIM+256`. `STKIMPL` checks the full generated callee frame against `STKLIM`, using `BH STKOVFL` for overflow.

**Crucially, the tracked source registers external `BCPLAPT APTOVEC` at G40 and initializes its exported `APLIMIT` from root `STKLIM`.** `BCPLAPT` separately compares temporary-vector space against `APLIMIT`. Thus simply switching R5 and `STKLIM` would leave `APTOVEC` checking the wrong coroutine stack.

**Design inference for review:** a single private active-stack installer should coordinate `STKLIM`, `APLIMIT`, stack bounds reporting and frame-state transfer. There must be no checked entry or temporary-vector call while these invariants disagree. Exact ordering, private linkage, rollback and context save set remain CO.1 design questions.

**Versioned-source discrepancy:** `packaging/architecture/runtime-contract-v1.md` still describes an earlier **internal** G40 `APTOVEC` and B-APT-01 as a deferred external integration gap. Current `bcplmain.asm` explicitly initializes and registers **external** `BCPLAPT`. That is verified source evolution, **not** proof that a particular installed resident object follows the new path. Reconcile build provenance and target-link behavior before changing the accepted runtime contract or claiming target acceptance.

## 3. STACKBASE / STACKEND / STACKHWM

Source anchors: `bootstrap-toolchain/asm/bcplmain.asm` lines 81–104, 210–222; `richards-bcpltape/bcplib/bcpl/blib` lines 227–239.

G54 `STACKBASE` is `DYNWORK>>2` and G55 `STACKEND` is `DYNEND>>2`, both **BCPL word addresses**. G55 includes reserved clearance, **not** the safe check limit. BCPLMAIN paints alternating `EVENSTACK`/`ODDSTACK` words within the safe region; `STACKEND-2` is a marker guard in clearance and `STACKEND-1` stores the upper initialized paint pointer.

Historical BLIB `STACKHWM` checks both clearance words and scans backward toward `STACKBASE` to return a word address or `OVERFLOW=0` / `UNSET=1`. The paint guard is not hardware protection, and existing regression evidence does not prove exact high-water accuracy for all workloads.

**Proposed, not approved:** independently allocate, paint and initialize clearance for each worker. Report G54/G55 for the **active** coroutine so the unchanged G56 scanner can examine it. Preserve and restore original root G54/G55 along with both active safe limits. Verify root-to-A-to-B-to-root restoration, initial/suspended high-water reports, equality and one-word-over limit. Worker stack capacity and guard sizing remain open.

## 4. Ownership, lifecycle, failure and native registration

Source anchors: `bootstrap-toolchain/asm/bcplmem.asm` lines 1–159; `bootstrap-toolchain/asm/bcplmain.asm` lines 493–543; [Global Number Registry](../../architecture/global-number-registry.md).

`BCPLMEM GETVEC(N)` allocates `4*(N+1)+12` bytes (N+1 payload words plus its 12-byte private descriptor), returns a BCPL word pointer and tracks allocations in a static **nonreentrant** singleton. `FREEVEC` releases known exact pointers; `MEMDRAIN` reclaims remaining live vectors on normal termination. Candidate separate descriptor/stack allocations require agreed ownership, bounded size arithmetic, initialization and partial-failure rollback. Never free the executing stack or a stack retaining a reachable suspended continuation.

The current `STKOVFL` message path enters FINISH; accepted runtime documentation records possible `STACK OVERFLOW` with MVS RC=0. Invalid checked frame metadata has a separate RC=36 early-return path that bypasses ordinary explicit cleanup. No coroutine-local overflow recovery is established. Choose and verify a bounded initial termination/error policy.

MR10's G6–G8 and G91–G95 collide with historical Cambridge LIBHDR (G6 SAVEAREA, G91 RESULT2, etc.). System Extensions own G200–G203; G150 has a known native compiler conflict. **No native coroutine global is assigned here.** A source `GLOBAL` declaration, IEWL object inclusion and compiled-BCPL registration trailer must be checked separately against the effective executable exports.

## 5. CO.1 unresolved design questions

| Gate | Decision required before CO.2 |
| --- | --- |
| Native machine state | Save/restore set and precise R4/R5/R6/R7–R10/R11/R12/R14/R15 and condition-code obligations |
| First entry | Legitimate worker frame and first-entry continuation/trampoline |
| Descriptor | Root vs worker identity, private fields, parent and busy/idle/return states |
| Stack bounds | GETVEC storage sizes, metadata/clearance, paint, alignment, overflow arithmetic |
| S1 installation | Private interface and consistent `STKLIM` / `APLIMIT` / G54 / G55 restoration |
| Diagnostics | Active-stack G54–G56 vs root-only contract; how and when to report HWM |
| Globals/linkage | Collision-free assignments, BCPL export trailer, Core Runtime registration |
| Cleanup/failures | Valid-live-pointer contract, worker return/re-entry, deletion, out-of-storage, fatal overflow |

## 6. Isolated verification sequence (planned only)

| Phase | Candidate test | Evidence requirement |
| --- | --- | --- |
| A — offline | Inspect actual generated native CG370 listings around nested calls and checked entry | Code listing, source revision, annotated register liveness |
| B — native ABI | Isolated IFOX/IEWL/GO call/return and R7-result probe without installed object changes | Generated code, IFOX/IEWL severities, GO and JES RCs |
| C — stack bounds | Two candidate stacks, exact-fit/one-word-over, `STKIMPL` + `BCPLAPT` and root restoration | Actual check-path outcomes and diagnostics |
| D — first transfer | Approved trampoline: root → worker → root | Saved frames, continuation, transfer value |
| E — oracle transfers | Native adaptations of interpreted JOB 5331 (8), JOB 5332 (14), JOB 5333 (18) | 40 exact native output records and *native* JES receipts |
| F — lifecycle/regression | Busy/live targets, worker return/re-entry, safe deletion/rollback and existing suite baselines | Candidate-only linkage and per-suite results with expected SKIPs preserved |

No stage authorizes JES submission by itself. B–F need explicit MVS execution approval; D–F additionally depend on CO.1 design approval and appropriate implementation gates. Interpreted 12/12 JES-step counts must not be copied into native expected results. No test IDs, manifests or installed MVS datasets were changed.

**Disposition:** CO.1 IN PROGRESS — SOURCE-OBSERVED analysis only; native design acceptance pending; CO.2–CO.5 NOT STARTED.
