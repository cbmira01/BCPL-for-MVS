# TA.2 — Owner-approved one-shot BT0001/BT0002 MVS staging

**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026 (EST)  
**Status:** Exact six-step staging operation approved. Release identity and tape production remain unapproved.

## MVS evidence and approved scope

The owner ran the read-only `ta2-bootstrap-target-preflight --live`, reporting both staging targets absent and a TSO002 VTOC observation. Original sealed evidence: `workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572`. The owner subsequently ran the offline `ta2-bootstrap-preflight-review` against that evidence, reporting **15,400 IEHLIST free tracks** and the **31-track primary plus one-secondary allocation allowance**. Review: `workarea/ta2-bootstrap-preflight-review/20261120T030402Z-20698`.

The owner explicitly approved the **one-shot six-step BT0001/BT0002 MVS staging operation**. `ta2-bootstrap-stage-approval.json` records the exact two absent targets on TSO002, `PS/FB/80/800` BT0001 with `SPACE=(TRK,(5,1))`, `PO/FB/80/800` BT0002 with `SPACE=(TRK,(20,5,10))`, five IEBGENER steps and one IEFBR14 allocation step. It prohibits retries and excludes previously accepted BT0003–BT0020. No tape write or publication is authorized. The 31-track allowance is not a guarantee of extent contiguity or a maximum number of future secondary extents.

## Implementation and separate release identity gate

The new `scripts/ta2-bootstrap-stage-once` performs a strict read-only replay of the original, checksum-sealed preflight and review evidence. The runner requires the approved staging JSON to be committed and unchanged on the existing `main` branch, and requires a separately approved **release identity** record and committed canonical release manifest before writing. The owner explicitly approved the **operation only**, not the previously proposed version `0.1.0-rc1`, candidate ID `BCPL-0.1.0-rc1`, source freeze or `BC0001`. The file `ta2-bootstrap-identity-approval.json` therefore **does not yet exist**; the runner refuses submission without it. No VOLSER is reserved by this commit.

After an identity decision, the runner will use the already implemented canonical `ta2-bootstrap-installer` to derive the exact candidate-specific EBCDIC bootstrap and installer member records. It performs a fresh two-target MVS LISTDS/IEHLIST check, verifies the actual VTOC free-track report against the 31-track planning allowance, obtains one-character `Y` confirmation, creates an exclusive permanent one-shot intent marker, then submits the six-step MVS job. The authenticated job deck is not saved. Original job summary and JES report, completion receipts and a checksum seal are retained exclusively under ignored `workarea/ta2-bootstrap-stage-operations/`. A failed or ambiguous job **cannot be resubmitted** by this runner. Actual MVS IEF142I/RC results decide staging execution acceptance. A later read-only MVS catalog/member verification must check the two staged inputs; the successful IBM utilities are not independently reimplemented or byte-for-byte recertified.

## Local checks

The new runner was Python-compiled and **28/28 focused synthetic tests passed** in the assistant's workspace, including a simulated successful MVS submission, a failed submission retaining the no-retry marker, exact six-step card parsing, preservation of nested JCL as DD DATA, scope/space/tape refusal, separate identity gate and source-evidence binding. No MVS interaction was performed in the assistant workspace. These tests **do not** establish that the future generated JCL executes successfully on the user's MVS system.

**Next approval needed:** explicitly accept or revise the proposed candidate ID, version, source commit and VOLSER, and approve their binding to a release-specific manifest. Only then can the guarded one-shot staging job be submitted. No old staging needs to be repeated.

**TA.2 IN PROGRESS.** TA.0/TA.1 qualified closures and TA.0–TA.8 naming remain unchanged.
