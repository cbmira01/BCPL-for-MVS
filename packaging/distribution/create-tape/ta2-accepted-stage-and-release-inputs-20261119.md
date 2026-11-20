# TA.2 — Accepted staging and release-input preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026 EST / 20 November UTC  
**Status:** **TA.2 IN PROGRESS**; 18 staged PDS inputs accepted; tape candidate not authorized.

## Owner decision: trust MVS utilities absent an observed defect

IEBCOPY, IEBGENER, IFOX, IEWL and other established MVS system programs are trusted components. Check **our selection, JCL, integration, status and actual results**. Additional independent examination of an IBM utility's internal copying behavior is justified by a concrete anomaly, not an imagined failure mode. This does not waive independent **tape readback/restore** and sequence/label integration evidence required by TA.2.

The previously proposed 126-step FB80 IEBCOMPR panel and bespoke RECFM=U load-module binary extractor were **not promoted**; they are unnecessary additional staging gates without evidence of a defect. No load-member byte hash is claimed. Do not change accepted TA.0/TA.1 statuses or TA.0–TA.8 numbering.

## Actual staging checkpoint accepted by owner

- **TA2STAGE JOB 9310:** selective IEBCOPY, 18/18 RC=0000, exactly 127 manifest-selected members staged on **TSO002**. Preserved private evidence: `workarea/ta2-stage-operations/20261120T002516Z-19547`.
- **JOBS 9311 and 9312:** independent MVS `LISTDS LABEL` and `LISTDS MEMBERS` checks, 18/18 PDSes and 127/127 selected members, no extras/missing/duplicates; expected attributes including `MR10_LOAD` `PO/U/0/6144`. Preserved private evidence: `workarea/ta2-stage-verification/20261120T005732Z-20183`.
- The owner-reported PASS and the existing independent read-only verifier support **acceptance of staging**. They do not establish a produced tape or recipient restoration.
- All staged `HERC02.BCPL.TA2STG.BT0003` through `BT0020` remain immutable and read-only producer inputs. **Do not rerun JOB 9310** or resubmit 9311/9312 as a routine gate.

## New non-state-changing producer-input map

`packaging/distribution/create-tape/scripts/ta2-release-input-plan` consumes only the canonical design inventory and the **existing SHA256-sealed 9311/9312 receipt**. It does not submit JES or reread staged members. It derives the exact logical aliases `BCPL.BT0001`–`BT0020` and the 18 staged PDS associations (`BT0003`–`BT0020`) from the existing manifest, preserving the 127 exact names and the `MR10_LOAD` exceptional DCB. It treats the original successful IBM utility work as accepted, rather than repeating it.

The read-only default prints two concise lines. Optional `--output workarea/<new-name>.json` writes an **exclusive**, non-authoritative private snapshot under repository `workarea/`; it refuses overwrite, unexpected evidence, mismatched acceptance identity, wrong DCB/order or changed member selection. This is a **derived input map**, not a second release manifest, version/VOLSER registry, tape producer authorization or release candidate.

It explicitly reports four remaining categories of work:

1. Prepare release-specific **BT0001** human-readable EBCDIC FB80 bootstrap. The existing `packaging/distribution/docs/README.txt` declares itself draft and is not automatically promoted to release text.
2. Prepare **BT0002** MVS-only installer PDS. `packaging/distribution/install-from-tape/` currently has no operable installer job; do not advertise a self-installing tape.
3. Freeze approved source, lineage/rights, candidate manifest, version and new unique VOLSER through the canonical manifest and registry. No identities have been invented or reserved.
4. Only with separate authorization, produce a **new** standard-labeled AWS candidate using the existing `ta2-offline` generated JCL and staged inputs. Test our label/sequence/mount/readback/restore integration on real MVS and preserve original JES, physical tape map, SHA-256 and provenance.

## Offline validation and boundaries

The new input-map tool passed **16/16 focused isolated offline tests**, including exact sequence, 18 PDS/127-member mapping, `MR10_LOAD`, absent/altered saved JES evidence, wrong job identity, unexpected reports, duplicate members, unsafe output path and no-overwrite writes. Python syntax validation passed. The assistant did not have the private MVS evidence in its workspace; no execution of the tool on the owner's exact reports is claimed.

The next real MVS-facing work should prepare/inspect the two **missing** release inputs—not repeat accepted IEBCOPY staging. Production tape initialization, JES tape writing, restoration, reservation and publication require their own specific authorization. TA.2 remains **IN PROGRESS** until the official complete candidate-media gate is satisfied.
