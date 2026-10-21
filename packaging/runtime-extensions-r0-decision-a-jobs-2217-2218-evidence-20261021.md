# Milestone Runtime Extensions — R.0 Decision A, JOBs 2217–2218 object-identity evidence

**Date:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**Implementation reviewed:** GitHub `main` commit `3aa4ba46f64697635f984355f4d2100b13fdfc87`.
**Accepted distinction:** strict binary identity **FAIL**; object records **match except the assembler's three-byte `END` run-day field** under the owner-approved narrow comparison rule. This is *record-comparison evidence*, not cryptographic provenance or full proof of the 17 October clean-room source revision.

## Actual MVS comparison

**JOB 2217 (`R0BICAL`) calibration:** ASMA, ASMB, COPYA and SAME returned RC=0000. DIFFER returned **RC=0008**. IEBCOMPR compared three nonempty FB/80 records, and `IEB221I RECORDS ARE NOT EQUAL` identified genuine ESD and TXT record differences in the intentionally changed object. The control comparison (object vs IEBGENER copy) found no differences. Historical MVS IEBCOMPR behavior and the sequential FB/80 copy path are therefore calibrated within this test scope.

**JOB 2218 (`R0BIMEM`) comparison:** ASMMEM (IFOX00) returned RC=0000, zero flagged statements and **18 object records punched**. IEBCOMPR COMPARE returned **RC=0008**, and its SYSPRINT showed **exactly one** `IEB221I` mismatch, in physical block 2, logical record 8, the last of **18** logical FB/80 records. The installed object was opened as `//SYSUT1 DD DSN=HERC02.BCPL.BOOT.OBJ(BCPLMEM),DISP=SHR`; the freshly generated object as temporary `&&MEMOBJ` input. No accepted PDS member was installed, modified or overwritten.

The two *complete 80-byte* offending records both begin `02C5D5C4` (object `END`). All bytes are equal except **one-based byte 52**:

| Source | Field | Recorded value |
| --- | --- | --- |
| Installed `BOOT_OBJ(BCPLMEM)` | END IDR assembler run year/day | `26/292` (19 October 2026) |
| Temporary rebuild | END IDR assembler run year/day | `26/294` (21 October 2026) |
| Unequal byte 52 | EBCDIC digit | `F2` vs `F4` |

## Narrow normalization rule — separately owner-approved

The System/360 relocatable object `END` record encodes the assembler run day as **one-based columns 50–52** of its 80-byte logical record (EBCDIC three-digit Julian day). Only this field may be disregarded when classifying *object content equivalence*. This **does not change** the full-record IEBCOMPR result: strict byte-for-byte equality remains **false**, and COMPARE still has RC=0008.

The [report-only verifier](../bootstrap-toolchain/probes/r0-object-identity-probe/audit-end-date.py) accepts a date-only explanation only when the original job passes the existing member step/punch checks; the single reported comparison is sequential (`TYPORG=PS`), finishes with the full nonzero punched-record count, and reports exactly **one** `IEB221I` mismatch. It must be the final logical record, with two complete 80-byte hex dumps, both object `END` records with an assembler identifier and valid EBCDIC Julian days, *identical byte-for-byte except for positions 50–52*. Different years, compiler/assembler versions, ESD/TXT/RLD data, END control bytes, other IDR text, additional disagreements, truncated reports, wrong counts and utility errors must fail.

The new tests exercise these acceptance and rejection conditions. Applied to the operator-supplied full JOB 2218 report, the verifier returns **`CONTENT_EQUAL_EXCEPT_END_RUN_DAY`**, 18 records compared, unequal column **52**, installed day **292**, rebuilt day **294**, with `strict_binary_identity: false` and `normalized_content_identity: true`.

**Limitations:** The verifier interprets *IEBCOMPR's printed discrepancy evidence*, not a complete independent raw binary export of both datasets. It relies on the historical IEBCOMPR result that all other compared records are equal. It does not prove the exact Git source revision of the installed member, an unchanged incumbent since 17 October, or a production registrar. No masking is applied to any byte of any other record, and no object data is rewritten.

## Reproduce evidence interpretation — no new MVS job

After pulling the new `main`, reuse the existing ignored JES report:

```sh
python3 -B bootstrap-toolchain/probes/r0-object-identity-probe/audit-end-date.py \
  workarea/runtime-extensions-r0-object-identity/job-2218.txt
```

No further MVS run is needed to classify JOB 2218 under the accepted date-field rule. The R.0 gate still needs unrelated global-ownership, actual-owner collision and remaining diagnostic decisions. **R.0 remains open; R.1 has not started.**
