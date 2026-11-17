# TA.0 — IEBPTPCH FB80 object readback, JOB 9044

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** Owner-supplied **actual MVS/JES observation** and tested host-side readback parser; **not** candidate binary provenance or TA.0 closure.

## Live MVS operation — 17 November 2026

The owner ran the approved, read-only JCL pilot against `HERC02.BCPL.EXT.OBJ(BCPLDEMO)` on TK5/MVS 3.8J and posted the `tools/mvs/dump-report-for-job 9044` output in the project conversation.

- JES payload: **JOB 9044, TA0READ**; step **TA0HEX**, `PGM=IEBPTPCH`, **RC=0000**.
- `SYSUT1`: `HERC02.BCPL.EXT.OBJ`, `DISP=SHR`; `SYSUT2` and `SYSPRINT`: JES SYSOUT.
- Control statements: `PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1`; `MEMBER NAME=BCPLDEMO`.
- JES: **14 cards read, 77 SYSOUT print records**. This is a JES report total, **not** an object-member record count.
- IEBPTPCH: `EOF ON SYSIN` and `END OF DATA FOR SDS OR MEMBER`.
- Listed member: **10 FB80 logical records** printed across 20 hex lines, split 48 + 32 bytes per record; **800 bytes** total.
- The observed single `*` delimiters mark logical records, while the trailing `**` marks the physical block boundary. `**` does **not** mean end-of-member in general; additional blocks can follow. For this 10-record observation, `**` followed the final record.
- SHA-256 of the **hexadecimal data manually transcribed from the posted report**: `b74b12ac496437725910ce0a1edfbbd5e55cb33e5905e405b8a6820257f30ee6`.

**Evidence source qualification:** The sanitized fixture `tests/fixtures/ta0-job9044-bcpldemo-transcribed.txt` is an exact attempted transcription of the user-posted hex records with surrounding utility lines, **not original JES printer bytes**. The related test synthesizes a minimal job-log prefix based on the pasted report. This fixture is a parser regression input, not an independently authenticated evidence attachment. Do not distribute the full report from the conversation; it includes a job-card credential field.

The period reference is IBM *OS/VS2 MVS Utilities*, Release 3.8, GC26-3902-1, chapter 11, and the described record/block delimiter distinction also appears in IBM's IEBPTPCH documentation: https://www.ibm.com/docs/en/zos/3.1.0?topic=utilities-iebptpch-print-punch-program .

## Implemented read-only pilot decoder

`tools/distribution/decode-iebptpch-readback.py` consumes a saved **complete** `dump-report-for-job` text file and requires explicit member, payload JOB number and independent expected record count. It verifies the MVS success markers and member identity, then strictly accepts the observed two-line/FB80 output layout with **12** hexadecimal eight-digit groups on the first line and **8** on the second. It preserves all 80 bytes including binary zero and trailing blanks. It accepts `**` at intermediate block boundaries, requires a terminal physical block marker for this FB pilot, detects extra hex/member output, and writes binary plus a receipt to **new private files outside the Git checkout only**.

The expected record count is an operator input. Passing it does not independently establish that the printed member was complete; a retained original report and independent record-count/byte comparison are still required. Unrecognized IEBPTPCH pagination or format changes **fail closed**, rather than silently omitting data.

## Verification

- **20/20 new offline decoder tests PASS**, including JOB 9044 transcription/digest; 20 earlier IEBPTPCH generator tests independently re-run **PASS** in the assistant's isolated workspace.
- The new test suite exercises wrong job/member, nonzero RC, missing IEF142I/utility completion, wrong record shape, truncation, duplicate/extra records, block boundary placement, malformed printed data, and overwrite refusal.
- No real target JES jobs or IFOX/IEWL executions were run by the assistant. No tape or MVS dataset writes occurred during review.

## Outstanding acceptance gates

1. Preserve and SHA-256-pin the original JOB 9044 printer window and entire job report in operator-private evidence storage; compare the parsed output against this transcription.
2. Independently verify PDS DCB and resident object member count/bytes on MVS using existing acquisition evidence, not a printer digest alone.
3. Repeat readback for the other 13 selected `MR10_OBJ`, `BOOT_OBJ` and `EXT_OBJ` binary members, recording exact identities and receipts; do not infer source revision binding.
4. `MR10_LOAD(ICINT19)` is `PO/U/0/6144` and **excluded** from the FB80 decoder; load structure, independently verifiable contents and actual executable use require their own track.
5. Preserve the separate `BLIB` compiler-hosted build lineage, generated `COROUTIN` assembly lineage, candidate source commit and redistribution rights reviews.

**TA.0 remains IN PROGRESS.** TA.1 writes and release publication remain independently gated. All `BCPL.BT0003` and later positions remain proposed, not frozen.
