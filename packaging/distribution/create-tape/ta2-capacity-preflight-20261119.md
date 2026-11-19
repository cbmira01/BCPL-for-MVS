# TA.2 — MVS source-capacity preflight (read-only)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** Implemented as an unexecuted, read-only MVS inquiry; **not a staging allocation or tape-production authorization**.

## MVS evidence basis

The owner's corrected `ta2-source-preflight --live` execution reported
18/18 PDSes, zero blockers, 127 selected members, and **76 unselected
members**. Its private evidence is retained in
`workarea/ta2-source-preflight/20261119T140206Z-15135`.
This report establishes read-only MVS dataset metadata and selected-member
presence, **not** source bytes, binary provenance or authorization to
redistribute.

The independent `ta2-source-review` rechecks the private `dspal` results,
SHA-256 inventory and all 127 manifest-selected names. The original
private files have not been supplied to the assistant, so its verdict on
those exact records still requires execution in the owner's MVS host
workspace.

## New MVS space observation

`packaging/distribution/create-tape/scripts/ta2-capacity-preflight` takes
one explicit `--source-evidence` directory and requires `--live` for an
MVS inquiry. It **first independently reviews** the saved source-inventory
evidence and refuses mismatches. It then invokes the existing read-only
`tools/datasets/dspal stat` *without a dataset operand*, which uses TSO
LISTDS and MVS IEHLIST for managed PDS allocation observations. It
validates the exact 18 manifest-selected PDS names, volumes, source DCBs,
track allocation/high-water marks, extents and PDS directory blocks.

The MVS report is captured privately in a **new**
`workarea/ta2-capacity-preflight/<timestamp>-<pid>/` directory together
with a summary and SHA-256 checksums. Failure is terminal and preserves
a separately marked refusal record; the tool does **not** modify or
allocate MVS datasets, initialize/mount tape, or choose a release identity.
The console receives only a short result and evidence-directory path.

**Do not infer that the observed tracks through the VTOC high-water mark
represent the exact compacted payload size.** PDS replacement and freed
extents make that inference invalid. Before selecting staging `SPACE`,
review observed source allocations with a conservative margin and test
actual IEBCOPY selective staging on MVS, separately authorized. A
future 18-PDS staging operation must select **only** the 127 manifest
members, not the 76 extra development members. Its destination names,
allocation parameters, precise MVS operation bounds and failure handling
are not yet approved.

## Offline verification and authority

The assistant's isolated workspace ran the complete 94-case focused TA.2
synthetic suite, including 17 new capacity-parser, metadata and evidence
persistence checks, with no MVS/DASD/tape operations. Python syntax
compilation succeeded. The tests include `RECFM=U` load PDS, missing or
mismatched DCB/volume/DSN, failed or ambiguous IEHLIST track/directory
observations, duplicate headings, digest persistence and refusal to
overwrite existing evidence.

**Next gate:** The owner may issue a new read-only MVS source capacity
inquiry and report its compact result. Its actual LISTDS/IEHLIST output,
not estimated host allocation, determines whether planning can proceed.
No candidate ID, source freeze, release version, VOLSER, AWS image or
state-changing MVS JCL has been created. TA.2 remains **IN PROGRESS**.
