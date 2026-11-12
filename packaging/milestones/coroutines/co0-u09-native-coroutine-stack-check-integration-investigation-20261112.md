# CO.0 — Native coroutine stack-check integration source investigation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Source checkpoint:** GitHub `main` at `64f65d300e7ee3711206bb315137ee14f61c18b2`  
**Status:** SOURCE-OBSERVED implementation investigation; proposed CO.1 verification requirements, **not** approved stack architecture.

## Decision already made; question still open

The owner selected **Approach A**, valid-live **pointer descriptors**,
for the initial native coroutine release, deferring generation-validated
handles to future research. See the
[CO0-U09 owner-decision record](co0-u09-native-coroutine-ownership-and-stack-decision-briefing-20261112.md).
This does **not** settle independent stack allocation, limit selection,
stack metadata restoration or native context switching.

The next decision is how a coroutine's independent stack bounds interact
with the current BCPLMAIN **S.STKCK** implementation.

## Source observations

- [`bootstrap-toolchain/asm/bcplmain.asm`](../../../bootstrap-toolchain/asm/bcplmain.asm):
  the current startup obtains a single block for a 700-word global
  vector, 65,536-byte working stack, and 256-byte clearance. It
  initializes `DYNWORK`, `STKLIM`, `DYNEND`, paints the original
  working stack, and publishes native `STACKBASE`/`STACKEND` in G54/G55.
  The reserved clearance is not available coroutine working storage.
- **Actual stack-check instruction path:** `SYSSTK` routes
  `S.STKCK` to `STKIMPL`; `STKIMPL` uses the inline frame-size
  word and compares the candidate frame end against the single
  runtime-local `STKLIM` field (via `C 4,STKLIM`; `BH STKOVFL`).
  This is a **single current bound**, not already a per-coroutine map.
  Consequently merely changing R5 to a different stack region is
  insufficient: checked procedure entry would still compare with the
  prior `STKLIM`.
- [Native runtime contract](../../architecture/runtime-contract-v1.md):
  R5 denotes the current BCPL frame, R6 return linkage, R7–R9
  arguments/results, R4 is restored from the caller frame, R11 is the
  system-vector base. `STKOVFL` currently reports a controlled
  `STACK OVERFLOW` and enters the termination path; safe recovery
  of only the offending coroutine is **not** established.
- [Historical stack-check checkpoint](../../architecture/stack-check-contract.md):
  historical material distinguishes `STKBASE`, `STKLIM` and
  `STKHIGH`; the original low-level `STKCK` body is missing.
  The native Test 52 observation shows that the caller next-frame
  displacement can be smaller than the callee's required frame size.
  The native check must continue using the **full inline callee size**.
- [`bootstrap-toolchain/asm/bcplmem.asm`](../../../bootstrap-toolchain/asm/bcplmem.asm):
  GETVEC/FREEVEC use MVS GETMAIN/FREEMAIN, tracked by a static
  non-reentrant singleton allocator. A coroutine switch is cooperative
  but does not alone prove that an allocator operation can be suspended
  safely; CO.1 must define allocation/switch serialization.
- [Accepted CO0-U08 oracle matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md)
  proves three distinct interpreted behavior scenarios (40/40 records,
  JOBS 5331–5333), **not** native stack bounds or registers.

## Narrow CO.1 choice for owner review

Two potential ways to preserve per-coroutine **safe limits** while using
the existing checked-entry mechanism are:

**S1 — Switch the current runtime stack context.** Each context owns
an independent stack allocation and its safe and extent boundaries.
The context switch makes the incoming safe limit the active value read
by `STKIMPL`, and restores the outgoing limit when switching back.
Root-stack state must remain recoverable. The mechanism to update
these fields and expose `STACKBASE`/`STACKEND` consistently has not
been selected.

**S2 — Resolve current stack bounds indirectly during every check.**
`STKIMPL` consults a currently active context record to obtain the
safe limit. This centralizes context metadata but changes the
frequently executed stack-check path and requires proof of valid
initialization, register use, and no unintended behavior for ordinary
non-coroutine programs.

These alternatives do **not** prescribe a CSECT, data layout, global
slot or exact register-save set. Both must retain the original root
stack and **check against the current context's safe limit before
entering the next frame**. Stack extent for reporting is distinct from
the safe limit used for frame admission.

## Proposed evidence gates — no MVS execution claimed

1. Establish the exact generated call and checked-entry sequences,
   including the inline frame-size convention and register liveness,
   by inspecting compiler output and native IFOX/IEWL artifacts.
2. Prove a legacy non-coroutine native application still uses
   BCPLMAIN's original root stack bound and reports overflow correctly.
3. Exercise two different stack extents with boundary cases
   (fit, one fullword beyond limit) in isolated native tests; confirm
   that a switch cannot accidentally check one coroutine against
   another's `STKLIM`.
4. Verify root-to-A-to-B-to-root transitions preserve the current
   checked-entry bound and published stack metadata. Determine if
   `STACKHWM` is per-context or retains a root-only meaning; do not
   silently claim a historical answer.
5. Verify error handling on native stack exhaustion and allocation
   refusal, using the accepted runtime termination contract; no
   unsupported per-coroutine overflow recovery or arbitrary-address
   rejection is promised.
6. Only after owner approval of CO.1 architecture, adapt the accepted
   5331–5333 oracles to native compiled BCPL, preserving all
   8/14/18 exact ordered records. Use actual native JES step RCs
   rather than importing interpreter counts.

**Working preference for discussion, not an owner decision:** S1
may minimize changes to the established `STKIMPL` checked-entry
path; the risk is consistency of the active limit and published
stack diagnostics across every switch. S2 trades a single current
limit for explicit context lookup at every frame check.

**Disposition:** Approach A descriptor policy is recorded and does
not imply approval of either S1 or S2. CO.0 IN PROGRESS;
CO.1–CO.5 NOT STARTED. No native ABI, code, globals, datasets,
regression manifest or JES job were changed.
