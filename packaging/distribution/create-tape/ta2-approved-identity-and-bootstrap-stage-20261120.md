# TA.2 — Approved release identity and bootstrap staging handoff

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026 (EST)  
**Status:** Four release identity values approved and Git-controlled; one-shot BT0001/BT0002 stage separately approved; no MVS staging execution or AWS candidate media yet.

## Owner approval

After discussing the role of a release candidate ID, the owner explicitly authorized the four proposed values:

| Field | Approved value |
| --- | --- |
| Version | `0.1.0-rc1` |
| Candidate ID | `BCPL-0.1.0-rc1` |
| Source Git revision | `146ae09a58398c9b4d685500760f85592e770e1e` |
| Production VOLSER | `BC0001` |

The approved Git source revision is an ancestor of the current `main`; the subsequent two commits before the identity assignment modified TA.2 tools/milestone text rather than the selected source member files. That does **not** substitute for the final provenance and build-receipt review.

## Canonical records

- `packaging/distribution/manifest/releases/BCPL-0.1.0-rc1.yaml`: preliminary candidate identity grafted onto the exact TA.0 20-sequence design selection. The 18 source PDS member inventories remain **127 selected members**, unchanged. `native_compiler: absent` is disclosed. Its SHA-256 is `9eb6fe9c56059d27fa08c184eab7e402d6708fd0b246f6b58d35e9434dc40832`.
- `packaging/distribution/registry/releases.yaml`: first canonical registry entry, `state: reserved`, binds exactly this candidate ID, version, source commit, VOLSER and manifest SHA. **BC0001 is now reserved for this candidate**. It has not been used to initialize, label or write tape.
- `packaging/distribution/create-tape/ta2-bootstrap-identity-approval.json`: independent owner identity approval matching that exact manifest digest, declaring `production_tape_authorized: false`.

These records satisfy the preparatory `ta2-bootstrap-installer --prepare` identity inputs and the separately approved `ta2-bootstrap-stage-once` identity gate. They are **not** a claim that the strict final `ta2-offline --candidate` gate passes. The release manifest does not yet contain every member's redistribution-rights/provenance review, approved unload DCB and complete MVS source receipts; these remain explicit blockers for AWS candidate creation. No rights or evidence has been fabricated.

## Approved MVS step now enabled

A separate owner decision already authorized **one** six-step MVS staging operation to create only `HERC02.BCPL.TA2STG.BT0001` and `BT0002` on `TSO002`. The earlier read-only MVS inquiry returned two absent catalog names; the saved independent review returned IEHLIST **15,400 free tracks** against the **31-track initial-plus-one-secondary planning allowance**. Exact original private evidence is retained at:

- `workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572`
- `workarea/ta2-bootstrap-preflight-review/20261120T030402Z-20698`

Use the existing Git-tracked `scripts/ta2-bootstrap-stage-once --run --manifest <absolute candidate manifest path>`. It replays the saved MVS receipts and performs a fresh *read-only* two-target MVS LISTDS/IEHLIST check before asking for a one-character **Y** confirmation, writing a no-retry intent marker, and submitting the one-shot IEBGENER/IEFBR14 deck. Its operation approval fixes the SPACE triples `(5,1)` and `(20,5,10)`. The job's actual JES RC and IEF142I lines determine the outcome. Do **not** rerun on an ambiguous, partial or failed submission: preserve original evidence and investigate the concrete MVS result. Previously accepted BT0003–BT0020 remain immutable.

## Offline checks and later stages

The Git-created identity files passed **10/10 offline identity/inventory checks**, including the SHA-256 implementation's known-answer test, 20 contiguous datasets, unchanged TA.0 inventory, exactly 127 selected members, the `MR10_LOAD` `RECFM=U` exception, approved source SHA, registry singularity and no-tape authorization. No actual MVS job was executed during this commit.

After the six-step staging job, use actual MVS `LISTDS` attributes and exact BT0002 directory members to accept the two new inputs. Continue TA.2 with source/provenance/rights review, the existing strict producer gate, new AWS tape candidate generation only under separately approved media authority, and independent tape readback. TA.3 recipient installation verification remains later. **TA.2 IN PROGRESS; TA.0/TA.1 qualified closure unchanged.**

## Actual one-shot MVS staging execution — JOB 9317

The owner executed the authorized six-step `TA2BTSTR` job with the approved identity and reported **6/6 steps RC=0000**, after a successful fresh absent-name and TSO002 15,400-free-track preflight. Original MVS evidence: `workarea/ta2-bootstrap-stage-operations/20261120T132013Z-21957`. The next action is the new **read-only**, two-job `ta2-bootstrap-stage-verify --live` DCB/directory check. No rerun of JOB 9317 is allowed; the attempt marker is permanent. See [the JOB 9317 record](ta2-bootstrap-stage-job9317-and-verification-20261120.md). No BC0001 tape image was written.
