# BCPLIO on MVS — JCL, QSAM and character-stream contract

Status: **M4.2 characterization retained; current M5.4 dynamic runtime contract published 2026-10-17. M4.3/M4.4 and M5.0–M5.3 later closed within their documented scopes.**
Parent: [Milestone - BCPLIO dynamic stream](Milestone-BCPLIO-dynamic-stream.md)
Evidence: [M4.2 characterization and acceptance](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md)

## Responsibilities

| Party | Contract |
|---|---|
| BCPL application | Supplies a DD name to FINDINPUT or FINDOUTPUT; uses SELECTINPUT/SELECTOUTPUT, RDCH/WRCH, ENDREAD/ENDWRITE, and the ordinary BCPL stream behavior. It does not configure DCBs or invoke QSAM. |
| Programmer and job JCL | Arrange the named DD allocation, appropriate dataset/device, disposition, and compatible data characteristics (including relevant RECFM, LRECL, and BLKSIZE when needed). Dataset labels and system defaults can contribute attributes; JCL is not necessarily the sole source. The application programmer is responsible for supplying usable input and output datasets. |
| MVS/JES/QSAM | Resolve and allocate DDs, reconcile applicable attributes, validate and perform record-oriented operations, and issue diagnostics or system completion codes for errors. OPEN can return control with an unopened DCB or can terminate the task. |
| BCPLIO | Own per-stream descriptors, DCBs, buffers and handles; request RDJFCB/OPEN/GET/PUT/CLOSE as needed; convert supported QSAM records to/from BCPL character streams; and release resources on paths where control returns to BCPLIO. It is not a general dataset validator or an MVS recovery subsystem. |

## Current supported stream shape (not a general QSAM interface)

- **Input:** The implemented logical input contract assumes 80-byte fixed text records, trims trailing EBCDIC blanks from each record, and synthesizes BCPL newline character 10. RDCH reports -1 at EOF; UNRDCH is per-stream. Significant trailing blanks cannot be represented faithfully by this translation.
- **Output:** The implemented logical output contract uses 132-byte, blank-padded fixed records. WRCH(10) emits a record; buffering is independent per stream. An overlong logical output record uses the documented STOP(12) policy. ENDWRITE and normal termination handle outstanding data under the existing stream lifecycle contract.
- **Dataset compatibility:** Provide sequential, text-oriented DD allocations compatible with these implementations and the actual QSAM DCBs. The private input DCB template uses `DSORG=PS,MACRF=GM,EODAD=INDYEOD`, and the output template uses `DSORG=PS,MACRF=PM`. The copied templates do **not** themselves specify RECFM, LRECL or BLKSIZE; MVS resolves applicable attributes at OPEN. A JCL DD with a plausible description is not proof that the effective in-core DCB or subsequent GET/PUT will have the assumed shape.
- **Not promised:** Arbitrary RECFM/VB, binary streams, PDS without a selected member, arbitrary device organizations, VSAM, direct QSAM exposure to BCPL, or transparent correction of a programmer's bad DD allocation. These need a different documented contract or optional library.

These are the current **stream translation expectations** and observed test fixture shapes, not evidence that BCPLIO actively rejects every incompatible dataset at FIND time.

## FIND failure and system error boundary

1. Empty, invalid, overlength or unallocated DD names return zero without changing currently selected streams (focused compiled-BCPL regression 134).
2. If descriptor/buffer/handle allocation fails and control returns, FIND returns zero; the code has cleanup branches and targeted synthetic recovery evidence (135–137). Actual low-storage behavior and exact free counts are separate.
3. If `DQOPEN` detects an unsuccessful OPEN *after control returns to BCPLIO*, FIND takes its zero-return cleanup branch, without CLOSE on a DCB not marked open. Test 138 **simulates DQOPEN returning failure before SVC19** and proves BCPL-visible preservation/retry behavior. It does not prove how a genuinely unsuccessful SVC19 is reported.
4. If MVS issues an S013 or other unrecovered system abend, BCPLIO cannot necessarily intercept it and **does not promise continued execution**. Nor does BCPLIO guarantee recovery from arbitrary QSAM GET, PUT or CLOSE errors. Do not convert an abend into a regression PASS.

The source's post-SVC19 DCB-open-state interpretation remains a host detail requiring independent observation before broader claims. Failure to open a real dataset that MVS rejects does not by itself constitute a BCPLIO bug; incorrect BCPLIO handling **if it does receive a recoverable failure** would be a bug.

## M5.4 current contract clarification (2026-10-17)

This document remains the **M4.2 explanation** of how
a BCPL stream interacts with JCL and MVS QSAM, including
the crucial distinction between a returned OPEN failure
and an MVS abend. The current implementation's complete
dynamic-name, stable-handle, FB80/FB132, lifecycle and
QSAM/JES2 responsibility contract is
[BCPLIO dynamic streams — current DEVOBJ runtime contract]
(BCPLIO-dynamic-runtime-contract.md).
M4.3 subsequently accepted scoped returned-control
resource accounting; M4.4 accepted 145/0/1 regression
compatibility; M5.1 closed on printer-route and QSAM
dataset-readback evidence, with JES2 internal spool
validation explicitly removed from the BCPLIO gates.

Historical "next gates" below are retained as dated
provenance rather than current work requests.

## Evidence, limits, next gates

- Focused regression **134 PASS**: ordinary bad/absent DD names and preservation of selection/cursor.
- Focused regressions **135, 136, 137 PASS**: temporary, isolated synthetic GETMAIN failure branches; observable subsequent retry.
- Focused regression **138 PASS**: temporary, isolated synthetic DQOPEN failure branch; selected stream/cursor preserved and successful retry.
- Actual-OPEN exploratory jobs **7874, 7875, 7876** all returned a DD02 handle, with GO RC0000. **None** demonstrated an unsuccessful real OPEN; **none** read DD02. They are characterization, not validation of incompatible record I/O.
- **M4.2 CLOSED on the scope-limited recovery contract**; real SVC19 failure manufacture is no longer its exit condition. **M4.3 remains responsible for independent GETMAIN/FREEMAIN and OPEN/CLOSE counts, post-OPEN state/cleanup observability where relevant, and leak/double-close evidence.** M4.4/full-panel compatibility and M5 per-DD output attribution remain separate, with the full panel deferred by owner direction. Nothing here promotes DEVOBJ modules to production OBJ.

For application-level record I/O beyond this historical character-stream contract, design a separate optional BCPLQSAM (or future BCPLVSAM) library rather than silently changing core stream semantics.
