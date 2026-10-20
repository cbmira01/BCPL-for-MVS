# Milestone QSAM — Q.0 record limits, resource failures and finalization review

**Status:** Q.0 — Reconnaissance & contract; engineering findings and **proposed R.0 design for owner approval**. No BCPLQSAM or Runtime Extensions implementation has been performed. **Q.1 — Linkage & OPEN/CLOSE skeleton has not started.**

**Source-of-truth references:** `packaging/milestone-qsam.md`; `packaging/bcplqsam-public-interface.md`; `packaging/qsam-q0-staging-resource-design-decision.md`; `packaging/milestone-runtime-extensions.md`; `packaging/runtime-and-library-nomenclature.md`; `packaging/global-number-registry.md`; `packaging/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md`. Source repository: `cbmira01/BCPL-for-MVS` on `main` (reviewed at `2afb81a972fe5668c5ef587ffa015ef779a039e6`).

## 1. Period MVS record limits — documented facts, not BCPLQSAM acceptance

The period authority is IBM, *OS/VS2 MVS Data Management Macro Instructions*, Release 3.8, GC26-3873-0 (amended 30 March 1979), especially **DCB—QSAM** (printed pp. 93, 102) and **Appendix C: Device Capacities** (printed pp. 199–200):
https://bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3873-0_OS_VS2_MVS_Data_Management_Macro_Instructions_Rel_3.8_Mar79.pdf

| Property | Documented ceiling or rule | Important restriction |
|---|---|---|
| QSAM BLKSIZE | Maximum operand value 32,760 bytes | Ordinary sequential DASD (without track overflow or spanned records) also limited by *device-specific single-track capacity*. |
| F/FB LRECL | Logical record data bytes; `LRECL <= BLKSIZE` | Unblocked F requires BLKSIZE = LRECL; blocked FB requires BLKSIZE multiple of LRECL. For direct-access media, logical record cannot exceed applicable device capacity. |
| V/VB LRECL | Maximum 32,756 bytes including 4-byte RDW | At this general limit, theoretical data maximum is 32,752 bytes; actual supported values are constrained by device/block geometry. |
| V/VB BLKSIZE | Includes four-byte physical BDW in addition to logical-record RDW | A single unspanned record must fit with both internal overheads; no BDW/RDW bytes enter public BCPL data. |
| Example device limits in Appendix C | 3330/3333 model 1: 13,030; 3350: 19,069 bytes per track | **Examples only.** The actual TK5 work-volume device type was not established in this review. Do not infer 3350 just from `SYSDA`. |
| VBS/VS, undefined record and track-overflow exceptions | Have separate rules | Excluded from initial BCPLQSAM public support; do not import these exceptions as permissions for F/FB/V/VB. |

**Consequence:** The approved per-handle stage must cover the *effective* LRECL, including RDW for V/VB, but never exceed a separately tested BCPLQSAM storage ceiling. `INFO.result!7` must report the maximum **payload** bytes supported by both that specific dataset and the extension, not merely a theoretical MVS-wide constant. Keep F/FB = effective LRECL, V/VB <= effective LRECL - 4. Do not announce support for 32,752-byte V/VB payloads until the actual target buffers and device geometry are tested.

**Existing MVS evidence:** JOB 2160 passed FB80/BLKSIZE800 with 23 records; JOB 2161 passed V LRECL100/BLKSIZE104; JOB 2162 passed VB LRECL100/BLKSIZE404 with 15 records. All steps RC=0000; these are *not* tests at upper size bounds. See `packaging/qsam-q0-dasd-evidence-20261020.md`.

## 2. Conditional allocation and cleanup — existing tested code precedent

`bootstrap-toolchain/asm/bcplio.asm` already uses `GETMAIN RC,LV=32`, `GETMAIN RC,LV=268` and `GETMAIN RC,LV=16`, checking R15 after each request; it uses `FREEMAIN R` on returned-control rollback and final release. The accepted BCPLIO dynamic-stream contract documents fault-injection/resource cleanup tests but explicitly does **not** claim recovery from every real MVS storage or I/O abend.

