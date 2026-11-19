# TA.2 — Manifest-derived staging plan and fresh MVS source-capacity replay

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** Read-only staging-planning preflight implemented. **No stage allocation, copying, candidate reservation or media operation authorized.**

## Actual MVS checkpoint

At GitHub main `eb9bf66ee6c31b9de8b2345f8d382b48b40ec572`,
the owner executed the approved read-only MVS source-capacity inquiry and reported:

```text
TA.2 CAPACITY PREFLIGHT: 18/18 source PDSes; 127 selected; 76 excluded; 0 blockers
Private saved MVS evidence: workarea/ta2-capacity-preflight/20261119T150315Z-16868
Source high-water and directory observations only; no staging/tape changes.
```

The assistant has **not** inspected the owner's private raw report or numeric
source track/directory observations. The compact owner-reported PASS is
evidence of source capacity metadata observation, **not** recipient DASD free
space, exact selected-member compact footprint, source-to-Git byte identity,
binary ancestry or redistribution permission. The previous 18-PDS source
inventory with all 127 curated members and 76 excluded development members
remains a distinct accepted read-only metadata checkpoint.

## New guarded stage-plan tool

`packaging/distribution/create-tape/scripts/ta2-stage-plan` has an inert
default mode. Its explicit `--live` mode requires both existing saved runs:

- `--source-evidence workarea/ta2-source-preflight/20261119T140206Z-15135`
- `--capacity-evidence workarea/ta2-capacity-preflight/20261119T150315Z-16868`

Before MVS contact it independently reruns `ta2-source-review`, verifies the
source-capacity evidence directory and original `SHA256SUMS`, checks the
saved `dspal stat` inquiry RC=0, pins the summary to the source receipt,
and **replays the source-capacity parser** rather than trusting the saved
summary. Extra, missing, linked or altered evidence fails closed.

Only after those checks, it invokes one **read-only** current managed
`dspal stat` inquiry (TSO LISTDS and MVS IEHLIST), requiring exact
DSN, VOLSER, DCB, allocation/high-water and directory agreement for the
18 selected development PDSes with the saved capacity receipt.
The tool records a fresh, exclusive, checksum-protected private run under
`workarea/ta2-stage-plan/`.

The resulting `stage-worksheet.json` has the manifest's proposed
BT0003–BT0020 sequence, selected member names and per-source MVS
capacity observations. Every entry leaves `staging_dsn: null`,
`stage_space: null`, `allocation_approved: false`.
It does not invent a staging name, estimate compacted member bytes,
recommend a fixed `SPACE` allocation, render a write job, call IEBCOPY,
or reserve a release version/VOLSER.

On a failed or changed MVS observation, original read-only output and a
separate `failure.json` are preserved; no automatic retry is attempted.

## Next accepted design and MVS decision gates

1. Examine actual per-source tracks/volumes from the private
   checksum-protected worksheet, investigate destination DASD free space
   and decide conservative, explicitly approved stage `SPACE`/directory
   allocations rather than treating VTOC high-water as compacted bytes.
2. Choose isolated candidate-specific MVS staging names and check
   destination catalog absence, exact source volumes, DCB and device
   readiness immediately before any state change.
3. Generate 18 guarded MVS IEBCOPY selective-copy steps from the **one**
   manifest, with exactly 127 members selected; prove 76 extra development
   members are excluded. Require preallocated empty targets, no retry or
   overwrite, and recorded exact target inventories and records.
4. Separately prove source-to-staged records, `RECFM=U` load-module
   usability, generated `BOOT_ASM(COROUTIN)` and `BOOT_SOURCE(BLIB)`
   lineage, all 15 binary-member build receipts and redistribution rights.
5. Review the complete proposed 20-logical-dataset tape producer including
   bootstrap/installer before separately authorizing identity reservation,
   new AWS tape or state-changing JES/DASD operations.

The only authoritative release-selection authority remains the TA.0
design manifest until a separately approved candidate is frozen. Do not
reuse BTA101/BTA102; preserve earlier accepted TA.1 evidence.

## Assistant-workspace verification

The added `tests/test_ta2_stage_plan.py` contains **31 synthetic tests**,
all passing in an isolated repository-root workspace; both Python files also
passed AST parsing. The cases include end-to-end mocked MVS read-only
execution, exact evidence/checksum parsing, invalid RC, forged summary,
source linkage mismatch, member counts, DCB form, symlinks and foreign
directories, current MVS metadata drift, no-use-before-review and private
failure receipts. The historical 94 earlier TA.2 tests were not rerun
with this isolated focused test run. **No new live MVS execution was
performed by the assistant**; real MVS/JES/IEHLIST output remains the
next verification authority.

**TA.2 remains IN PROGRESS. No stage data set or candidate/tape identity
has been created or reserved.**
