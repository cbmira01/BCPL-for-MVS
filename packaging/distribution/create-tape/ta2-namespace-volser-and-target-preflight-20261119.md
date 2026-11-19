# TA.2 — Approved staging namespace, production VOLSER policy, and read-only target preflight

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**State:** Owner-approved naming conventions; read-only target preflight implemented but **not executed on MVS**.

## Owner decisions

1. **Staging PDS DSNs:** exactly
   `HERC02.BCPL.TA2STG.BT0003` through `HERC02.BCPL.TA2STG.BT0020`,
   corresponding to the manifest's proposed 18 curated logical tape
   dataset positions and 127 selected PDS members.
2. **Production tape volume serials:** `BCnnnn`, `BC0001` to `BC9999`,
   monotonically assigned and never reused after an image is created.
   Serial numbers are not release versions or `BCPL.BTnnnn` dataset
   sequence identifiers. `BC0000` is invalid.
3. These approvals do **not** allocate DASD, reserve `BC0001`, freeze a
   source revision, create a candidate registry/manifest, initialize media
   or authorize any IEBCOPY or other state-changing MVS job.

The former design illustrations of alternative namespace/serial formats
are superseded by these exact owner decisions. The single TA.0 design
manifest remains the only curated member selection authority.

## Read-only target collision inquiry

`packaging/distribution/create-tape/scripts/ta2-target-preflight`
is the next MVS-facing tool. It requires the exact saved TA.2 stage-plan
evidence directory and a *proposed* DASD VOLSER argument, with explicit
`--live` needed to contact MVS.

Before any JES submission, it loads the canonical TA.0 inventory and
replays the stage-plan report and its original source/capacity evidence
chain using the existing `ta2-stage-jcl` validator. It refuses source
mapping, member count, DCB, checksum or record drift. It derives the
18 approved staging DSNs itself; there is no editable second selection.

With `--live --volume TSO002`, it submits and saves exactly two **read-only**
MVS JES inquiries, through the existing authenticated `dspal-core`:

- One TSO IKJEFT01 `LISTDS 'DSN' LABEL` job for all 18 proposed
  staging DSNs, requiring explicit recognized *not-in-catalog* output
  for every DSN and refusing contradictory attributes.
- One IEHLIST `LISTVTOC FORMAT,VOL=SYSDA=TSO002` job for the
  **proposed, not allocated**, DASD volume. Its full original JES
  report is preserved; any selected staging DSN found in the report
  blocks further planning.

`TSO002` is a source-supported existing DASD VOLSER from earlier TA.1
restore observations, chosen for *read-only investigation only*. It is
**not yet approved as the staging destination** and its available free
tracks and uncataloged allocations are **not established** by mere
execution of this probe.

Both reports, JES job IDs, stage worksheet SHA-256, explicit volume and
derived destination names are preserved under a freshly created
`workarea/ta2-target-preflight/<timestamp>-<pid>/` with SHA-256 manifest.
Failures preserve their original reports and fail closed with no retry.
Temporary authenticated JCL files are confined to repository
`workarea/` for this runner. Reports may contain private JES content;
keep them ignored and do not commit them.

The VTOC output still requires a later independent volume free-space,
allocation/extent and uncataloged-collision analysis before any
state-changing staging JCL is approved. A clean catalog alone is
**not** proof that staging is safe. Staging primary/secondary tracks,
directory blocks and possibly alternate DASD placement remain open.

## Assistant isolated-workspace checks

- 43/43 selective staging JCL synthetic tests PASS, including
  owner-approved exact namespace enforcement and RECFM=U selection.
- 26/26 new target inquiry synthetic tests PASS: canonical sequence,
  duplicate/managed namespace, volume safety, JCL width, exact catalog
  absence, contradictory result, VTOC collision, one-shot two-job
  execution, no VTOC job after a failed catalog inquiry, evidence
  persistence, no-overwrite and restored temporary file environment.
- 9/9 direct `BCnnnn` regular-expression boundary tests PASS.
- Python AST checks for the four involved files PASS.

The previous `ta2-offline` producer fixture was updated to `BC0001`
and augmented with nonconforming-VOLSER tests, but its full historic
suite was **not executed in this isolated workspace**; this limitation
remains explicit. No assistant MVS run, source-byte comparison, IFOX,
IEWL, BCPL execution, stage allocation or tape verification occurred.

**TA.2 remains IN PROGRESS.** The next MVS observation should drive
actual staging volume/SPACE decisions, not host estimates.
