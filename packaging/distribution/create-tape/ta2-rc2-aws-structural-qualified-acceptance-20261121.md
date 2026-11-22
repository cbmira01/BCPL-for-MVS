# TA.2 — BC0002 private AWS structural acceptance (qualified)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Execution date:** 21 November 2026 EST / 22 November 2026 UTC  
**Disposition:** **Private AWS creation, 21-step MVS write, and independent label/file structural review PASS (qualified). TA.2 remains IN PROGRESS.**

## Owner-reported actual MVS and HETMAP verification

The owner executed the Git-controlled read-only `packaging/distribution/create-tape/scripts/ta2-rc2-postwrite-audit` after the corrected HETMAP Summary parser was committed at `ef86e0fb8b695a0344729539f5ba6e34021125f5`. The result was **RC=0**, using the **same original private AWS**, not a new write:

```text
TA.2 RC2 POSTWRITE: JES JOB 9339, 21/21 steps RC=0000; 21 SL datasets; AWS 1957296 bytes.
Saved/live HETMAP -f agree: {"file_entries":64,"first_file_numbers":[1,2,3,4,5,6,7,8],"last_file_numbers":[57,58,59,60,61,62,63,64],"sequential_from_zero":false,"sequential_from_one":true,"missing_or_repeated_block_counts":0,"first_number_or_count_discrepancies":[],"first_block_counts":[3,5,2,2,32,2,2,25,2,2],"last_block_counts":[2,7,2,2,16,2,2,671,2,0],"footer_files":64,"footer_blocks":2559,"footer_reconciles":true,"first_dataset_layout_discrepancies":[],"strict_21_dataset_layout_pass":true}
AWS SHA-256: 123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375
Read-only evidence: workarea/ta2-rc2-postwrite-audit/20261122T001850Z-27778
AWS label/file structure PASS (qualified); MVS restore, member-byte fidelity and publication NOT authorized.
TA.2 RC2 structure review RC=0
```

### Specific accepted assertions

- `TA2RC2WR`, **JES JOB 9339**: all **21** MVS `IEBGENER` / `IEBCOPY` steps and their `IEF142I` confirmations RC=0000, replayed from the original SHA256-sealed one-shot evidence.
- Standard-label volume **`BC0002`** with **21** ordered `BCPL.BT0001`–`BCPL.BT0021` dataset header/trailer groups accepted by the independent AWS reviewer.
- Exactly **64** physical tape files, numbered **1–64**; 21 expected header/data/trailer triples and final zero-block file, with all data-file block counts nonzero and no layout discrepancies.
- HETMAP's `Summary` footer reports **64 files / 2,559 total blocks**, exactly reconciling to the individual physical files.
- Independently saved and fresh `hetmap -l/-f/-a` reports were reconciled without changing the tape.
- Existing candidate file: **1,957,296 bytes**; SHA-256 `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375`, checked before and after the read-only audit.

### Original artifacts and evidence

- Image: `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`
- Permanent no-retry intent: `workarea/ta2-rc2-production-operations/BC0002-one-shot-attempt.json`
- Original stateful write: `workarea/ta2-rc2-production-operations/20261121T231644Z-27163`
- First postwrite diagnostic (unmodified): `workarea/ta2-rc2-postwrite-audit/20261121T234319Z-27684`
- Qualified final structure review (original SHA256SUMS-sealed private receipt): `workarea/ta2-rc2-postwrite-audit/20261122T001850Z-27778`
- Frozen JOB-less 21-dataset JCL SHA-256: `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`

The preceding RC=2 from the original one-shot command is retained as a **post-write reporter parsing refusal**, not overwritten or represented as a failed MVS write. The HETMAP Summary parser was corrected **without regenerating or altering** the AWS.

### Acceptance limits and next gate

The assistant inspected the authoritative GitHub reviewer source and the owner's exact terminal output, **not** the private original `workarea/` bytes or the image itself. Thus this is a qualified owner-reported MVS/Hercules acceptance, not independent external access to the user's original system.

**TA.2 is not formally closed.** Outstanding: independent MVS tape readback, restored DCB/member inventory, actual record-content comparison and load-member/executable qualification, preserved candidate provenance and restore evidence. Clean recipient installation belongs to TA.3 and later marches. Redistribution-rights decisions and public publication remain separate.

**Immutable-media rule:** Never rerun the one-shot producer, reinitialize, overwrite, rename, unmount, remount or move `BC0002` merely to repeat accepted tests. Any new MVS tape readback or scratch DASD allocation requires a distinct owner-approved one-shot operation and fresh safety preflight. See [proposed independent MVS readback scope](ta2-rc2-independent-mvs-readback-proposal-20261121.md).
