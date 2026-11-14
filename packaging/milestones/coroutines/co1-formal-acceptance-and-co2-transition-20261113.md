# CO.1 — Native ABI and Stack Architecture: qualified owner acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture  
**Decision:** CLOSED — qualified owner acceptance and authorization to start CO.2  
**Owner decision date:** 13 November 2026 (Louisville local time)  
**Source reviewed:** GitHub `main` at `1c42c02b360c933318f85cfb61e6c64b341c58e6`

## Decision and verification basis

The owner explicitly directed: **“Move directly to CO.1 acceptance without
delay. Begin CO.2 without further delay.”** This is acceptance of a
**bounded CO.2 engineering baseline**, not a declaration that every
candidate-only interface has become the production ABI.

CO.0 — Historical Research and Behavioral Contract remains CLOSED
(qualified). CO.1 closes with the qualifications below, and
**CO.2 — Native CHANGECO Implementation begins IN PROGRESS**.
CO.3–CO.5 remain NOT STARTED.

CO.1 source work established the actual CG370 calling and return
conventions: BCPL R4 entry, R5 frame, R6 continuation, R7 value,
R11 system-vector return/check entry, R12 globals, and R15 workspace;
the accepted /CN path uses three saved-frame words, not the
MR10 INTCODE descriptor layout. The working native candidate
preserves all 16 GPRs in a private context image. Separate worker
stack limits must coordinate `STKLIM` and `APLIMIT`, as well as
G54 `STACKBASE` and G55 `STACKEND`, before resuming checked
BCPL code. Root state must be restored.

The series of OWNER-REPORTED NATIVE-MVS-TESTED isolated candidates
includes single worker and recursive checked frames (through JOB
5361), two simultaneously live independent worker stacks (5362/5363),
direct worker-to-worker transfers (5364/5365), natural termination
and rejected re-entry (5366/5367), bounded membership validation
(5368/5369), revoke-before-`FREEVEC` (5370/5371) and
generation-token same-address lifetime separation (5372/5373).
The last successful receipt: compiler JOB **5372**, native GO
JOB **5373**, IFOX 3, IEWL 1 and GO 1 all RC=0000,
ordered `A1 R1 A2 R2 PASS`, runner RC=0. Full printer reports
were retained by the owner; they were not independently reviewed
by the assistant.

## Accepted CO.2 implementation direction

1. **Core Runtime ownership:** implement a separate IFOX native
   context-switch module. Do not modify historical BLIB or the
   installed `BOOT_OBJ` objects in the CO.2 candidate stage.
2. **Initial descriptor policy:** retain the previously owner-selected
   **Approach A**, opaque to BCPL clients but requiring valid, live
   descriptor references. Do not claim recovery from arbitrary,
   freed, or concurrently modified pointers. Generation tokens
   from JOB 5373 are comparative research, **not** the accepted
   initial public handle ABI.
3. **Stack policy:** retain previously owner-selected **S1**,
   independently allocated worker stacks with coordinated
   `STKLIM`/`APLIMIT`/G54/G55 installation and checked-entry
   compatibility. Preserve the root limits and synthetic initial
   caller frame/ordinary compiler return linkage.
4. **Context transfer:** preserve compiler-visible register and
   continuation semantics, pass values in R7, and use the ordinary
   native `RETIMPL` convention. The 24-word candidate descriptor,
   singleton `CO1SREG`, trampoline and error values are proven
   *candidate mechanics*, not a frozen release ABI. No subtasks or
   preemptive transfer.
5. **Lifecycle ownership:** later BCPL library management routines
   belong in a **separate BCPL coroutine library**, not assumed
   historical BLIB. Use existing `BCPLMEM` `GETVEC`/`FREEVEC`
   where appropriate. Never free an active stack or a stack with
   reachable suspended frames. More complete parent chains,
   `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT` and `RESUMECO`
   remain the separate CO.3 gate.
6. **Global numbers and public API:** **no permanent coroutine
   global slots or public API are approved by this qualified
   closure**. CO.2 can assemble and link a private isolated module
   with test-local G!295–299 only. Before *production* global
   registration, module promotion or a public library implementation,
   a separately reviewed, collision-free allocation and callable
   API must be approved against the Global Number Registry.
   Historic MR10 slots G6–G8 and G91–G95 must not be reused.
7. **Diagnostics:** preserve unchanged checked stack overflow,
   `STACKHWM`/guard conventions and current native runtime
   diagnostics; no candidate may claim safe arbitrary overflow
   recovery without target-native evidence.

## Acceptance qualifications, not silently resolved

This is **qualified** rather than unconditional acceptance against
the milestone's original full CO.1 gate. The precise production
descriptor structure, final public interface/global assignments,
lifecycle error policy, all PSW/condition-code obligations, and
production-safe pointer/ownership protocol were **not fully
approved or verified**. Those items remain explicit hold points
**before any production runtime or public API promotion**, and
CO.2 must not describe them as settled. The owner-directed transition
authorizes bounded implementation and native testing *now*, rather
than additional speculative CO.1 probes.

No new native JES run, installed MVS dataset change, production object
promotion, regression renumbering, or release action occurred in this
documentation decision.

**Disposition: CO.1 CLOSED (qualified); CO.2 IN PROGRESS;
CO.3–CO.5 NOT STARTED.**
