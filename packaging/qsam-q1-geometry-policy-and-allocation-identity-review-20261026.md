# Milestone QSAM — Q.1 approved geometry policy and allocation-identity feasibility review

**Date:** 26 October 2026  
**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**Owner decision:** **APPROVED: fail-closed hybrid production geometry policy.**  
**Status:** design and documentary feasibility only; no new MVS experiment, production assembler change, or Q.1 acceptance.

## Decision and scope

The owner approved the **fail-closed hybrid** after the scoped three-DD
[JOB 6620 result](qsam-q1-job-6620-explicit-go-dcb-evidence-20261026.md).
`QSAMSVC:200` and the public OPEN-by-allocated-DDNAME contract remain unchanged.
Successful `RDJFCB` with incomplete geometry is **not** permission to OPEN.

1. **Complete, trustworthy pre-OPEN JFCB geometry:** apply existing format,
   size, and blocking validation before MVS OPEN; verify effective DCB
   attributes again after successful OPEN and before GET/PUT.
2. **Missing JFCB geometry on an existing supported DASD allocation:**
   investigate a supported non-opening inquiry into the **actual allocated**
   dataset and volume, then validate reliably recovered attributes.
   No recovered-geometry implementation is yet approved as correct.
3. **Partial, conflicting, unidentifiable, or unsupported allocation:**
   reject before unsafe OPEN using the existing `QS_ERR_OPEN=-6` where the
   failure is an invalid/unknown geometry; preserve `QS_ERR_NO_DD=-5`
   only for a positively established missing allocation.
   Do not silently substitute catalog, default, or guessed attributes.

An output allocation without verified pre-OPEN geometry also fails
closed until a separately supported mechanism is established.
The hybrid **does not** impose a universal mandatory JCL `DCB=` rule.
An explicit GO reader DCB remains the **only demonstrated passing Q.1
three-DD configuration**. This policy does not promise universal
recovery from MVS abends; the [Q.0 JOB 2171 S013-20](qsam-q0-open-incompatible-evidence-20261020.md)
and [approved Q.0 error policy](qsam-q0-error-and-r0-design-decisions-20261020.md)
remain binding.

## Source-level feasibility findings — not MVS verification

The source-controlled Q.1 `bcplqsam.asm` currently performs
`RDJFCB ((2))`, reads `JFCB+100` (RECFM), `+102` (BLKSIZE),
`+104` (LRECL), and passes those to `QCVFORM` **before** the
`OPEN` macro. JOB 6619 recorded all three geometry values as zero
on omitted-DCB GO readers; JOB 6620 saw the expected F1024 values
when the same GO DDs supplied explicit attributes.

**IBM period documentation:**

- [OS/VS2 System Programming Library: Data Management, GC28-3830-4](https://manuals.plus/m/2ed78ffec54432885e4118cfa9235b0e93839871416ad4616b9c1f51825a9b6d),
  Release 3.8 (Oct 1981), pp. 33–36, documents `OBTAIN` with
  `CAMLST SEARCH` to obtain a format-1 DSCB using a **44-byte name,
  six-byte volume serial and 140-byte work area**, without QSAM OPEN.
  The output begins with the **96-byte DSCB data portion**.
  `OBTAIN` is not available for SYSIN/SYSOUT.
- [OS/VS2 System Data Areas, ST68-0606-0](https://bitsavers.org/pdf/ibm/370/OS_VS2/Release_1_1972/ST68-0606-0_OS-VS2_System_Data_Areas_VS2_Release_1_First_Edition_197209.pdf),
  Release 1 (1972), maps `JFCBDSNM` to offset 0 (44 bytes),
  `JFCBNVOL` to +117 (one byte), and `JFCBVOLS` to +118
  (five six-byte entries). These earlier-release offsets are
  **candidates requiring verification against MVS 3.8J's
  installed IFOX macro/control-block mapping and actual bytes**.
- The same earlier DSCB map lists `DS1DSORG` at full DSCB +82,
  `DS1RECFM` +84, `DS1BLKL` +86 and `DS1LRECL` +88. If
  `OBTAIN` returns only the 96-byte *data portion* of a 140-byte
  DSCB, candidate work-area offsets would be +38/+40/+42/+44,
  **not** +82/+84/+86/+88. Do not use these guesses in production
  until verified against target macros and a controlled probe.

`LOCATE`/catalog lookup may report a *cataloged* dataset location,
but this alone is **not** proof that it is the dataset/volume
allocated to the DD currently being opened. Do not use it as an
unverified shortcut. A JFCB-supplied volser is likewise not yet
proven to be populated or authoritative for `&&` temporary passed
datasets in the Q.1 GO step.

## Next test-only evidence gate (separate JES authorization)

**First probe: allocation identity, without calling `OBTAIN` or
opening any of the three candidate input DCBs.** Prepare a
source-controlled, strictly opt-in temporary diagnostic:

1. Preserve the Q.1 `WGO` temporary F1024 writer and omitted-DCB
   `GO` reader DDs `Q00/Q01/Q02`; keep `GO REGION=256K`.
2. Issue non-opening `RDJFCB` separately for the allocated DDs;
   capture R15 and **raw hex** for `JFCBDSNM` (44 bytes),
   `JFCBNVOL` (one byte) and `JFCBVOLS` (30 bytes), alongside
   existing RECFM/LRECL/BLKSIZE values. Do not print JCL job-card
   credentials or dump unrelated storage.
3. Verify whether the extracted name/volser pair really identifies
   the allocated existing temporary DASD dataset. Check unresolved
   or multi-volume indicators rather than taking the first
   six bytes unconditionally. If this link is not established,
   **stop** and investigate a supported allocation-to-volume
   mechanism; do not execute `OBTAIN` with a guessed volser.
4. Only after positive identity evidence and separate owner review,
   prepare a read-only `OBTAIN/CAMLST SEARCH` test; validate R15,
   DSCB format and record attributes, reconcile with JFCB overrides,
   and reject every uncertain or incompatible combination.

Boundary cases for later evidence: explicit DCB vs omitted DCB;
missing DD; mismatched FB blocking (must **never** reach unsafe
QSAM OPEN); temporary passed DASD; pre-existing cataloged and
uncataloged DASD; missing/multiple volumes; output allocation;
concatenation; SYSIN/SYSOUT; returned inquiry errors. Neither
the first probe nor the proposed `OBTAIN` experiment establishes
full device support or a universal OPEN-abend safeguard.

**No JES run, installed dataset change, public API change,
`bcplqsam.asm` modification, extra region, or Q.1 closure is
authorized by this decision record.** Preparation must be reviewed
and any MVS submission separately approved. Q.1 remains **OPEN
and NOT ACCEPTED**; Q.2 must not begin.
