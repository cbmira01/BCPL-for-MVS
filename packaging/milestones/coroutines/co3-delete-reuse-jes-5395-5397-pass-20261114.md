# CO.3 — Native DELETECO and registry/storage reuse PASS, JOBS 5395–5397

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Local date:** 14 November 2026 (15 November UTC evidence timestamp)  
**Tested GitHub `main`:** `1875b26110dae6b19be05cf77a150cb54a1bb392`  
**Evidence class:** OWNER-REPORTED NATIVE-MVS-TESTED; candidate scope only

## Owner-run verification

The owner executed the private candidate runner
`tools/coroutines/run-co3-delete-reuse.py --run` and reported:

    CO.3 first lifecycle PASS: compiler JOBS 5395/5396,
      native JOB 5397; IFOX 4, IEWL 1, GO 1
    CO.3 first lifecycle evidence:
      workarea/co3-delete-reuse/20261115T000019Z-nc9zruc0
    CO.3 deletion/reuse verification RC=0

The runner requires two independent Cambridge BCPL compiler jobs,
four IFOX steps (ASMA, ASML, ASMM, ASMS), one IEWL step (LKED),
and one native GO step: each native step RC=0000, overall JES
`JOB RESULT: SUCCESS` and `HIGHEST RC: 0000`.

It also requires exactly these 21 ordered, complete BCPL records:

    CO3BCPL MADE
    CO3BCPL FULL
    CO3BCPL A1
    CO3BCPL RA
    CO3BCPL B1
    CO3BCPL RB
    CO3BCPL DELA
    CO3BCPL C1
    CO3BCPL RC
    CO3BCPL B2
    CO3BCPL RB2
    CO3BCPL DELB
    CO3BCPL C2
    CO3BCPL RC2
    CO3BCPL DELC
    CO3BCPL D1
    CO3BCPL RD
    CO3BCPL D2
    CO3BCPL RD2
    CO3BCPL DELD
    CO3BCPL PASS

The operator-local workarea contains the raw compilation,
generated assembly, candidate JCL, JES summary/report and receipt.
These raw files were not supplied to or separately inspected
by the assistant. Assertions above derive from the owner's PASS
output and source-verified runner's strict success conditions.

## Verified bounded lifecycle behavior

The test-local, independently compiled BCPL module binds
`CREATECO`, `DELETECO`, `CALLCO`, `COWAIT` and `RESUMECO`.
The candidate IFOX `CO3DROP` checks a registered idle worker,
revokes its membership before BCPL releases the worker's stack
and descriptor through `FREEVEC`, and reopens the vacated
two-worker registry slot. The native fixture covers:

- Refusal of a third live worker at registry capacity and refusal
  to delete the currently executing worker.
- Deletion of an inactive, parent-free worker and list unlinking.
- Preserved operation of another registered worker after deletion.
- Subsequent creation, function completion/re-entry, deletion and
  renewed creation within the same native application.
- Ordered results, root reactivation, and original G54/G55
  stack-boundary restoration.

This demonstrates **registry-slot reuse and allocator-driven
storage reacquisition**, not proof that an identical freed
MVS address was returned. A normal worker function return in
`CO3BOOT` leads to another wait/re-entry; it is not proof of
a general terminal-coroutine reclamation policy.

## Provenance and limits

The first deletion/reuse attempt on revision
`4565e9f6aca065fc3193ec7e044dc06055531a08` failed in
the host export adapter with `BCPL library imports changed`,
before native submission. It remains a separate failure record:
[adapter mismatch](co3-delete-reuse-first-attempt-adapter-failure-20261114.md).
The corrected candidate at `1875b261...` subsequently passed
MVS; no failed job result is reclassified.

The qualified CO.2 `BCPLCO` source and installed `BOOT_OBJ`
were not changed by the candidate. G!289–300 are temporary
candidate assignments, **not approved public registry slots**.
The design is static, supports a maximum of two simultaneous
workers and requires the Approach A known-live descriptor
precondition. Invalid/stale pointers after allocation-address
reuse are **not** supported; no production opaque handles,
general ABA-safe identity, arbitrary-size stacks, multitasking
reentrancy, or full exceptional cleanup are established.

The earlier [first-slice MVS PASS](candidates/co3-first-lifecycle/README.md)
(JOBS 5384–5386) and [parent-chain MVS PASS](co3-parent-chain-jes-5390-5392-pass-20261114.md)
(JOBS 5390–5392) remain independent evidence.

**Disposition:** This is a qualified CO.3 lifecycle acceptance
candidate, not an owner acceptance or closure. CO.3 stays
IN PROGRESS pending explicit owner review; CO.4–CO.5 NOT STARTED.
