# TA.0 — MR10_LOAD(ICINT19) IEHLIST directory inspection, JOB 9060

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** Owner-reported read-only MVS utility execution; formatted directory interpretation remains a separate live evidence gate. **TA.0 IN PROGRESS**.

## MVS execution observed 17 November 2026

The owner executed the committed `tools/distribution/inspect-ta0-mr10-load.py` on the MVS 3.8J TK5 system, using the previously collected and SHA-256-pinned `MR10_LOAD` `LISTDS MEMBERS` and `LISTDS LABEL` evidence. The operator-reported result was:

    TA.0 MR10_LOAD DIRECTORY: JOB 9060 TA0LDIR IEHLIST RC=0000
    Private evidence: /home/calvin/ta0-mvs-evidence-20261117/ta0-mr10-load-iehlist
    Listing requires inspection; no load bytes, executable or tape verified.

The job generator selected development dataset `HERC02.BCPL.MR10KIT.LOAD`, the one canonically selected load member `ICINT19`, and a `PO/U/0/6144` source DCB. It submitted one read-only `IEHLIST LISTPDS ... FORMAT` job. Its preflight required the separately pinned MVS `LISTDS` directory/DCB evidence and derived the resident volume from that evidence. Successful execution is an **owner-reported RC=0000 only**; neither the actual `IEHLIST` formatted member row nor the preserved original `job-report.txt` and `printer-window.raw` was available in the assistant's workspace when this document was written. Do not represent `ICINT19` as confirmed by the formatted directory until the live saved report has been processed.

## Safe, local interpretation of retained MVS evidence

`tools/distribution/verify-iehlist-load-directory.py` accepts **only the existing evidence directory** from that job and a **new output directory outside the Git checkout**. It never submits JCL, touches MVS datasets, reprints objects, modifies tape or reads the load-module byte stream. It validates the `receipt.json` schema and identity, pins of all five retained sources, expected JES START/END and IEHLIST/IEF142I RC=0000, exact saved JCL body, and the edited `IEHLIST` directory title, dataset/volume identification and member-table columns. It requires a **single non-alias `ICINT19` directory row with entry-point and attribute hexadecimal fields below the table heading**; a JCL `LISTPDS` echo or incidental `ICINT19` text is never sufficient. Ambiguous, unknown or truncated printed output fails closed.

The edited directory-column pattern derives from a published IEHLIST example showing `SYSTEMS SUPPORT UTILITIES---IEHLIST`, `DIRECTORY INFO FOR SPECIFIED PDS ON VOL`, `MEMBER / ENTRY / ATTR`, an entry-point/attribute row and the directory-block footer: https://yfuku.sakura.ne.jp/mvs/dsinf1.html . The operation and distinction between `FORMAT` (edited) and `DUMP` (unedited) are documented for MVS 3.8: https://www.jaymoseley.com/hercules/os_utilities/mvs_utilities.html . That reference is a *format specimen*, not observed JOB 9060 output. The parser intentionally rejects any format variation it does not yet recognize instead of incorrectly certifying a load module.

If successful, it produces one private `directory-review.json` recording the pinned source hashes and directory-only metadata. It does **not** mark the member executable, validate byte equality, determine linkage correctness, demonstrate `ICINT19` GO, perform an IEBCOPY transfer or verify a restored tape copy. A mismatched actual listing requires another investigation, **not** automatic resubmission of JOB 9060.

Twenty-four isolated synthetic tests pass (including positive published-format structure and negative/mutated report cases), with Python syntax validation. These tests do **not** claim access to original JOB 9060 SYSOUT or represent a live MVS acceptance result.

## Remaining evidence boundaries

- The 14 selected `MR10_OBJ`, `BOOT_OBJ` and `EXT_OBJ` FB80 relocatable objects have separate MVS printer readback receipts, 902 records / 72,160 decoded bytes. See [the object evidence ledger](ta0-fb80-readback-acceptance-evidence-20261117.md). They do not establish independent DASD byte equality or Git-to-MVS source ancestry.
- `MR10_LOAD(ICINT19)` uses `RECFM=U`; **no FB80 decoder may be applied** to its load-module contents. Directory information is not a load-module-byte hash.
- Executable use, `RECFM=U` IEBCOPY unload/restore and scratch-tape mechanics remain explicit further-stage checks; TA.1 tape writing requires separate authorization.
- The eight source/build receipts, historical BLIB/COROUTIN lineage, redistribution rights and candidate identification/registry remain open.

**No TA.0 closure, VOLSER reservation, TA.1 tape-write authorization or publication is implied.**