**Approved BCPLQSAM ownership policy, reiterated (not a new choice):**

1. Reserve an unpublished handle-table slot. Allocate and initialize its DCB/control state; validate DD; OPEN the DCB and check effective characteristics. Acquire the stage via conditional `GETMAIN RC` **before any GET or PUT**. Do not publish an opaque handle until all acquisitions succeed.
2. A failed returned-control acquisition reports `QS_ERR_RESOURCE=-11`, unwinds acquired objects in reverse order, and leaves previously open handles unchanged. If OPEN already succeeded, attempt safe CLOSE *before* releasing its live DCB. When CLOSE itself fails, keep a diagnosable state; do not claim all allocations were freed without evidence.
3. The stage is private to that handle; a pending READ remains staged across repeated capacity errors. On valid READ buffers, the caller's bytes are unchanged unless the full record fits. A GET may never be repeated while that record is pending. Disjoint handles must not share work areas.
4. A live handle identifier is a positive, monotonically issued non-recycled BCPL integer for the program lifetime. Slot reuse never revalidates a stale handle. Reject identifier exhaustion rather than wrapping.
5. All actual MVS allocations have recorded address and length. Release exactly once. Track live DCB/control regions, stages, handle records, and pending records independently, for diagnostics and tests.

**Updated with subsequent Q.0 evidence (2026-10-20):** JOB 2177
observed a genuine conditional 1 MiB GETMAIN refusal (R15=4) at GO
REGION=256K and successful rollback. JOB 2182 acquired and freed
sixteen independent 1024-byte areas. Jobs 2180/2181 verified V/VB
LRECL=1024 on TK5 3390 DASD; the owner then approved **1024 bytes
total private staging per BCPLQSAM handle**. See
[the execution record](qsam-q0-1024-byte-stage-evidence-20261020.md)
and [approved staging design](qsam-q0-staging-resource-design-decision.md).
These are not tests of the production module or sixteen opened DCBs.
Still unproven: a complete 16-handle region budget, safe recovery after
exceptional CLOSE, and behavior across all devices/record formats.

## 3. Proposed Runtime Extensions finalization contract (owner decision needed)

Current `BCPLMAIN` calls `IOFIN` from its shared `FINEXIT` on both `FINISH` and `STOP(n)`, then releases memory through `MEMDRAIN`. `BCPLIO.IOFIN` calls `IODRAIN`, which drains and closes the core character streams. The accepted staging design requires BCPLQSAM to close outstanding record-oriented handles too, **without hard-coding a QSAM-specific call into BCPLMAIN**.

**Recommended minimum generic model (not yet adopted as the R.0 ABI):**

- Each explicitly selected optional module's linker-resolved registration descriptor contains its dispatcher export and an **optional finalization entry pointer** (zero/absent for stateless modules); no additional public `G!N` is allocated for cleanup.
- At startup, the common Runtime Extensions registrar validates the table and saves an ordered list of finalizers for that executable. Unlinked packages have no entries and no work. Duplicate/invalid descriptors must be rejected before START.
- At the normal `FINEXIT` common path, invoke all registered finalizers **once**, in **reverse registration order**, **before** the existing `IOFIN` and **before** `MEMDRAIN`, while MVS services and package private state are still valid. This is a proposed ordering; verify that it preserves existing BCPLIO output and register invariants.
- A finalizer uses an assembler-compatible entry convention and reports a status to its caller. **Exact register/descriptor/diagnostic layout remains to be specified and tested in R.0**; do not present any illustrative register assignment as an accepted ABI.
- A BCPLQSAM finalizer tries to CLOSE each still-open DCB, proceeding to other independent handles after a returned-control error, and frees resources only when safe. Multiple finalizer invocations must be harmless at the internal state level, although the registrar calls it once.
- `STOP(n)` retains its requested completion code, including `STOP(8)`. For `FINISH`, if an implicit CLOSE fails, **do not silently claim success**; choose a concrete return-code and diagnostic policy after targeted evidence and owner approval. No normal-finalizer guarantee is made on unrecovered MVS abends.
- Test `FINISH` and `STOP(8)` with several unclosed input and output files, including an unterminated output buffer and a staged pending input record. Confirm resulting record completeness, handle retirement, the same STOP code, no leaks, and no regressions in core BCPLIO.

