# TA.2 — All 20 staging inputs accepted; producer-source reconciliation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**Status:** All 20 input datasets have owner-reported successful MVS directory/DCB verification; release candidate media remains unbuilt and unauthorized.

## Actual MVS acceptance

The owner executed `ta2-bootstrap-stage-verify --live`, with this result:

```text
TA.2 BT INPUTS: 2/2 DCB PASS, 4/4 installer members, TSO002; MVS PASS.
MVS jobs: catalog 9318, members 9319.
Private MVS evidence: workarea/ta2-bootstrap-stage-verification/20261120T132703Z-22108
```

This completes the already accepted **JOB 9317** six-step BT0001/BT0002 staging. Earlier **JOB 9310** staged BT0003–BT0020 successfully; independent MVS **JOBS 9311/9312** confirmed all 18 PDS directories, 127 selected members and required DCBs, including `MR10_LOAD` `PO/U/0/6144`. All 20 input datasets therefore have accepted stage execution and MVS directory/DCB evidence on **TSO002**: **one PS (BT0001) and 19 PDSes (BT0002–BT0020)**. Preserve all existing results. **Do not rerun staging or revalidate IBM utility copying** without concrete evidence of a problem.

The new tool `packaging/distribution/create-tape/scripts/ta2-complete-stage-inputs` composes the original immutable MVS verification receipts through the existing historical 18-PDS input mapper and the exact canonical `BCPL-0.1.0-rc1` candidate manifest. It validates the saved BT0001/BT0002 SHA256SUMS, checks the original MVS job IDs and exact four installer members, preserves all 127 unchanged selected payload members, and checks the candidate manifest SHA against the one `BC0001` registry reservation. It adds no MVS utility call, creates no release manifest or AWS tape, and makes no claim of member byte comparison. Optional JSON output is exclusive under ignored `workarea/`.

**Offline verification:** 10/10 focused synthetic tests and Python bytecode compilation passed in the assistant workspace, including exact 20-input reconciliation, wrong job/DSN/manifest/volser, evidence-file tampering and no-overwrite. The assistant did not directly access the private MVS JES reports, so the user’s original live result is recorded as an **owner-reported** accepted checkpoint, not an assistant-replayed live result.

## Actual next producer blockers

- The candidate `packaging/distribution/manifest/releases/BCPL-0.1.0-rc1.yaml` already fixes the approved version, candidate, frozen Git SHA and `BC0001` VOLSER, and retains the canonical TA.0 exact dataset/member selection. Those identity values must not be changed for this candidate.
- Its final producer metadata and **per-member redistribution-rights, source/transform/build lineage and build receipts** remain incomplete. Existing TA.0 provenance auditing distinguishes 110 Git-backed selected members, 2 generated and 15 resident binary members; that earlier audit describes **127 unreviewed rights decisions**, not an MVS failure. Do not auto-approve rights from successful IEBCOPY or invent source lineage.
- The strict `ta2-offline --candidate` gate also expects approved `source_dcb`, `unload_dcb`, `producer_source_dsn`, cryptographically bound saved MVS `stat/ls` evidence and generator hashes for the frozen release manifest. The accepted raw LISTDS reports may be reused as evidence; do not submit duplicate verification jobs simply to manufacture differently formatted receipts. Any adapter must preserve the original evidence seal and source identities.
- Production `BC0001` AWS initialization/write, physical label/readback, independently usable installer, final acceptance and publication remain separate authorization and verification gates.

The **current stage remains TA.2 IN PROGRESS**. TA.0 and TA.1 remain CLOSED (qualified). The following official march is still **TA.3 — MVS Bootstrap and Installation**, not a newly numbered milestone.
