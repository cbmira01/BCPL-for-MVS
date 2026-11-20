# TA.2 — Frozen Git-source lineage review

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**State:** Frozen Git source identity verified; redistribution and MVS build lineage remain pending.

## Accepted MVS staging

The owner reported **JOBS 9318/9319 PASS** for BT0001/BT0002 DCBs and four installer members on TSO002, following the one-shot staging JOB 9317. Together with previously accepted JOBS 9310–9312, **all 20 logical inputs have accepted MVS staging and DCB/directory checks**. This work does not repeat any successful MVS operation or perform a tape write.

## Actual frozen-source evidence

The approved candidate is **BCPL-0.1.0-rc1**, source commit **146ae09a58398c9b4d685500760f85592e770e1e**, VOLSER **BC0001 reserved**. On 20 November 2026, the assistant independently compared the complete, untruncated GitHub Git trees at the source commit and at main **2f951e2ec1ce023173d258710e0bcc7b3114c14f**. Paths were selected using the authoritative TA.0 dataset inventory and development DSPAL member mappings.

**110/110 selected Git-backed members have identical Git blob identities at both revisions; zero missing and zero changed.** This is stronger than an inferred path match but only establishes Git source identity—not MVS record bytes, redistribution rights, or a particular executable's build history.

The existing TA.0 audit identifies **110 Git-backed sources, two generated members and 15 resident object/load members**, for 127 selected payload members. The two generated items are BOOT_SOURCE(BLIB) and BOOT_ASM(COROUTIN). The object/load members include MR10 ICINT19, native runtime/BLIB/coroutine objects and extensions.

## Implemented source-lineage tool

The new *scripts/ta2-source-lineage* uses the existing canonical TA.0 validator and source provenance worksheet, not a new release inventory. It checks candidate/registry manifest SHA correspondence, selected member identity/order, approved Git revision ancestry, and ordinary non-symlink Git blobs at that revision and current main. It rejects selected source drift or changed identity. Default output is two compact lines; an optional new private JSON worksheet can be written exclusively under repository workarea.

For all 127 members the worksheet retains **redistribution UNREVIEWED, rights_ref null and build_receipt null**, and groups the work into historical material, historical derivation, project-or-derived, generated chain and resident binary build chain. These are review tracks, **not decisions**. The tool submits no JES, edits no MVS dataset, changes no Git branch, and creates no AWS media. The approved manifest and registry remain unchanged.

**Local checks:** 21/21 synthetic offline tests plus Python syntax checks passed in the assistant's repository-root workspace; tool and tests were transferred as exact tested Git blobs. The tool has not yet been executed on the owner's full checkout; the above real source comparison used GitHub's Git object trees.

## Rights and next gates

Project LICENSE.md grants MIT terms to original work unless stated otherwise. THIRD-PARTY-NOTICES.md and PUBLIC-RELEASE-AUDIT.md distinguish archived historical BCPL material and close derivatives: public archival availability and the repository's preservation-first policy **do not themselves grant a blanket license to redistribute a new AWS tape**. The TA.0 audit also warns that original build receipts for 17 generated/resident members need explicit source-to-output provenance.

Next review source-family redistribution decisions and connect actual retained BCPL/IFOX/IEWL build receipts to those 17 inputs. Continue using the existing strict final TA.2 producer gate; do not bypass it. Any subsequent approved change to the candidate manifest must rebind the registry manifest SHA under owner review.

**TA.2 IN PROGRESS.** No BC0001 tape image, label/readback acceptance, publication or TA.3 installation has been authorized or performed. TA.0 and TA.1 qualified closures remain unchanged.
