# CO.3 — DELETECO / registry revocation / storage reuse candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Status:** Offline-tested source candidate; new native MVS evidence pending.

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
list head/middle/tail unlinking, and repeated registry slot reuse. The
successful case requires exact output, six zero-RC native JES steps and
runner RC=0. Full reports stay under `workarea/co3-delete-reuse/`.

## Explicit remaining gates

- MVS Cambridge/IFOX/IEWL/GO evidence for this candidate is **pending**.
- No real same-address `GETMAIN` reuse, stale-pointer safety or production
  generation-token ABI is claimed. The separate CO.1 token experiment
  remains the evidence for bounded same-address identity separation.
- Broader CO.4 robustness and CO.5 integration/release are NOT STARTED.
- CO.3 cannot close without separate owner acceptance.
