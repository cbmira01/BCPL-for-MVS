# Milestone QSAM — Q.0 staging and resource-management decision

**Status:** Approved Q.0 staging and resource-management design. The owner
also approved a **1024-byte total private logical-record stage per
handle** after standalone MVS JOBs 2180–2182. **Not implemented as
BCPLQSAM.** The owner has additionally approved the conservative
returned-CLOSE error and generic R.0 finalizer architecture, including
ordinary FINISH RC=8 on a returned finalizer failure. Exceptional
CLOSE MVS outcomes, full 16-handle region budget and the exact
generic Runtime Extensions assembler ABI remain open. Q.0 — Reconnaissance & contract remains in progress; Q.1 — Linkage & OPEN/CLOSE skeleton has not started.

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
7. **CLOSE and finalization.** On successful explicit CLOSE, invoke QSAM CLOSE first, then dispose of the pending record/staging area, DCB/control allocation and public handle. A returned CLOSE error reports `QS_ERR_CLOSE`, retires the handle
from application I/O and retains **uncertain ownership** of
resources MVS may still reference; do not blindly retry or free. A linked stateful BCPLQSAM package must be finalized on normal `FINISH` and `STOP(n)` even if handles were left open. Use a *generic* termination hook supplied by Milestone Runtime Extensions, before BCPLMAIN's final storage reclamation, not a QSAM-specific permanent edit to BCPLMAIN. It should attempt all live-handle closures, continue cleanup of unrelated handles after a returned failure, release resources when safely possible, and preserve the intended STOP code. The owner approved diagnostic reporting and **FINISH RC=8**
on a returned implicit-finalizer failure, with `STOP(n)` still n.
The diagnostic format, exact assembler finalizer ABI, and
exceptional MVS CLOSE behavior still require R.0/Q.0 tests.
8. **Accounting and allocation errors.** Keep explicit counts of live DCB/control blocks, stages, handles and pending records; use conditional MVS storage requests and report `QS_ERR_RESOURCE` on a returned allocation failure without consuming an input record or losing another handle's state. MVS may still issue unrecovered abends. The initial module is nonreentrant, with all mutable state private to BCPLQSAM.

See also the [Q.0 period-limit, conditional-allocation and generic-finalization review](qsam-q0-record-limits-failures-finalization-review.md).
It distinguishes documented MVS maxima from the approved private
stage ceiling. The owner has now approved the R.0 **finalizer
sequencing model** separately: see
[Q.0 error and R.0 decisions](qsam-q0-error-and-r0-design-decisions-20261020.md).
No generic finalizer has yet been implemented.

## Approved initial record-stage limit (2026-10-20)

The owner approved **1024 total private staging bytes per open BCPLQSAM
handle** for the first implementation, supported by
[JOBs 2180–2182](qsam-q0-1024-byte-stage-evidence-20261020.md).

- F/FB: support only an effective DCB LRECL of **1 through 1024**
  logical data bytes; a record's public data length is the LRECL.
- V/VB: support an effective DCB LRECL of **4 through 1024 bytes**,
  including the **four-byte RDW inside the stage**, giving **0 through
  LRECL-4 application data bytes** per logical record. A zero-length
  data record is not EOF. The QSAM BDW is never part of this stage.
- Reject unsupported effective LRECL/RECFM or inconsistent BLKSIZE
  before the first GET/PUT. Use non-opening preflight where necessary
  to avoid known incompatible-OPEN abends; do not claim every invalid
  DCB can be recovered from OPEN. This does not change the existing
  Q.0 transactional OPEN and error-return policy.
- For supported opened datasets, `INFO.result!7` is the **effective
  dataset-specific supported data-byte maximum**: F/FB = LRECL,
  V/VB = LRECL-4. It is **not** always 1024 or 1020.
- This is a **BCPLQSAM version-1 implementation policy**, not the
  maximum permitted by MVS 3.8 and not an automatic acceptance of any
  job region's storage budget.

**Still not approved or verified:** a guarantee that **16 fully open
maximum-sized handles** fit within `REGION=256K` (JOB 2182 held only
sixteen private stages); the completed public implementation; abnormal
QSAM CLOSE behavior and unrecovered abends; the *exact* R.0/R.1
generic registration/finalizer byte layout and calling convention.
The observable normal FINISH/STOP returned-error policy is approved,
but its diagnostic format and MVS behavior are not yet tested.
The approved handle count remains **16 concurrently open handles as a
functional target**, with region budgeting and Q.1 validation pending.

## Required evidence before accepting the implementation

| Stage | Minimum targeted tests |
| --- | --- |
| Q.0 remaining | **Size-stage design approved** after MVS JOBs 2180–2182; error-path reconnaissance, full region budgeting and generic finalizer/registration contract still need resolution |
| Q.1 — Linkage & OPEN/CLOSE skeleton | Three concurrent DDs and ultimately 16 active handles; allocation counts; invalid/closed/stale IDs and slot reuse; failed OPEN cleanup; normal `FINISH` and `STOP(8)` auto-close through a generic finalizer |
| Q.2 — Fixed logical records | FB/F exact bytes, two independent handles, short-READ / repeated short-READ / successful retry with no extra GET; output flushing at explicit CLOSE and termination; binary 00/FF/trailing-byte fidelity |
| Q.3 — Variable logical records | V/VB sizes, RDW isolation, payload-only `result!1`, smallest/maximum supported payload, repeated undersized retries, no buffer overwrite |
| Q.5 — Hardening & release | Full resource-accounting audit and accepted runtime regression panel; clean-room rebuild; terminal cleanup in success and returned-failure paths |

**Milestone QSAM Q.0 remains open.** This approves the design direction, not implementation readiness or any new march closure. The existing `BOOT_OBJ` members remain untouched unless separately authorized.