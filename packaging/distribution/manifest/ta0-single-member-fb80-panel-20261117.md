# TA.0 — Single-member FB80 evidence panel

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** TA.0 — Release Architecture, Inventory, and Manifest
**State:** Tested host-side MVS/JES orchestration; **no new execution evidence or acceptance claim**.
**Authority:** Tape artifact release milestone, `ta0-inventory.yaml`, and existing `config/dspal.yaml` source mapping.

## Why a separate route is necessary

- Actual MVS JOB **9044**, `TA0READ/TA0HEX`, executed `IEBPTPCH` against `EXT_OBJ(BCPLDEMO)` at **RC=0000**. Its member was displayed as FB80 hexadecimal records with 48+32 printed bytes per logical record. The independently saved report's decoded digest and earlier hand-transcription digest **differ**; neither value proves byte identity against the resident PDS.
- Actual MVS JOB **9045**, `TA0MULT/TA0HEX`, executed one two-member `IEBPTPCH` job selecting `BCPLTIME` and `BCPLQSAM` at **RC=0000**. The operator's subsequent strict multi-member decoder failed with `printed member headers missing, duplicated or reordered`. The report bytes remain private and unavailable to the assistant workspace; this exact formatting/selection failure remains unresolved. **No `TA0MR10` or `TA0BOOT` job ran in the stopped shell stanza.**
- This is a tactical fallback to the previously observed **single-member** output contract. It does not silently relax the strict multi-member parser, infer the contents of JOB 9045, or claim period IEBPTPCH cannot print multiple members.

Period reference: IBM *OS/VS2 MVS Utilities*, Release 3.8, GC26-3902-1, chapter 11, confirms `PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=n` and repeated `MEMBER NAME=` controls; the utility can split source records across printed lines. A later IBM z/OS APAR, OA45799, documents selected-member processing order for its own later release; this **does not** prove the exact MVS 3.8J output in JOB 9045.

## Implementation

`tools/distribution/run-iebptpch-single-panel.py` accepts a canonical `--dataset-key` (`MR10_OBJ`, `BOOT_OBJ`, `EXT_OBJ`) and either repeated `--member` or `--all-selected` for **that source only**. The existing manifest remains the sole release-selection authority. `MR10_LOAD` (`DSORG=PO,RECFM=U`) is never eligible. It:

1. Validates all selected member names, uniqueness, FB80/800 DCB attributes and active site dataset mapping **before any MVS submission**.
2. Creates a new private output directory **outside Git**. Existing output paths are refused. The output is never a tape or target MVS dataset.
3. For each selected member, asks the existing `submit-iebptpch-pilot.py` to submit **one read-only `DISP=SHR` JES job** with `MAXNAME=1`, unique job names `TA0E001`/`TA0B001`/`TA0M001` etc. Each job has its own guarded printer cursor, original raw printer bytes, report, JES summary, and pinned private receipt. The authenticated JOB card is generated at runtime; no password is committed or intentionally printed to console.
4. Immediately calls the existing strict `decode-iebptpch-multi.py` in one-member mode. A printed member must exactly match the selected identity; JES and receipt pins, 80-byte record framing and final block boundary are checked. The routine does **not** use or reinterpret JOB 9045's two-member report.
5. Stops on the **first failed or ambiguous** job/decoder, saves private `failure.json` containing only the member, stage, optional job number and exception type, and never retries automatically or submits remaining jobs. A full `panel-receipt.json` with SHA-256 of the per-member receipts appears **only after all members pass**.

The full panel can be used for ten `BOOT_OBJ` members, one `MR10_OBJ` member or the three `EXT_OBJ` members. For the first new MVS execution, **select only `EXT_OBJ(BCPLTIME)` and `EXT_OBJ(BCPLQSAM)`**, each in a separate job, as a bounded comparison against JOB 9045. Keep the earlier JOB 9045 evidence untouched.

The decoded member hashes are hashes of the **IEBPTPCH printed byte representation only**. They are not independent resident DASD binary hashes, not provenance of source Git revisions and not a redistribution-rights disposition. An MVS `RC=0000` alone is never binary acceptance. MVS spool can include sensitive authenticated JOB-card material: retain evidence in a private operator directory and do not check it into Git.

## Test checkpoint

On 17 November 2026, the assistant ran **25/25** isolated mock orchestration tests and **9/9** existing heading-diagnostic tests, plus Python AST syntax checks. The mocks exercise selection and site mapping, safety, private output, SHA-256 receipts, stopping/retaining failure evidence, no automatic retry, and the three allowed FB80 dataset mappings. They do **not** simulate a faithful IBM MVS 3.8J execution or substitute for actual JES/IEBPTPCH evidence. The previously reported 73-test TA.0 baseline was not rerun in this checkpoint.

**TA.0 remains IN PROGRESS.** The two-member JOB 9045 format discrepancy, complete FB80 candidate verification, independent PO/U `MR10_LOAD(ICINT19)` verification, eight build-job receipts, BLIB/COROUTIN build ancestry, redistribution rights, TA.1 tape experiments and release acceptance remain outstanding. No VOLSER reservation or tape operation is authorized or performed by this document.
