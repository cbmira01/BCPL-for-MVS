# TA.2 — Offline bootstrap and MVS-only installer material generator

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026 EST / 20 November 2026 UTC  
**Status:** Offline implementation; no release candidate, tape or MVS staging authorization.

## Accepted baseline

The owner accepted TA2STAGE JOB 9310 and independent MVS `LISTDS` JOBS
9311/9312 as sufficient evidence that the 18 exact PDSes and 127 members
were staged on TSO002. The project trusts established IBM MVS utilities
absent a concrete anomaly. Nothing in this change repeats or modifies that
staging or attempts to independently certify IEBCOPY byte copying.

The accepted distribution design reserves **BCPL.BT0001** for an initial
human-readable EBCDIC FB80 sequential file and **BCPL.BT0002** for an
MVS-only IEBCOPY-unloaded installer PDS. BT0003–BT0020 remain the exact
manifest-selected source, object, load and documentation PDSes. The first
two logical datasets are **not** part of the accepted 18-PDS staging.

## Implemented bounded generator

`packaging/distribution/create-tape/scripts/ta2-bootstrap-installer`
prepares **offline material only** from the canonical TA.0 20-position
inventory and a later, frozen candidate manifest. Its command-line entry
point calls the existing `ta2-offline --candidate` gate first. This requires
the canonical registry reservation, source freeze, evidence checks and
member provenance before generation; no alternate manifest or registry is
invented.

It renders into a new directory directly under ignored `workarea/`:

- `BT0001.txt` — reviewer-readable ASCII record text identifying candidate,
  version, source SHA, VOLSER, native-compiler status and the exact 20 logical
  dataset aliases; `BT0001.ebcdic-fb80` — the same records, encoded as
  **exactly 80 CP037 EBCDIC bytes per logical record** with EBCDIC blank
  padding. No newline or carriage-control bytes are appended to the binary
  file. Actual MVS transfer/staging remains a separate verified operation.
- `BOOTREAD1.jcl` — JOB-card-free IEBGENER body to print logical tape
  dataset 1 with `LABEL=(1,SL)` and the candidate VOLSER. It requires a
  recipient-supplied tape unit.
- `BOOTREAD2.jcl` — JOB-card-free IEBCOPY body to restore logical tape
  dataset 2 with `LABEL=(2,SL)` into a **NEW** MVS installer PDS. The site
  must fill in HLQ, DASD allocation and tape unit. It must not overwrite an
  existing dataset.
- Four BT0002 proposed PDS source members (`INSTALL`, `DATASETS`,
  `RELEASE`, `RESTORE`) in both reviewer-readable `.txt` and exact EBCDIC
  FB80 `.ebcdic-fb80` representations. `RESTORE` is a **deliberately
  non-submittable** 18-step IEBCOPY JCL template. Recipient replacements
  of `<HLQ>`, `<TAPE>`, `<DASD>` and each `<P>`, `<S>`, `<D>` allocation
  are required before a site can submit it. The exceptional
  `MR10_LOAD` target DCB remains `PO/U/0/6144`; the others are
  `PO/FB/80/800`.
- `materials.json` — offline file identities and SHA-256 for local review;
  it is **not** an AWS checksum or MVS evidence.

All JCL DD allocations for data recovery/restoration use standard MVS
IEBGENER/IEBCOPY, without BCPL, Python, `dspal`, developer HLQ or a
new runtime program on the recipient. All generated cards are checked for
80-column limits, JCL statements for column-71 limits, and dataset/member
selection against the authoritative inventory. Output creation is
exclusive (no overwrite). The generated cards intentionally have no JOB
card and contain visible unusable site placeholders until reviewed.

## Verification and further work

**20/20 focused offline synthetic tests pass** and Python compilation
passes in the assistant's repository-root workspace. Cases include the
exact inventory and 127 members; 20 standard-label aliases; 80-byte EBCDIC
record padding; manifest identity and no native-compiler claim; 18
IEBCOPY steps; `RECFM=U` preservation; missing/altered source members;
JCL widths, recipient independence, unknown site parameters, checksum
identity and output no-overwrite. These are *not* actual MVS executions.

This increment does **not** create either the actual BT0001 sequential DASD
input or the BT0002 installer PDS, submit a JES job, mount a tape, reserve
a production VOLSER/version, or establish an installer profile. The installer
is a site parameterization **proposal** pending later MVS tests and TA.3
installation decisions. Before TA.2 candidate production, the owner must
approve/freeze the candidate identity/rights and authorize the separate
MVS input-staging and tape-writing operations. Actual JES, IEBCOPY and
Hercules tape labels/readback will determine whether the proposal works.

**TA.2 remains IN PROGRESS.** TA.0/TA.1 qualified closures unchanged;
no TA.3–TA.8 renumbering or premature closure.
