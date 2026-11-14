# CO.2 — Native CHANGECO Implementation: qualified acceptance candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation  
**Prepared:** 14 November 2026  
**Decision status:** PROPOSED FOR OWNER REVIEW — **NOT ACCEPTED / NOT CLOSED**  
**Candidate implementation:** `bootstrap-toolchain/asm/bcplco.asm`  
**Last verified native test source:** `5f941bb34cc70649f0325bd73f42eeb67397c5d6`

## Proposed decision

Recommend **qualified CO.2 acceptance** for the isolated separate IFOX
Core Runtime context-switch candidate, for its verified *candidate-only*
behavior. CO.2's specified gate is a functioning native CHANGECO mechanism
with first transfer, multiple suspended contexts, checked nested BCPL
frames, continuation/result propagation and ordinary return, supported by
actual MVS IFOX/IEWL/GO evidence. The owner, not this record, decides
whether to close CO.2 and authorize the CO.3 — Coroutine Library and
Lifecycle transition.

The candidate is **not** approved for installation into accepted
`BOOT_OBJ`, assignment of permanent public global numbers, release
distribution, or general coroutine ABI publication.

## Evidence and gate mapping

| CO.2 obligation | Grounded evidence | Disposition |
| --- | --- | --- |
| Separate IFOX Core Runtime module | `bootstrap-toolchain/asm/bcplco.asm`: `BCPLCO`, `CO2INIT`, `CHANGECO` | Source present; assembles in both native runs |
| Actual Cambridge-generated BCPL | Compiler JOB 5374 and JOB 5378, `/CN` | Owner-reported PASS |
| Native IFOX, IEWL, GO | JOB 5375 and JOB 5379; three IFOX, one IEWL, one GO each; strict RC=0000 runner checks | Owner-reported PASS twice |
| First worker activation and valid frame return | Initial worker entry and natural return, both fixtures | Verified through behavioral oracle |
| Two independent live worker stacks | Root, A and B independent descriptors/stacks | Verified through two candidate applications |
| Direct worker-to-worker transfer | A/B and B/A in each test | Verified by ordered BCPL records and result checks |
| Checked nested frames and surviving locals | `NEST1(3)`, `NEST2(4)`, `DEEP1(4)`, `DEEP2(5)` | Verified by successful nested results |
| Multiple suspensions and continuations | JOB 5379 `X1 Y1 X2 Y2 X3 R1 Y3 R2 PASS` | Verified by strict nine-record oracle |
| R7 value passing and natural results | Both native fixtures check transfer and completion values | Verified at BCPL behavioral level |
| Root stack bounds restoration | Both fixtures compare G54/G55 after switches | Verified at BCPL behavioral level |
| Isolation from installed objects | Temporary ASM/IEWL/GO; existing `BOOT_OBJ` read-only | Source-verified runner contract; no install claimed |

The initial seven-record PASS and operator's preserved evidence are
recorded in [JOB 5374/5375](co2-native-changeco-jes-5374-5375-pass-20261114.md).
The independent nine-record PASS is recorded in
[JOB 5378/5379](co2-native-continuations-jes-5378-5379-pass-20261114.md).
The preceding `FVALUE` test-fixture failure and exact arithmetic repair
are preserved [separately](co2-native-continuations-failed-oracle-20261114.md),
not reclassified as successful.

The assistant has reviewed tracked source and the owner-provided console
receipts, **not** the complete local JES, generated assembler listings or
`result.json` for these runs. Both native evidence classifications are
OWNER-REPORTED NATIVE-MVS-TESTED. The successful runner evaluates
specified JES steps and behavioral markers, rather than providing a
proof of all possible machine states.

## Qualifications inherited from CO.1 and deferred gates

1. **No approved public descriptor or global ABI.** The 24-word
   descriptor, `CO2INIT`, `CHANGECO`, private two-worker registry,
   test-local G!295–299 and negative status codes remain candidate-only.
   Historic MR10 G6–G8/G91–G95 are not usable native allocations by default.
2. **Valid/live Approach A input and S1 independent checked stacks.**
   No claim of safety with arbitrary stale/freed pointers, address
   reuse, concurrent changes or deletion of active/suspended stacks.
3. **Stack limits.** The module writes `STKLIM`/`APLIMIT` and
   G54/G55 during context changes. The native tests verify checked
   entry and G54/G55 restoration but do not directly measure
   `STKLIM`/`APLIMIT` or establish `STACKHWM` precision under all loads.
4. **Machine context.** The code restores 16 general registers.
   Complete PSW/condition-code behavior is not separately proven
   by these BCPL fixtures. No reentrancy, preemption or MVS subtasks.
5. **CO.3 scope remains separate.** `CREATECO`, `DELETECO`,
   `CALLCO`, `COWAIT`, `RESUMECO`, parent chains, allocation
   ownership and reuse have not been implemented as a portable BCPL
   library by the CO.2 test implementation.
6. **CO.4/CO.5 remain independent.** Invalid active/stale targets,
   exhaustion, error recovery, complete native regression, clean-room
   reconstruction and release integration remain unaccepted.
7. **Production promotion hold.** Before a public library interface
   or production object install, decide the versioned callable ABI,
   collision-free global assignments, descriptor ownership and
   enforceable limits with separate owner authorization.

## Decision requested from owner

**Proposed:** Accept **CO.2 — Native CHANGECO Implementation** as
**CLOSED (qualified)** on the narrowly demonstrated native candidate
mechanics; then authorize **CO.3 — Coroutine Library and Lifecycle**
planning. This text is a proposal, **not** an acceptance record.
Until explicit owner approval, the authoritative milestone status stays:
**CO.0 CLOSED (qualified); CO.1 CLOSED (qualified);
CO.2 IN PROGRESS; CO.3–CO.5 NOT STARTED.**

No source code, installed object, permanent global-number registry,
historical BLIB or release artifact is promoted by this document.
