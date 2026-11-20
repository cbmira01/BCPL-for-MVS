# TA.2 — rc2 historical-source-only correction and validation evidence

**Date:** 20 November 2026
**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone / march:** Tape artifact release / TA.2 — Manifest-Driven Tape Producer
**State:** Owner-approved release-selection correction committed; no new MVS write or AWS tape operation performed.

## Owner design decision

The GitHub-specific, transformed and regression-instrumented **demoted
Cambridge Compiler is development infrastructure**, not MVS-distributable
source in isolation. Its generation scripts, filters, test machinery and
development dependencies remain in GitHub repository context.

Keep the distinct historical **Cambridge Compiler** sources on the MVS
tape. Retain release identity `BCPL-0.1.0-rc2` and reserved production
VOLSER `BC0002`; do not assign a third identity for this correction,
because no rc2 tape image was produced.

## Selected successor

- `BT0001`–`BT0020`: exact original `rc1` dataset selections and
  accepted MVS input staging evidence, unchanged.
- `BT0021`: `CAMB_SOURCE`; 15 historical archival members;
  `{HLQ}.BCPL.CAMBRIDG.SOURCE`; PO/FB/80/800.
- There is **no BT0022** and **no CAMB_DEMOTED** release source PDS.
  Derived `BCPL`, `BLIB`, `SYN`, `LEX`, `TRNA`, `TRNB`,
  `CGA`–`CGE`, support `BOOTHOST`, `CAMBPARM`, `CAMBBLD`,
  and the demotion-specific `SNOTICE` are not selected.
- `cambridge_source: included`; `native_compiler: absent`.
  This is not a claim of a native-running Compiler.

**Selection totals:** 21 logical tape datasets; 142 selected source,
documentation and binary PDS members (127 original + 15 historical).
The four `BT0002` installer members are separately counted.

## Committed identities

- Code, validator, and PDS map correction source commit:
  `78baec9a8546e4ab09caee779aa2b675379272f3`.
- Corrected canonical manifest + registry commit:
  `0106cb1d7d0254d084e5e2693e58704a35db022e`.
- Canonical `rc2` manifest SHA-256:
  `12b2dd8cc9c2edab033575bd3c60864be4a983b0e163fdec2823efb14086d19a`.
- `rc1` manifest Git blob is unchanged:
  `584b0aa8da424358f9477d4f69ba190dec106a03`.
- The original `BC0001` registry reservation and digest were
  preserved. A direct GitHub read-back confirmed both manifests'
  first 20 dataset blocks were **byte-for-byte equal**.

## Offline checks and limitations

In an independent assistant repository workspace, the exact Git blob
contents of `pack.py`, `successor-contract.py` and
`rc2-stage-draft.py` were copied, checked by Git blob SHA and
compiled by Python. A compact synthetic suite passed **5/5
unittest methods**, including **19 contract refusal cases, eight
staging refusal cases and two forbidden-development-deck cases**.
The source-only staging generator renders **one** JOB-less IEBCOPY
step with **15** selected members and 80-column JCL checks.
These local checks are not MVS acceptance and do not replace the
full project test suite.

The owner reported `dspal stat CAMB_SOURCE` RC=0 and the now-excluded
`CAMB_DEMOTED` RC=2. The untouched original MVS command reports
are at `workarea/ta2-rc2-mvs-20261120T194333Z-855`
on the owner's repository host; those report bytes were not sent
here and **have not been independently inspected**.

## Unaccepted gates

- Actual MVS member listing, DCB and record-fidelity comparison for
  the 15 historical source members remain pending.
- The new staging dataset `HERC02.BCPL.TA2STG.BT0021` has not
  been proven absent or allocated; any staging requires a separate
  review of fresh MVS evidence and explicit state-changing approval.
- Historical third-party redistribution rights, adequate notices,
  rc2 recipient bootstrap/installer reconciliation, final producer
  gate, AWS media, readback and clean-target installation remain open.
- No existing accepted BT0001–BT0020 staging or IBM utility
  certification work should be repeated without evidence of a defect.

**Next MVS-facing action:** perform `dspal ls CAMB_SOURCE` read-only
and review the actual MVS directory against the 15 canonical names.
The existing successful source `stat` need not be repeated.
