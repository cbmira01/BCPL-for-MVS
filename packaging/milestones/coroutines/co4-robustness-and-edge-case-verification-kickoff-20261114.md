# CO.4 — Robustness and Edge-Case Verification: kickoff and handoff

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification  
**Status:** **IN PROGRESS**  
**Opened:** 14 November 2026 (Louisville local time)  
**Authority:** [CO.3 qualified owner acceptance](co3-formal-acceptance-and-co4-transition-20261114.md)  
**Source authority:** GitHub `main`; verify HEAD before making changes

## Mission and official gate

Verify native System/370 BCPL coroutine robustness across
**stack boundaries, recursion, repeated switches, allocation
exhaustion, invalid/active/stale descriptors, cleanup and error paths**.
The official gate is **focused positive/negative evidence with no
newly broken runtime invariants**. Work within the bounded,
owner-accepted CO.1/CO.2/CO.3 candidates; do not imply a frozen public
ABI, unrestricted pointer validity or generalized error recovery.

The Cambridge compiler remains INTCODE-hosted; it emits native S/370
code executed under MVS 3.8J. Native self-hosted compiler completion
is not a prerequisite.

## Accepted starting baseline

GitHub `main` at the qualified CO.3 closure and transition commit is
the new documentary baseline. Preserve and refer to the three distinct
native CO.3 evidence receipts:

| Area | Native JOB | Strict oracle | Evidence |
| --- | --- | --- | --- |
| First lifecycle | 5386 | 8 records | `co3-first-lifecycle` |
| RESUMECO parent chain | 5392 | 13 records | `co3-first-lifecycle` |
| DELETECO and registry reuse | 5397 | 21 records | `co3-delete-reuse` |

Full receipt paths and individual compiler jobs are in
[CO.3 closure](co3-formal-acceptance-and-co4-transition-20261114.md).

Source boundaries:
- `bootstrap-toolchain/asm/bcplco.asm` — separately assembled,
  accepted candidate machine context-switch mechanism (CO.2).
- `packaging/milestones/coroutines/candidates/co3-delete-reuse/`
  — independent BCPL library, private IFOX unregister extension and
  the latest positive-path native fixture.
- `tools/coroutines/run-co3-first-lifecycle.py` and
  `tools/coroutines/run-co3-delete-reuse.py` — guarded native runners.
- `bootstrap-toolchain/asm/bcplmain.asm`, `bcplmem.asm`,
  `bcplio.asm` — source contracts; installed `BOOT_OBJ` is read-only.
- `packaging/architecture/runtime-contract-v1.md`,
  `stack-check-contract.md`,
  `runtime-and-library-nomenclature.md` and
  `global-number-registry.md` — architectural constraints.
- `coroutine-research-and-design-gates.md` and the milestone record
  — behavioral provenance, qualified acceptance boundaries.

## Initial work: evidence-first, no change of ABI by default

1. **Reconfirm baseline and map actual failure surfaces.**
   Read the accepted `BCPLCO`, candidate `CO3DROP`, `CO3BOOT`,
   `BCPLMEM` and checked-entry implementation; identify recoverable
   versus unsafe-to-probe failures and the minimal safe sentinels.
   Inventory the available host test runners and existing MVS oracles.
2. **Prepare an owner-reviewable CO.4 verification matrix.**
   Classify stack-boundary/guard checks, nested recursion,
   many sequential switches, valid/busy/active/terminated target
   refusals, worker deletion while suspended, allocation capacity,
   partial allocation rollback, registry-slot reclamation and cleanup.
   For each case define the exact supported precondition, expected
   result/status, rollback invariant, permitted side effects,
   machine oracle and evidence type.
3. **Start with safe known-live positive and negative probes.**
   Verify frame/stack state and root `STKLIM`/`APLIMIT`/G54/G55
   restoration under repeated transfers. Exercise known-live invalid
   states **without dereferencing arbitrary or freed addresses**.
   Keep a bounded suite and preserve previous oracle receipts.
4. **Separate risky design decisions.**
   Identical-address reuse, generation-token or opaque-handle schemes,
   stale-pointer recovery, overflow policy, cancellation semantics,
   exceptional teardown and larger worker counts are **not** silently
   approved by CO.3. Propose alternatives and ask for owner decisions
   before changing the ABI or creating tests likely to abend.
5. **Verify with MVS, not just host models.**
   Write real BCPL fixtures, IFOX where machine-specific, JCL in
   temporary datasets, and strict JES/IFOX/IEWL/GO oracles; run host
   syntax/manifest/unit checks before operator MVS trials. Record
   failed attempts separately, including exact job numbers and
   underlying observed output. Use the owner's WSL checkout only for
   guarded fast-forward pull and MVS-facing test execution.

## Acceptance requirements and controls

Maintain existing native positive paths with source-revision-tracked
results. Test boundary conditions and refusal paths without unsafe
assumptions; do not claim full recovery from arbitrary machine
addresses, stale references or unrecovered MVS abends. For any
recovered failure, demonstrate that current context, worker registry,
allocated vectors and root stack bounds remain valid. No hidden
resident-MVS-only patches.

The private registry remains two-worker, the descriptor layout is
candidate-only, worker stacks are fixed at 1024 safe words plus
256-byte clearance, and native G!289–300 are temporary. Retain
Approach A and S1 unless the owner explicitly chooses a replacement.

Do not renumber historical tests, add public global assignments,
overwrite installed `BOOT_OBJ`, commit/push unrelated changes, or
start CO.5 without a separately accepted CO.4 closure. Any
installation, release or permanent API promotion needs separate
authorization. GitHub `main` remains authoritative.

**CO.0–CO.3 CLOSED (qualified); CO.4 IN PROGRESS; CO.5 NOT STARTED.**

**Immediate next step:** source-grounded CO.4 verification matrix and
first minimal, bounded native test proposal for owner review;
avoid prematurely implementing a new descriptor or public handle API.
