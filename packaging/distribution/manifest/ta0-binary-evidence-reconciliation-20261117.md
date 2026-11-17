# TA.0 — Development binary evidence reconciliation and JOB 9061 executable-use acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** JOB 9061 **development-load executable-use verified (qualified)** by owner-reported, twice-repeated pinned-evidence review on 17 November 2026. **TA.0 remains IN PROGRESS.**

## Actual MVS evidence

The owner ran the already-committed once-only `run-or-review-icint19.py` twice against the same saved private evidence under `workarea/ta0-mvs-evidence-20261117/`. Both returned:

    TA.0 ICINT19 GATE: SAVED_EXECUTION_VERIFIED JOB=9061
      PREFLIGHT=OK_NOW REPORT=PINNED_JES_AND_BCPL_RESULT_VERIFIED
      SUBMITTED_IN_THIS_INVOCATION=NO

The verifier checks the *original saved* `TA0ICEX` JES report and summary, all five SHA-256-pinned attachments, retained JOB 9060 directory review, eight expected steps at RC=0000, interpreted `CODE=0`, and scalar/vector actual outputs:

    RP: SCALAR 17 42
    RP: VECTOR 5 10 15 20

The eight steps are the approved `MRREGRES` scalar-vector subset: `SSYNI`, `STRNI`, `SCGI`, `SBLIBI`, `SICLIB`, `C01A`, `G01A`, `R01`, with three `ICINT19` program invocations using `HERC02.BCPL.MR10KIT.LOAD` as `STEPLIB`. JOB 9061 was **not resubmitted** by either later review. The private report and its binary pins were not copied into Git or directly inspected in the assistant's workspace. This is an **owner-reported live-system observation validated by the committed tool**, not a synthetic MVS result.

**Qualified acceptance:** the development `MR10_LOAD(ICINT19)` module was successfully executed in this bounded existing MR10 workload. Its directory listing from JOB 9060 showed entry `000000`, attr `02E2`. Do **not** infer independent `RECFM=U` module-byte equivalence, Git-source revision binding, unload/restore or execution after tape installation. Those are distinct subsequent gates. The full MR10 12-case `EXP:`/`RP:` review remains TA.4 work.

## Consolidated read-only reconciliation

`tools/distribution/reconcile-ta0-binary-evidence.py` provides one follow-up read-only reconciliation over the **single authoritative design inventory** and historical object readback ledger:

- Read the exact 14 selected `EXT_OBJ` (3), `MR10_OBJ` (1) and `BOOT_OBJ` (10) members and DCBs from the canonical TA.0 manifest; reject changed member sets or order.
- Revalidate all source `IEBPTPCH` receipts, their five saved file digests, JES results and printed FB80 records through the **existing strict decoder**. Recheck every decoded object against its private stored bytes, per-member receipt, panel receipt and the published MVS job/record/hash ledger, including the recovered EXT panel's original failure provenance.
- Reuse the current `ICINT19` receipt inspector on the unchanged JOB 9060/9061 files, requiring `SAVED_EXECUTION_VERIFIED` (not mere receipt existence).
- After all checks succeed, write only `workarea/.../<new-output>/reconciliation.json` as a private derived evidence index. The index is neither a new release manifest nor an authoritative source selection; it preserves the distinction between printer-output identity and original DASD bytes. Failure creates **no** new output directory.

The reconciler submits **no** JES job, changes no permanent MVS dataset, initializes no tape, and prints no JES report or password. It deliberately pins the 17 November 2026 historical jobs; a future candidate must use separate frozen build and release evidence rather than relabeling these receipts as production proof.

## Offline verification

The standalone reconciler has **14** locally passing synthetic tests, covering correct and recovered panels, changed design selection, order, reported jobs, source-printer integrity, decoded object bytes/receipts, altered load execution/job metadata, and no-side-effect behavior. Python compilation was checked. Existing `IEBPTPCH`/`IEHLIST`/`ICINT19` component verifiers remain independently tested, but those historical tests are **not** counted in the 14 new tests.

## Still open

TA.0 requires actual source-to-resident binary lineage/producer receipt binding, historical and project redistribution review, generated `BLIB`/`COROUTIN` provenance, exact MVS DCB/source/unload/target mapping, recipient JCL independence, and owner review of proposed post-`BT0002` positions. **TA.1** separately requires owner-authorized fresh scratch tape testing and `RECFM=U` IEBCOPY unload/restore followed by GO. No candidate, unique VOLSER, tape write, TA.0 march closure, or publication is authorized by this evidence.


## Live reconciliation refusal and narrow schema correction — 17 November 2026

The first live invocation of the consolidated reconciler returned
`DECODE_RECEIPT_MISMATCH`. No new JES jobs were submitted; because the
reconciler verifies before creating its destination, no reconciliation
receipt was produced. The error is **not evidence of changed MVS object
bytes** or invalid JOB 9061 execution.

Investigation identified an exact version difference in the checked-in
decoder implementations: the decoder used before the JOB 9048 pagination
fix omitted the `repeated_page_headings` metadata field. The later decoder
adds it to *every* member, including members with no pagination. The
reconciler had compared old saved metadata against new metadata with a
strict full-object equality check. This is the leading cause; the user's
private receipt bytes were not independently examined in the assistant
workspace. See [the compatibility investigation and constraints](ta0-reconciliation-schema-compatibility-20261117.md).

The revised reconciler accepts the old schema **only** when newly decoded
printer evidence confirms integer zero repeated headings, with exact
equality of all other metadata and all existing SHA-256, JES, member,
record-count, binary and panel-receipt checks. It records each schema
variant and the legacy receipt count in the derived output. Original
evidence files are not rewritten. Live MVS reconciliation remains pending
until the owner runs the revised tool against the preserved evidence.
