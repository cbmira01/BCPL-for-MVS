# TA.2 — Selective staging deck design and guarded offline implementation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**State:** **Draft-only code, no MVS staging/allocation/tape operation authorized.**

## Owner-reported MVS staging-plan checkpoint

At GitHub `main` `ebafb31321ef0e35b988addd2496b3d39cb17f1d`, the
owner ran `ta2-stage-plan --live` against the previously checksum-pinned
source/capacity receipts. The actual MVS-facing result was:

```text
TA.2 STAGE PLAN PREFLIGHT: 18/18 source PDSes; 127 selected; 76 excluded; 0 blockers
Private MVS planning evidence: workarea/ta2-stage-plan/20261119T155947Z-17087
No staging allocation, data copy, candidate identity or tape change.
```

This is owner-reported read-only MVS LISTDS/IEHLIST evidence; the private
numeric space data and original raw MVS reports were not transferred to the
assistant. Source-to-Git member-record identity, 15 binaries' build receipts
and redistribution rights remain unverified.

## Guarded staging JCL generator

`scripts/ta2-stage-jcl` is an **offline-only**, deliberately non-submitting
staging-deck renderer. It accepts a saved `ta2-stage-plan` evidence directory.
Without separate allocation parameters it reports only the validated
18-source, 127-member source selection. It checks the original
`stage-worksheet.json` and `dspal-stat-all.txt` against a complete
`SHA256SUMS`, refuses symlinks, missing/extra evidence, failed MVS RC,
and unexpected/stale source or member maps.

**Independent historical replay:** It re-runs the TA.2 source-review,
rechecks the pinned capacity evidence against its original LISTDS/IEHLIST
output, compares the final saved `dspal stat` observation with the capacity
baseline, and reconstructs the worksheet from the **single canonical
TA.0 design manifest**. A worksheet rehashed after modification but no
longer supported by raw MVS evidence is refused.

An *additional* operational allocation proposal, not a competing release
member manifest, must provide schema 1, the exact worksheet SHA-256,
a proposed isolated staging namespace, and **18 explicit** ordered
destination DSNs, target DASD volumes and
`primary_tracks/secondary_tracks/directory_blocks` allocations. These
parameters are **not chosen or approved yet**. The tool refuses
unrecognized/missing fields, duplicate source/destination identities,
managed-source namespace overlap, invalid MVS qualifiers, malformed space
parameters and noncontiguous tape positions.

Only with all inputs does `--allocations ... --output ...` write one
**JOB-less, draft-only**, private, exclusively created JCL file under
`workarea/`. The deck contains **18 IEBCOPY selective-copy steps** in the
proposed BT0003–BT0020 order and exactly **127 `SELECT MEMBER` cards**.
Source PDSes are `DISP=SHR`, new distinct destinations are
`DISP=(NEW,CATLG,DELETE)`, and subsequent steps use
`COND=(0,NE)`. The `RECFM=U` `MR10_LOAD` stage receives
`PO/U/0/6144` without incorrectly adding an FB80 record DCB.
Source/target selection and source DCB derive from the manifest,
never the operational destination map. A nonzero step leaves any earlier
successful staging allocations present: **never retry** or reset without
separate investigation/approval.

No JCL is submitted or previewed in the console. No data set is created,
opened for writing or deleted, and no Hercules/tape/volume identity is
allocated. The tool has **no run/submit option**. The draft's initial
comments explicitly disallow submission. This does not satisfy the later
fresh target-catalog absence, free-DASD capacity, MVS control-card syntax,
record identity or executable-restore acceptance gates.

## Operational decisions still required

The release owner must first approve the actual staging namespace and each
destination DASD volume and `SPACE` allocation after review of MVS
capacity/free-space evidence. The source PDS high-water mark is not a proof
of curated, compacted footprint. An illustrative synthetic test namespace
`HERC02.BCPL.TA2STG` and synthetic `TSO002` volumes are **not operational
decisions**; no corresponding allocation map is committed to GitHub.

Before staging execution, implement and demonstrate fresh read-only MVS
source identity, target catalog absence, target volume availability and
an exclusive one-shot job receipt. Separately authorize state-changing
IEBCOPY, inspect exact staged DCB/directories/127 members with no extras,
verify record/binary fidelity and provenance, then create the release
bootstrap/installer and fully frozen candidate manifest as the official
milestone requires. Preserve BTA101/BTA102.

## Offline verification

42/42 focused `test_ta2_stage_jcl.py` synthetic tests passed in the
assistant-owned repository-root workspace, with Python AST/syntax checks
passing. Tests cover member counts/selection, 18 guarded steps,
`RECFM=U` treatment, exact JCL column widths, stage-map namespace and
DSN collision checks, invalid allocation sizes, receipt checksum and
symlink/failed-MVS inquiry refusal, absence of write-on-failure, private
non-overwriting draft creation and no source/history bypass. These are
**offline tests**, not actual target MVS IEBCOPY execution. Earlier TA.2
test suites were not rerun in this isolated workspace.

**TA.2 remains IN PROGRESS. No staging dataset, release candidate, VOLSER
or AWS tape has been created or reserved.**