**Decision point for owner:** Accept this *generic descriptor-carried optional finalizer* model and reverse-order-before-IOFIN timing for R.0 design, or choose an alternative after targeted ABI review. The existence of a module in IEWL does not on its own imply G!200 installation or a finalizer entry.

## 4. Recommended Q.0 evidence plan (safe, staged)

| Priority | Isolated test, no persistent PDS writes | Required observable evidence |
|---|---|---|
| 1 | Inspect actual TK5 `SYSDA` work-volume device type; test F80 (`BLKSIZE=80`), VB/V at lengths already known to pass; then vary legal small/medium LRECL/BLKSIZE pairs within **documented actual track capacity** | Actual DCB attributes after OPEN, writer/reader RC, record count/data, EODAD and JES allocation/abend messages. Avoid assuming a 32K DASD block works on smaller devices. |
| 2 | V and VB minimal RDW and zero payload, plus nonzero payload and one near-tentative-ceiling pair | Confirm whether a four-byte RDW with zero user data is genuinely supported, the effective DCB attributes, RDW content and return behavior. Do not call zero data EOF. |
| 3 | Test-only conditional `GETMAIN RC` fault-injection after one/two successful acquisitions, then optionally constrained-region genuine exhaustion in a **disposable job** | Count matching GETMAIN/FREEMAIN, no published handle on failure, unaffected existing handle, no leaked private stage. Synthetic denial is a cleanup test, not proof of actual MVS resource exhaustion. |
| 4 | Missing DD via non-opening inquiry; invalid DD name; valid DD with deliberately incompatible DCB/OPEN in a separate bounded exploratory job | Distinguish returned error status, a logged MVS abend, and skipped execution. Never claim every OPEN failure is recoverable. |
| 5 | Test-only generic registrar/finalizer with no package, a trivial stateful package, and two independent packages, then integrate candidate BCPLQSAM in Q.1 | Finalizers invoked once in reverse order; no-entry path is a no-op; register/save-area invariants preserved; STOP(8) unchanged; `IOFIN`/`MEMDRAIN` still function. |
| 6 | Negative READ tests, including EOF twice, short buffer twice, successful retry, multi-handle interleave | No second GET for pending handle; caller buffer unchanged until full capacity; independent handles; no GET after EODAD. |

Keep job sources, generated decks and reproducible instructions isolated under `bootstrap-toolchain/probes/`, use temporary `&&` datasets, and publish observed JES job IDs and actual return codes before upgrading a test from *prepared* to *PASS*. Do not manufacture success from static checks.

## 5. Q.0 gate recommendation

The period documentation supplies the *general* MVS numeric rules.
**After this review was written**, Q.0 JOBs 2180–2182 and owner
approval separately established the initial **1024-byte private-stage
implementation ceiling**, not an MVS maximum. JOB 2177 established one
real recoverable GETMAIN-refusal path, not generic resource or abend
recovery. Exceptional CLOSE recovery and R.0 finalizer pointer, order
and entry ABI remain **unaccepted proposals**, not a working facility.

**Keep Q.0 open**. Request owner choice on R.0 finalizer design and perform the targeted MVS probes before closing this march. Do not begin Q.1, modify accepted `BOOT_OBJ`/`BOOT_DEVOBJ`, or mark BCPLQSAM functional from the standalone assembler JOB 2157/2159–2162 evidence.