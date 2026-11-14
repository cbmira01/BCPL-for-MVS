# CO.1 — Revocation before FREEVEC: JOB 5370/5371 NATIVE PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026 (Louisville local date; UTC evidence on 14 November)  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED**, bounded two-worker revocation/release experiment  
**Disposition:** Isolated candidate PASS; production ABI/design gate OPEN; CO.2–CO.5 NOT STARTED

## Revision, execution and operator receipt

The owner's WSL checkout advanced to GitHub `main` at the exact tested
revision `2d24fcf6d8762e5381a84056ef17a378b3523923`. The
operator ran `tools/coroutines/run-co1-bcpl-revocation.py --run` and
reported:

```text
Git pull RC=0
HEAD=2d24fcf6d8762e5381a84056ef17a378b3523923
CO.1 BCPL PASS: compiler JOB 5370, GO JOB 5371; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-revocation/20261114T022204Z-g7e2s0wi
CO.1 revocation MVS runner RC=0
```

The inherited runner accepts only successful Cambridge compilation,
a completed `CO1BGO` native job, highest RC=0000, three IFOX
(`ASMA`, `ASMM`, `ASMS`) steps each RC=0000, IEWL `LKED` RC=0000,
GO RC=0000 and exactly the following ordered native BCPL records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The full compiler, assembler and JES reports remain in the owner's
local `workarea/` evidence directory; they were not independently
supplied to the assistant. The return-code and record claims are
based on the owner's actual runner receipt and the verified strict
runner oracle, not inferred independent printer inspection.

## Behavior established for the bounded experiment

The experimental IFOX module extends the verified two-worker registry
with a test-only `CO1DROP(worker)` entry bound to G!296 by the
candidate runner. It compares a requested address to live registry
entries before reading descriptor storage. It rejects the root,
unknown, active, new or suspended workers and already-revoked
references with test-only result `-2`. For a registered and inactive
`TERMINATED=3` worker, it sets `REVOKED=4`, removes that registry
entry, and returns zero.

The BCPL fixture specifically requires both workers to suspend,
worker A to resume and return 31, successful revocation of A **before**
`FREEVEC` of A's independent stack and descriptor, and both
`CHANGECO` and `CO1DROP` rejection of the saved old A pointer.
Worker B must still resume successfully, return 42 and satisfy the
same revoke-before-free and old-pointer rejection checks before the
final `PASS`. The root verifies its local sentinel during the
transfers and failures.

The native PASS therefore supports the specific two-worker
**revoke → free → reject-old-address** protocol while the module
does not register any new worker after deletion. It extends the
positive-path and invalid-target evidence through JOB 5369.

## Qualifications and next gate

The IFOX registry tracks bare descriptor addresses; it neither
tracks allocation generations nor prevents the same address being
registered later. The candidate deliberately **does not reuse** a
revoked registry slot, so it cannot prove safety in the ABA case
where MVS storage is reallocated at an old address.

The candidate's G!296 binding, `CO1DROP` name, `REVOKED=4` state,
`-2` negative result, fixed two-worker registry and static switch
scratch area are not approved production interfaces. No general
`DELETECO`, cancellation of a suspended worker, safe descriptor
address reuse, complete resource ownership model, arbitrary-pointer
validation, MVS subtask reentrancy or compiler-independent ABI
conformance is established here.

The run used temporary candidate objects/load datasets and read
accepted `BOOT_OBJ` members without installing or changing them.
No permanent global allocations, numbered regressions or release
assets were promoted.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
The next design gate remains owner review of production descriptor
identity/generation, ownership, stack/guard invariants, and lifecycle
semantics before opening CO.2.
