# CO.3 — DELETECO / registry revocation / storage reuse candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Status:** OWNER-REPORTED NATIVE-MVS-TESTED; JOBS 5395–5397 PASS; qualified acceptance pending.

## Scope and provenance

The separately compiled BCPL `library.bcpl` is the bounded candidate
successor to the first-lifecycle library. It retains `CO3INIT`, `CREATECO`,
`CALLCO`, `COWAIT`, `RESUMECO`, and `CO3BOOT`, and adds `DELETECO` at
**test-local G!291**. The private IFOX `CO3DROP` entry at **test-local G!300**
revokes a known-live idle worker before BCPL calls `FREEVEC` on its independent
stack and descriptor. Neither global assignment is a public ABI allocation.

The `co3drop.inc` extension is inserted into a **temporary assembly stream**
for the source-verified `bootstrap-toolchain/asm/bcplco.asm`. The accepted
CO.2 IFOX source is **not edited**. The native driver reuses the tested CO.3
independent BCPL compilation/export, four IFOX object steps, IEWL and GO
pipeline with read-only installed `BOOT_OBJ` and temporary MVS datasets.

The lifecycle contract is explicitly bounded:

- Root creates/deletes. At most two registered live worker descriptors.
- `DELETECO(C)` rejects null, non-member, root, current, parent-attached or
  parent-referenced descriptors. A suspended but inactive worker whose
  `C!25=0` may be removed from any position in `CO3LIST`.
- IFOX first checks root-active and registry membership **before** reading
  the worker descriptor. It accepts only worker state 2, checks no live
  parent references, marks state 4 (revoked), then clears the registry slot.
- Only after successful unregister does BCPL unlink the worker and call
  `FREEVEC(stack)`, then `FREEVEC(descriptor)`. No freed stack remains active.
- A subsequent `CREATECO` may reuse the vacated **registry slot** and may
  obtain new storage from MVS. The test does **not** require reuse of an
  identical physical address; any such address reuse is allowed.
- Approach A remains in force: **stale raw pointers after address reuse are
  not supported**. No stale handle is passed to `CALLCO`, `RESUMECO`,
  `DELETECO` or raw `CHANGECO` after successful deletion. General ABA-safe
  identity requires a separately designed generation-token/opaque-handle ABI.
- This candidate is static and nonreentrant, has fixed 1024-word safe
  worker stacks plus 256-byte clearance, and does not free the root.

## Focused native verification

`tools/coroutines/run-co3-delete-reuse.py --run` submits a separate
application compiler job, library compiler job, and an isolated native job
with four IFOX steps, IEWL, and GO. The exact **21-record** oracle is:

    MADE FULL A1 RA B1 RB DELA C1 RC B2 RB2 DELB
    C2 RC2 DELC D1 RD D2 RD2 DELD PASS

Each token above must appear as a complete, separately flushed
`CO3BCPL <token>` application record in the stated order.
`WRCH(10)` is used for the tested `BCPLIO` native newline operation.

The fixture verifies a refused third registration at capacity, an active
worker's refusal to self-delete, two suspended-worker removals, continued
operation of the other live worker, normal return followed by deletion,
list head/tail unlinking, and repeated registry slot reuse. The
successful case requires exact output, six zero-RC native JES steps and
runner RC=0. Full reports stay under `workarea/co3-delete-reuse/`.

## First owner attempt: hard-coded import/export adapter mismatch

On 14 November 2026, the initial native deletion/reuse attempt from
GitHub `main` at `4565e9f6aca065fc3193ec7e044dc06055531a08`
reported `CO.3 first lifecycle FAIL: BCPL library imports changed`
at `workarea/co3-delete-reuse/20261114T235000Z-zvui6mmb`.
The independent Cambridge compiler jobs had produced their listings,
but the adapter rejected the generated application before native
JCL submission; no IFOX, IEWL or native GO result was produced.

Root cause: the qualified CO.3 runner expands global trailer exports
using its dynamic `EXPORTS` tuple, but its application `EXTRN` and
library `ENTRY` cards retain a literal five-function symbol list.
The deletion adapter expected six imports and therefore refused
the otherwise valid output. The candidate adapter now requires
the exact baseline five-function cards, expands both to include
`C3DELETE`, and checks its compiler-generated `EQU` alias before
submitting the native deck. No change to the qualified base runner,
accepted BCPLCO, installed objects or public globals is made.

## Native MVS PASS: JOBS 5395–5397

On 14 November 2026 local time (15 November UTC), the owner ran
`tools/coroutines/run-co3-delete-reuse.py --run` from `main` at
`1875b26110dae6b19be05cf77a150cb54a1bb392` and reported:

    CO.3 first lifecycle PASS: compiler JOBS 5395/5396,
      native JOB 5397; IFOX 4, IEWL 1, GO 1
    CO.3 deletion/reuse verification RC=0

Operator-local receipt:
`workarea/co3-delete-reuse/20261115T000019Z-nc9zruc0`.
The strict runner requires all six IFOX/IEWL/GO steps RC=0000,
JES job SUCCESS, and the exact 21 ordered `CO3BCPL` records
listed above. This pass supersedes the pending-native status of this
candidate, **not** the separately recorded failed adapter attempt.

The MVS pass is evidence for unregister-before-release, list
maintenance, surviving-worker continuity, capacity refusal and
registry-slot reuse. The first and parent-chain fixtures retain
their independent earlier PASS records.

## Explicit remaining gates

- The owner-reported Cambridge/IFOX/IEWL/GO candidate PASS is recorded in the
  [JOBS 5395–5397 evidence record](../../co3-delete-reuse-jes-5395-5397-pass-20261114.md).
  The complete JES reports remain operator-local.
- No real same-address `GETMAIN` reuse, stale-pointer safety or production
  generation-token ABI is claimed. The separate CO.1 token experiment
  remains the evidence for bounded same-address identity separation.
- Broader CO.4 robustness and CO.5 integration/release are NOT STARTED.
- CO.3 cannot close without separate owner acceptance.
