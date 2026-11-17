# TA.0 — JOB 9048 page-continuation readback evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.0 — Release Architecture, Inventory, and Manifest  
**State:** Read-only MVS evidence and tested decoder correction, qualified. TA.0 IN PROGRESS.

## Actual MVS observation, 17 November 2026

The owner supplied `tools/mvs/dump-report-for-job 9048` as a pasted file in the project conversation. It documents an interrupted **EXT_OBJ single-member panel**, not completion of the MR10_OBJ or BOOT_OBJ panels:

- JOB **9048**, JES job name **TA0E003**, step **TA0HEX**, `PGM=IEBPTPCH`, **RC=0000**.
- Read-only source `HERC02.BCPL.EXT.OBJ`, volume `TSO003`, `DISP=SHR`; requested member `BCPLQSAM`.
- IEBPTPCH requested `PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1` and `MEMBER NAME=BCPLQSAM`.
- The printer listing spans **six pages**. Its **same** printed heading `MEMBER NAME  BCPLQSAM` appears at the beginning of each page, with preceding `PAGE 0001` through `PAGE 0006` markers. These are **five page-continuation headings**, not six PDS members.
- Independent offline parsing of the **supplied pasted report**, using 48+32 hexadecimal bytes per logical record, yields **159 FB80 records**, **12,720 bytes**, block boundaries at records **10, 20, …, 150, 159**, and **SHA-256 `503b026138aacc349beae69a4846a0f3db13f9d979e8dbedf992ffa4310cf4e7`**.
- These counts and digest describe the **pasted listing only**. They are not an independently retained/raw-printer-file hash and do not prove resident DASD bytes, the generating IFOX/IEWL build, Git ancestry or release rights.

The earlier single-panel operator output said:

    TA.0 SINGLE-PANEL REFUSED/STOPPED: MultiError
      stage=decode member=BCPLQSAM job=9048

The original fail-closed decoder rejected the repeated member headings. The earlier `EXT_OBJ` panel had already attempted preceding selected members separately. Its saved private evidence is not available in this workspace; their counts and acceptance are therefore not claimed here. The wrapper stopped before invoking the MR10_OBJ or BOOT_OBJ panels.

## Approved narrowly scoped parser correction

`tools/distribution/iebptpch-page-framing.py` collapses *only* repeated print headings that have the **same** active member name, an immediately preceding numbered `PAGE` marker incremented by one from the prior page for that member, and at least one complete 80-byte record printed since the previous heading. The unmodified strict record parser then checks both hexadecimal print lines per record, block delimiters and trailing output. New logical members still must appear exactly once in requested order; a missing, unexpected, reintroduced or reordered member fails closed. No guessed records, page data or member identities are inserted. Page headings are not binary input records.

This directly fixes the JOB 9048 behavior without changing the canonical release inventory, source datasets, IFOX/IEWL build chain, tape media or publication rules.

**Offline proof:** 14 new standalone page-framing tests and 11 further local checks (including parsing the supplied JOB 9048 report and adversarial mutations) passed in the assistant workspace. The full previously established TA.0 regression suite is not claimed rerun against this workspace. The actual *saved private* JOB 9048/9045 printer reports have not been re-decoded here; those require access to their bytes on Morkies.

## Recovery without a duplicate MVS job

`tools/distribution/recover-iebptpch-single-panel.py` is a deliberately
non-submitting recovery path for the stopped `EXT_OBJ` panel. It requires the
existing `failure.json` to identify the **decode** stage and the same
selected member/ordinal/job found in the saved, SHA-256-pinned pilot receipt.
It independently re-decodes every preserved pilot report, byte-compares both
previously decoded members and validates their original report/receipt hashes,
then creates only the missing decoded artifact for `BCPLQSAM` and an overall
panel receipt. It preserves `failure.json` as historical diagnostic evidence.
There are no JES calls, no silent retries and no replacement of prior bytes.
If any original pilot, previous decoded file, member identity, receipt or
expected job is inconsistent, it refuses recovery before producing the missing
artifact. Thirteen isolated mock-based recovery tests passed in the assistant
workspace. Real MVS/private-file recovery is not claimed executed here.

## Follow-up evidence gate

1. Re-decode the already-retained private single-member JOB 9048 pilot without resubmitting it; compare the resulting record count and checksum with the **pasted-output** values above. Preserve any disagreement rather than silently reconciling it.
2. Check the already-retained JOB 9045 two-member pilot with the corrected page-aware decoder. Do not assume print order or member completeness; it remains unaccepted until actual saved-report decoding succeeds.
3. Continue the selected `MR10_OBJ(ICINT19)` and ten `BOOT_OBJ` objects with read-only MVS evidence. Do not repeat successful prior member jobs just to create new receipts.
4. Keep separate the `MR10_LOAD(ICINT19)` `RECFM=U` transfer/executable-use path, eight build-job receipts, generated BLIB/COROUTIN lineage, rights reviews and the TA.1 scratch-tape authorization.

**No TA.0 closure or TA.1 tape authorization is implied.**
