# TA.0 — Historical decoded-receipt schema compatibility, 17 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** Narrow corrective implementation; live re-reconciliation pending. **TA.0 IN PROGRESS.**

## MVS evidence observation

The owner ran `tools/distribution/reconcile-ta0-binary-evidence.py` on the retained
`workarea/ta0-mvs-evidence-20261117/` evidence. It stopped with:

    TA.0 BINARY EVIDENCE RECONCILIATION REFUSED: DECODE_RECEIPT_MISMATCH

This result **does not establish failed MVS execution, changed object bytes or
corrupt reports**. The reconciler did not create its output directory and
submitted no JES job. The printed diagnostic does not identify the offending
member; the owner's private decoded receipts were not provided for direct
inspection in the assistant workspace.

## Code-level cause and correction

The original IEBPTPCH multi-member decoder (Git `6f3fa0e7`) stored member
metadata without `repeated_page_headings`. The page-framing correction
(`9f39b662`) added this metadata field to every freshly decoded member.
The first members of the interrupted `EXT_OBJ` panel were decoded before
that change, and their original JSON evidence was preserved when the panel
was recovered. The reconciler wrongly required exact JSON equality against
recomputed metadata from the newer decoder. This schema evolution is the
leading code-supported explanation; the specific private receipt has not
been examined independently.

`tools/distribution/ta0_receipt_compat.py` now permits exactly two versions:

- **PAGE_AWARE_V2:** the saved metadata is identical to current strict decoding.
- **PRE_PAGE_V1:** only `repeated_page_headings` is absent from the saved
  metadata; current decoding must report **integer zero** repeated headings,
  and every other metadata key and value must match exactly.

A missing page counter where the current printer report has repeated page
headings is **rejected**. The reconciler still checks original pilot receipt
hashes, source JES report and printer-window hashes, original decoded-receipt
file SHA-256 in the panel, published record count and SHA-256 ledger, exact
FB80 binary byte equality, member order and identity, and the saved JOB
9060/9061 load-directory/executable-use evidence. It neither rewrites nor
upgrades any original MVS reports, decoded binaries, or receipt JSON files.
The derived reconciliation record includes a per-member schema classification
and the total number of accepted pre-pagination receipts. Follow-up schema
errors identify the selected source/member without printing private SYSOUT.

## Verification boundaries

Thirteen isolated no-MVS tests exercise both schema variants and reject
malformed, missing and altered metadata. Seven additional reconciler
regression cases exercise mixed old/new receipts, including an EXT panel with
recovery provenance, positive no-rewrite behavior, and tamper rejection.
These are development-host synthetic tests; no new JES job or tape operation
was executed. A successful live reconciliation must still be observed.

Do not use this compatibility rule as original source-to-DASD binary proof or
as independent RECFM=U load-module byte comparison. No scratch tape write,
release candidate freeze, VOLSER allocation, TA.0 closure, TA.1 authorization,
rights decision or publication follows from this correction.


## Live compatibility verification — PASS (qualified), 17 November 2026

The owner ran the corrected reconciler and observed complete reconciliation
of **14/14 FB80 objects, 902 FB80 records / 72,160 bytes** with **exactly
two** historical pre-pagination receipts. Both old receipts were accepted
only where the present decoder observed zero repeated page headings; the
original receipts were unchanged. The retained MR10 load-directory JOB 9060
and interpreter executable-use JOB 9061 passed the consolidated gate.

This supersedes the prior "live re-reconciliation pending" status in the
heading; no independent raw DASD or tape-byte identity is inferred.
The successful tool created its private derived reconciliation index in the
ignored workarea. No original evidence files were rewritten or JES jobs
submitted. Full release acceptance remains open.
