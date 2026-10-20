# Milestone QSAM — Q.0 staging and resource-management decision

**Status:** Approved Q.0 staging and resource-management design decision. **Not implemented or MVS-tested as BCPLQSAM.** Numeric record-size ceilings, exceptional CLOSE outcomes, and the exact generic finalization ABI remain open. Q.0 — Reconnaissance & contract remains in progress; Q.1 — Linkage & OPEN/CLOSE skeleton has not started.

## Authority and boundaries

This decision refines, without changing, `packaging/milestone-qsam.md`, `packaging/bcplqsam-public-interface.md`, `packaging/qsam-q0-design-review-20261020.md`, and `packaging/milestone-runtime-extensions.md`. The Q.0 ABI probe (JOB 2157) and separate QSAM FB/V/VB probes (JOBs 2159–2162) are evidence for the individual mechanisms, not for this implementation.

Existing public API remains unchanged: `QSAMSVC:200`, the v1 opcodes, four-word request and eight-word result vectors, opaque positive handles, `QS_ERR_CAPACITY=-1`, `QS_ERR_RESOURCE=-11`, and `QS_EOF=1`.

## Approved internal architecture

1. **Private QSAM work area per open handle.** Every supported open input or output handle owns a distinct QSAM DCB/control region and one private logical-record staging area. QSAM move-mode GET/PUT uses this area; the extension never retains a caller's BCPL record-data pointer beyond its active call. The stage is allocated using a conditional, checked MVS allocation and records its actual allocation length for reclamation.
2. **Eager stage allocation.** Before publishing a handle, complete the MVS OPEN, inspect effective `RECFM`, `LRECL`, `BLKSIZE` and supported attributes, validate against the extension's *tested* supported ceiling, then allocate the entire stage before the first GET or PUT. For F/FB, capacity covers the logical record (`LRECL`); for V/VB it covers the complete QSAM logical record including the 4-byte RDW (`LRECL`). MVS's physical BDW is never copied into the application buffer. QSAM's own block buffers remain MVS-owned.
3. **Transactional OPEN.** Reserve an internal slot before opening but do not publish a positive public handle until OPEN, effective-DCB validation and all required private allocations succeed. On a returned-control failure, undo completed acquisitions in reverse order and return the documented error. If MVS has opened a DCB, perform a safe CLOSE before releasing it. A partial CLOSE failure is not silently called successful cleanup; preserve enough ownership state for diagnosis/finalization.
4. **READ state machine.** Each input handle independently tracks `READY`, `PENDING`, or `EOF`; pending presence is an explicit Boolean, never inferred from a nonzero record length. A READ in `READY` issues at most one GET into private storage. For V/VB, check the RDW and strip its four bytes from the public copy and `result!1` length. If capacity is insufficient, set `PENDING`, return `QS_ERR_CAPACITY` and required *data* length in `result!1`, and leave the destination buffer untouched. Any number of short retries return the same required length without another GET. The first sufficient retry copies exactly the logical data bytes and clears `PENDING`. EODAD sets persistent `EOF`; repeated READ calls report `QS_EOF` without GET. A legal zero-data-length variable record, if validated in MVS, succeeds with length zero and is not EOF.
5. **WRITE from private staging.** Validate mode and exact application data length *before* copying or calling PUT. F/FB requires data length equal to effective LRECL. V/VB uses private storage for the internally constructed RDW plus data; it reports only user data bytes. For a valid call, copy from BCPL byte buffer into the private staging area, then PUT. A successful PUT is not a guarantee that the physical output has been flushed; CLOSE remains consequential.
6. **16 active handles and stale-handle prevention.** Keep at least 16 simultaneous active entries. Each handle is a distinct positive BCPL signed integer, issued from a monotonically increasing non-recycled sequence for the life of the program; the internal slot may be reused after successful CLOSE, but its former handle value is never valid again. Reject exhaustion rather than wrap the counter or alias an old handle. Each entry tracks open/close state, mode, DCB/storage ownership, allocated lengths, input state, pending length, effective attributes and QSAM errors.
7. **CLOSE and finalization.** On successful explicit CLOSE, invoke QSAM CLOSE first, then dispose of the pending record/staging area, DCB/control allocation and public handle. A returned CLOSE error remains visible as `QS_ERR_CLOSE` and requires conservative ownership accounting; no speculative safe retry is promised. A linked stateful BCPLQSAM package must be finalized on normal `FINISH` and `STOP(n)` even if handles were left open. Use a *generic* termination hook supplied by Milestone Runtime Extensions, before BCPLMAIN's final storage reclamation, not a QSAM-specific permanent edit to BCPLMAIN. It should attempt all live-handle closures, continue cleanup of unrelated handles after a returned failure, release resources when safely possible, and preserve the intended STOP code. Exact diagnostic and termination-RC policy for implicit CLOSE failure requires separate approval and evidence.
8. **Accounting and allocation errors.** Keep explicit counts of live DCB/control blocks, stages, handles and pending records; use conditional MVS storage requests and report `QS_ERR_RESOURCE` on a returned allocation failure without consuming an input record or losing another handle's state. MVS may still issue unrecovered abends. The initial module is nonreentrant, with all mutable state private to BCPLQSAM.

See also the [Q.0 period-limit, conditional-allocation and generic-finalization review](qsam-q0-record-limits-failures-finalization-review.md).
It distinguishes documented MVS maxima from any *tested BCPLQSAM ceiling*
and proposes (without approving) R.0 finalizer sequencing.

## What is not approved as a fixed numeric value

- A universal MVS logical-record maximum, initial BCPLQSAM application-data ceiling, or region-dependent guarantee that 16 *maximum-size* handles can always OPEN. Test period MVS constraints and available GETMAIN capacity; select and document the actual ceiling before Q.2/Q.3 feature acceptance.
- Whether a zero-data-length V/VB record is accepted by the exact MVS/TK5 path, and the failure/recovery behavior of an anomalous RDW or exceptional CLOSE.
- Specific optional-module `BCPLREG` descriptor layout, generic finalizer ordering and how implicit-close errors affect a `FINISH` completion code. These require R.0/R.1 design and MVS testing; do not add a QSAM-only registration/finalization facility.

## Required evidence before accepting the implementation

| Stage | Minimum targeted tests |
| --- | --- |
| Q.0 remaining | MVS record boundaries and resource-ceiling determination; conditional storage failure/cleanup; zero-data-length V/VB; error-path reconnaissance; generic finalizer/registration contract design |
| Q.1 — Linkage & OPEN/CLOSE skeleton | Three concurrent DDs and ultimately 16 active handles; allocation counts; invalid/closed/stale IDs and slot reuse; failed OPEN cleanup; normal `FINISH` and `STOP(8)` auto-close through a generic finalizer |
| Q.2 — Fixed logical records | FB/F exact bytes, two independent handles, short-READ / repeated short-READ / successful retry with no extra GET; output flushing at explicit CLOSE and termination; binary 00/FF/trailing-byte fidelity |
| Q.3 — Variable logical records | V/VB sizes, RDW isolation, payload-only `result!1`, smallest/maximum supported payload, repeated undersized retries, no buffer overwrite |
| Q.5 — Hardening & release | Full resource-accounting audit and accepted runtime regression panel; clean-room rebuild; terminal cleanup in success and returned-failure paths |

**Milestone QSAM Q.0 remains open.** This approves the design direction, not implementation readiness or any new march closure. The existing `BOOT_OBJ` members remain untouched unless separately authorized.