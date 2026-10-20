# Milestone QSAM — Q.0 approved error, finalization, and concurrency policy

**Decision date:** 20 October 2026. **Owner approved** the Q.0
error-handling policy, the shared Runtime Extensions R.0 design
direction, and the isolated 16-DCB test plan. **Q.0 —
Reconnaissance & contract remains open**; Q.1 — Linkage &
OPEN/CLOSE skeleton has not started. The separate Milestone Runtime
Extensions **R.0 — Evidence and contract** has begun as a documented
design/evidence review; R.1 implementation has not started.

## 1. Approved QSAM error policy

**Prevention rather than speculative recovery.** Validate BCPL-owned
inputs and verifiable DD attributes before OPEN or other MVS activity;
recheck effective DCB fields after successful OPEN and before GET/PUT.
Keep the existing [version-1 numeric errors](bcplqsam-public-interface.md),
rather than creating new public return codes.

| Condition | Accepted handling |
| --- | --- |
| DDNAME invalid by BCPL rules | `QS_ERR_DDNAME=-4`; no MVS OPEN |
| Confirmed missing DD via non-opening inquiry | `QS_ERR_NO_DD=-5` |
| Invalid/oversized geometry rejected at preflight, or returned OPEN error | `QS_ERR_OPEN=-6` (distinguish from unsupported effective RECFM) |
| Unsupported effective record format | `QS_ERR_RECFM=-9` |
| Returned GET or PUT error | `QS_ERR_READ=-12`, `QS_ERR_WRITE=-13` |
| Returned CLOSE error | `QS_ERR_CLOSE=-14`; retire handle from further I/O and retain an explicit *uncertain ownership* state |
| Unrecovered MVS OPEN/GET/PUT/CLOSE abend | No ordinary BCPL return guaranteed; do not label this `QS_ERR_*` |

For a returned CLOSE error, **do not blindly retry CLOSE or release
storage that MVS may still reference**. Mark the handle unusable to
application calls; keep ownership, DCB and allocation state for
diagnosis and possible safe finalization. A failed CLOSE does **not**
establish that MVS has definitely retained the DCB or completed it.
Exhaustive exceptional CLOSE outcomes still require MVS tests.

**Evidence boundaries:** JOB 2170 returned `RDJFCB` R15=0 on an
allocated DD and R15=4 for the specifically missing DD; JOB 2172
used non-opening JFCB geometry inspection to distinguish valid FB80/800
from invalid FB80/801; JOB 2171 abended **S013-20 during OPEN** on
FB80/801 and did not return a BCPL status. These observations are
not a universal OPEN safeguard. The owner-approved 1024-byte total
private record stage remains the v1 BCPLQSAM size limit.

## 2. Approved shared Runtime Extensions R.0 design direction

Use **one application-specific, linker-relocated `BCPLREG` object**.
A versioned bounded table contains a signature, format version, byte
length and entry count, followed by explicit references to selected
package descriptors. A descriptor supplies package identity/version,
the global-number/address export(s), and an **optional finalizer
entry address** (zero/absent for stateless packages).

- The empty table is valid, with no optional extension installed.
- Exported globals are checked against the authoritative
  [Global Number Registry](global-number-registry.md). The normal
  policy remains one opcode dispatcher global per package;
  `BCPLQSAM` uses `QSAMSVC:200`.
- Reject malformed, out-of-range or duplicate global exports, absent
  declared requirements and missing selected package references
  **before START**; do not silently overwrite core/BLIB/application
  globals. A BCPL header alone is not a link/registration guarantee.
- A link-edited object alone does not install a BCPL global.
  Packages must be selected in application IEWL/BCPLREG inputs.
- No QSAM-specific registrar or permanent QSAM-only `BCPLMAIN`
  edit. `BCPLREG` and its generic finalizer serve System Extensions,
  Standard Libraries and User/Site Libraries alike.
- Call registered finalizers **once in reverse registration order**,
  on normal `FINISH` and `STOP(n)`, **before** existing
  `BCPLIO.IOFIN` and `BCPLMEM.MEMDRAIN`.
- Attempt remaining independent handle closures after a returned
  failure; release only demonstrably safe ownership. Preserve
  `STOP(n)`'s explicit requested completion code. On ordinary
  `FINISH`, **a returned implicit-finalizer error yields RC=8**
  and a diagnostic; do not silently report success.
- This policy does **not** promise finalizers on unrecovered MVS
  abends, nor safe continuation after one.

**R.0 evidence tasks still open:** exact binary layouts, size/extent
bounds, ABI/save-area and register rules for finalizers, return
diagnostics, compiler-generated trailer and BLIB-import collision
behavior, linker external references, empty table and missing-module
handling. The approved fields are an architectural contract, **not
an assembler byte layout or accepted executable ABI**. No `BCPLREG`
or finalizer code is implemented by this decision.

## 3. Approved Q.0 concurrent-handle experiment

Create **test-only**, independent IFOX/IEWL profiles with
**1, 3, 8 and 16 simultaneously OPEN QSAM DCBs**. The writer and
reader each hold **one private 1024-byte stage per DCB** while OPEN,
exercise two interleaved F1024 logical records per dataset, check
every record and EODAD, CLOSE in reverse order, and release stages.

Run first under **GO REGION=256K**; include a **512K fallback for
16 DCBs** if the smaller region fails. The recorded JES codes,
system messages, and QOUT markers—not the mere existence of
generated JCL—will determine what is supported.

The [test-only generator and standalone job results](qsam-q0-concurrent-dcb-evidence-20261020.md)
have now **PASSED under MVS in JOBs 2183–2186** for
1/3/8/16 simultaneously OPEN F1024 DCBs at GO REGION=256K;
the 512K fallback was not needed. It does not implement BCPL
handles, process public request vectors, invoke R.0 finalizers, or
establish a complete production program memory budget. Account for
actual DCBs, QSAM-owned buffers, stages, BCPL runtime and application
before promising that 16 production handles fit a particular REGION.

## 4. Milestone boundaries and next review

- **Q.0 remains open:** the **standalone 16-DCB test passed in
  JOB 2186**; characterize returned errors and exceptional CLOSE,
  verify the full BCPLQSAM/application storage budget, reconcile
  R.0 and request explicit owner Q.0 gate approval or a documented
  deferral before beginning Q.1.
- **R.0 — Evidence and contract is in progress:** verify actual
  `BCPLMAIN` startup, exports, runtime termination, and minimal
  `BCPLREG`/descriptor ABI. **R.1 not started**.
- Accepted BOOT_OBJ, BOOT_DEVOBJ, compiler, core BCPLIO and historical
  Cambridge compiler sources are unchanged; no milestone or march
  renumbering and no approval of implementation.
