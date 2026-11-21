# TA.2 — HETMAP Summary footer correction; qualified BC0002 acceptance review pending

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST (18:43), 23:43 UTC  
**Status:** **Live MVS JOB 9339 RC=0000 for all 21 steps; HETMAP report parser defect identified and corrected; independent structural re-review pending.**

## Actual owner-reported evidence

The owner executed the previously committed **read-only** `scripts/ta2-rc2-postwrite-audit` against the original one-shot candidate. It reported **RC=0**:

```text
TA.2 RC2 POSTWRITE: JES JOB 9339, 21/21 steps RC=0000; 21 SL datasets; AWS 1957296 bytes.
Saved/live HETMAP -f agree: {"file_entries":64,"first_file_numbers":[1,2,3,4,5,6,7,8],"last_file_numbers":[57,58,59,60,61,62,63,64],"sequential_from_zero":false,"sequential_from_one":true,"missing_or_repeated_block_counts":1,"first_number_or_count_discrepancies":[{"row":64,"file":64,"blocks":[0,2559]}],"first_block_counts":[3,5,2,2,32,2,2,25,2,2],"last_block_counts":[2,7,2,2,16,2,2,671,2,null],"first_dataset_layout_discrepancies":[],"strict_21_dataset_layout_pass":false}
AWS SHA-256: 123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375
Read-only evidence: workarea/ta2-rc2-postwrite-audit/20261121T234319Z-27684
No media change. Tape file-map acceptance is pending original HETMAP review.
TA.2 postwrite audit RC=0
```

The source-controlled audit replayed the original **SHA256-sealed JES and HETMAP reports** for the one-shot operation, verified the matching current HETMAP `-f`/`-l` output, 21 labels, all 21 original `IEF142I` results, and this existing AWS SHA-256. No new JES, mount or tape operation was performed.

## Root cause: physical file 64 versus HETMAP summary

The original `files_report` implementation scanned from a `File #` header to the *next* `File #` or end of output, then required exactly one `Blocks` field inside the section. Physical file **64** has the proper **zero** block count. After file 64, Hercules `hetmap -f` prints a separate **`Summary`** section with **`Files: 64`** and aggregate **`Blocks: 2559`**. The old parser incorrectly included this footer in file 64, yielding **`[0,2559]`**.

The Hercules `hetmap.c` source confirms that, after listing physical file blocks, its `O_FILES` option prints the independent **`Summary`**, **`Files`** and **`Blocks`** aggregate fields (source inspection: https://fossies.org/linux/hyperion/hetmap.c). Therefore the source defect is in *report segmentation*, not evidence that a second physical `Blocks` field was actually recorded on tape.

The corrected **independent AWS reviewer** now requires exactly one `Summary` boundary **after** 64 physical files and checks the aggregate `Files` and `Blocks` values against the actual parsed counts. It preserves strict 1–64 file numbering, 21 expected header/data/trailer triples, nonempty data files and the terminal zero-block file. Missing, duplicated or inconsistent footer fields **refuse**.

## Consolidated read-only re-review and safeguards

The revised `ta2-rc2-postwrite-audit` replays the exact original one-shot evidence and still performs only read-only HETMAP `-f/-l/-a` displays. It now separately parses the footer, calls the independent canonical `ta2-rc2-aws-review.evaluate` to validate each SL dataset's identities and physical file structure, and reconciles `-a` and `-f` physical totals. The existing image must **match the original owner-reported SHA-256 123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375**, checked before and after inspection. Any mismatch refuses without a tape write.

A successful revised audit will record a **qualified MVS/JES + SL label/file structure PASS** under `workarea/ta2-rc2-postwrite-audit/`. The original 23:43 UTC receipt remains immutable and its previous `strict_21_dataset_layout_pass:false` is not rewritten. **No claim of final structural acceptance is made before the new live result.**

**Offline verification:** Python AST checks; **37/37** tests in the two updated source-controlled reviewer test suites, plus **12/12** additional footer-parser negative and integration checks in the assistant's separate repository-root workarea, all PASS. This does not replace the actual MVS tape evidence.

**Preserve:** `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, its existing mount, original postwrite and production evidence, and permanent no-retry marker. **Do not rerun, reinitialize, remount, rewind, unmount or overwrite** this tape. The next operation is exactly **one read-only structural re-review**. No MVS restore, byte-for-byte member verification, clean-target installation, source-rights clearance or publication is authorized. **TA.2 remains IN PROGRESS.**
