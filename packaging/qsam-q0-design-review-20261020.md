# Milestone QSAM — Q.0 outstanding contract and implementation design review

**Status:** The private staging, handle lifetime, allocation and normal
termination resource-management policies in this review were subsequently
approved for design planning in the
[Q.0 staging/resource decision](qsam-q0-staging-resource-design-decision.md).
Other proposals remain subject to the indicated tests and owner approval.
No production implementation is authorized by this note.
Governing march: **Q.0 — Reconnaissance & contract**.
**Q.1 — Linkage & OPEN/CLOSE skeleton has not started.**

## Established evidence and existing API decisions

- G!200/`QSAMSVC` and the QUERY/OPEN/READ/WRITE/CLOSE/INFO opcode
  numbers are already assigned by the
  [Global Number Registry](global-number-registry.md) and the
  [BCPLQSAM Public Interface Specification](bcplqsam-public-interface.md).
  This review does not change them.
- JOB 2157 passed the separate assembler-dispatcher calling convention
  and test-only capability-query path. JOBs 2159–2162 passed standalone
  MVS fixed, FB DASD, V DASD and VB DASD logical-record probes:
  [FB/V/VB evidence](qsam-q0-dasd-evidence-20261020.md).
- The public contract already requires positive opaque handles,
  four-word request and eight-word result vectors, caller-owned data
  buffers in bytes, byte-exact records, a distinct EOF status and
  retry of an undersized READ without discarding the record.
  QUERY uses its separate six-word descriptor.
- F/FB records expose exactly their logical data bytes; V/VB QSAM
  buffers include a four-byte RDW whose length includes those four
  bytes. The public BCPL buffer and its reported length exclude the
  RDW. The BDW is never part of the public logical record.

## Implementation policies: approved directions and outstanding verification

The linked [decision record](qsam-q0-staging-resource-design-decision.md)
takes precedence over this earlier recommendation table wherever it
approves staging, handle allocation/retirement and normal finalization.
Numeric ceilings, exceptional CLOSE policy, and the precise R.0
registrar/finalizer representation remain unresolved.

| Subject | Proposal | Required evidence or owner decision |
| --- | --- | --- |
| Input staging and retries | Allocate a private per-input-handle record area after successful OPEN attribute validation and **before first GET**. Each GET lands in this area. Validate complete length, retain as a pending record until copied, and issue **no second GET** after BUFFER_TOO_SMALL. | Decide eager per-handle allocation versus bounded demand allocation. Probe buffer unchanged on repeated short READ, independent handles, and CLOSE with pending data. |
| Variable RDW | Keep the four-byte RDW private. On GET, validate length >=4, length <= effective limits, and zero reserved bytes where required; return length minus four. On PUT, build the RDW in private storage. | Probe empty variable payload (total RDW length 4) and near-boundary lengths before promising either; test binary payload fidelity. |
| Supported sizes | Derive actual LRECL, BLKSIZE and RECFM from the successfully opened DCB; bound accepted data length by both dataset geometry and an explicitly documented extension storage ceiling. Reject unsupported configurations at OPEN rather than accepting and later overrunning private buffers. No guessed universal MVS maximum. | Determine MVS 3.8/DCB and memory limits with period documentation plus direct boundary jobs. Approve an implementation ceiling and whether per-handle allocation is practical. |
| Missing DD and OPEN errors | Normalize and validate DD name before allocation. Use a separate, non-opening DD-allocation inquiry only if the existing `BCPLIO`/`DDVERIFY` precedent works for the relevant DD types. Return QS_ERR_NO_DD **only** for reliably proven absence; otherwise distinguish a recoverable QS_ERR_OPEN. | Run present/missing DD, conflicting mode, invalid DCB/RECFM and partially allocated-resource tests. Determine MVS OPEN failure/abend behavior. |
| EOF and failure handling | Translate EODAD into a persistent per-handle EOF state. Repeated READ at EOF returns QS_EOF without a new GET. Treat SYNAD/physical failures as recoverable only where MVS demonstrably returns to the module. | Test empty dataset, EOF twice, I/O errors and partial CLOSE failure. No blanket abend-recovery promise. |
| Handles and cleanup | Allocate at least 16 simultaneous handles, track mode, DCB, private area, pending length/flag, EOF and lifecycle. Use a generation or other stale-handle discriminator so closing/reusing a table slot cannot validate an old handle. | Choose precise generation encoding, exhaustion behavior and cleanup disposition after failed CLOSE. |
| INFO and QUERY | INFO returns effective DCB RECFM mapped to public enum, actual LRECL/BLKSIZE and maximum **data** bytes the extension can handle; return only implemented bits in QUERY. | Add native INFO/QUERY callers exercising version/size/capacity and unsupported format cases. |
| Optional registration | Reuse **Milestone Runtime Extensions**, not a QSAM-only loader or permanent generated-trailer workaround. Keep only the selected dispatcher in G!200. | R.0 must choose and verify `BCPLREG` representation, duplicate-slot validation, missing-package behavior and startup order before normal Q.1 integration. |

**Specific staging invariant:** On a valid READ buffer, no bytes are
written until complete record length is known and capacity suffices.
If a GET has advanced QSAM but the application buffer is inadequate,
the pending full record remains associated with that handle. A
repeated undersized call returns the same required data length
without another GET. A sufficiently large call copies exactly the
record data and clears the pending state. CLOSE discards it.

For F/FB, a requested WRITE length must equal effective LRECL.
For V/VB, the implementation must account separately for the RDW
(4 bytes) and for BDW/block geometry. Those are already public
interface obligations, not proposed API changes.

## Outstanding experimental questions and Q.0 exit requirements

1. **Attribute boundaries:** Test a genuinely unblocked F dataset,
   V/VB smallest valid payload, near supported LRECL/BLKSIZE sizes,
   binary data including `00` and `FF`, and larger blocked datasets.
2. **Error paths:** Establish DD-name rejection, absent allocation,
   incompatible mode/record format, empty dataset, EOF repeated,
   observed abnormal termination versus recoverable OPEN/CLOSE
   and SYNAD handling. Document when no negative status is possible.
3. **Buffered retry:** Execute a test-only staging proof, including
   an undersized caller buffer, repeated undersized retry, successful
   retry, interleaved independent input streams and resource exhaustion.
4. **Production ABI:** Validate register/save-area discipline across
   actual MVS service calls, not merely the Q0DISP test surrogate.
5. **Optional registration:** Settle and execute the shared R.0
   registration mechanism, including missing and duplicate extensions.
   Do not silently promote an ad hoc G!200 binding to a generic facility.
6. **Q.0 gate:** Owner reviews documented implementations choices,
   evidence and remaining risks against
   [Milestone QSAM](milestone-qsam.md), then explicitly accepts or
   defers Q.0. Evidence from standalone assembler jobs alone
   is insufficient to close the march.

No BCPLQSAM executable has yet been assembled, linked or exercised,
and no accepted `BOOT_OBJ` object is altered. This review is
deliberately **not** Q.1 implementation.
