# TA.2 — BT0001/BT0002 accepted preflight and proposed next authorization

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026 UTC  
**Status:** Read-only MVS bootstrap staging-target preflight **ACCEPTED** (qualified); next MVS staging and candidate identities **NOT AUTHORIZED**.

## New owner-reported actual MVS result

The owner ran `packaging/distribution/create-tape/scripts/ta2-bootstrap-target-preflight --live` and, separately, the independent **offline replay** of the original MVS evidence using `scripts/ta2-bootstrap-preflight-review`. Their compact original output is:

```text
TA.2 BT TARGET PREFLIGHT: 2 catalog-absent; TSO002 VTOC observed.
Private MVS evidence: workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572
No allocation, tape write or repeat of accepted JOB 9310.
TA.2 BT SAVED MVS REVIEW: 2/2 absent; IEHLIST free tracks 15400; proposed budget 31.
Private review: workarea/ta2-bootstrap-preflight-review/20261120T030402Z-20698
No new JES jobs, staging allocations, candidate VOLSER or tape write.
```

The **15,400** free tracks are the IEHLIST-reported quantity from the user's actual MVS saved output, reviewed by the existing project readers; the assistant has **not** independently accessed the private full raw MVS report in this workspace. The 31-track allowance is 5+1 for BT0001 and 20+5 for BT0002: primary allocation and one secondary extent each, **not** a guaranteed maximum extent budget. These observations are sufficient to accept this **read-only** staging namespace/capacity preflight. Actual MVS allocation, JES and source/member creation still determine success. Do not rerun successful inquiry jobs routinely.

The 18 accepted stage PDSes BT0003–BT0020 (JOB 9310; independent JOBS 9311/9312) remain unchanged, without additional byte-comparison gates.

## Concrete proposal for owner decision, not assignment

The next work needs **both** a release-specific bootstrap identity and a narrowly bounded two-dataset MVS write authorization. To avoid a premature production reservation or staging with throwaway identity, propose the following values **for discussion only**:

| Item | Proposed value | State |
| --- | --- | --- |
| Release version | `0.1.0-rc1` | Unapproved |
| Candidate ID | `BCPL-0.1.0-rc1` | Unapproved |
| Source Git freeze | `146ae09a58398c9b4d685500760f85592e770e1e` | Proposed baseline only; final validation pending |
| First production VOLSER | `BC0001` | **Not reserved**; requires collision review and Git registry reservation |
| BT0001 DASD target | `HERC02.BCPL.TA2STG.BT0001`, TSO002, PS/FB/80/800, `SPACE=(TRK,(5,1))` | Read-only preflight accepted; allocation not approved |
| BT0002 DASD target | `HERC02.BCPL.TA2STG.BT0002`, TSO002, PO/FB/80/800, `SPACE=(TRK,(20,5,10))` | Read-only preflight accepted; allocation not approved |
| New MVS job | Six-step IEBGENER/IEFBR14 stage deck from the canonical manifest-driven bootstrap generator | **Not approved for submission** |
| Production AWS image and tape writer | 20 logical datasets, standard labels `BCPL.BT0001`–`BCPL.BT0020` | **No media creation authorization** |

If the owner accepts the identity values, stage-specific SPACE and one-shot JES authority, the project can commit its frozen release-specific manifest, registry/authorization material and guarded stage runner, then generate/submit the exact BT0001/BT0002 deck under independent collision/readiness checks. As before, all new generated work stays under `packaging/` (tracked), `workarea/` or `mvs-state/` (ignored). No owner host patching, new branches, or restaging of BT0003–BT0020.

**Important qualifications:** The 127-member release rights/provenance reviews, MVS-recorded BT0001/BT0002 source artifacts, canonical strict `ta2-offline --candidate` gate, installation execution and independent tape labels/readback are still open. Approval of these proposed *DASD stage allocations* must **not** be construed as production tape authorization or release publication. The candidate release may declare the native-running Cambridge Compiler `absent`, but must not claim two programming compilers.

## Scope and next checkpoint

On approval, the next MVS evidence must be **actual** six-step IEBGENER/IEFBR14 execution and catalog/DCB/member results for exactly BT0001/BT0002. Trust those successful IBM utility results absent a concrete defect. Follow the authoritative TA.2 and TA.3 acceptance criteria afterward; do not invent additional IBM-utility certification tests.

**TA.2 remains IN PROGRESS.** Qualified TA.0 and TA.1 closures remain unchanged; TA.3–TA.8 march names and numbering remain intact.
