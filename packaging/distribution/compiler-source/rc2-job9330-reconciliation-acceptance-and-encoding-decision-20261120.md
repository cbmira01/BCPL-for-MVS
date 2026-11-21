# TA.2 — JOB 9330 reconciliation accepted; BT0021 source-encoding decision

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026 EST  
**Source of authority:** GitHub `main`; owner-reported real MVS and saved-evidence verification  
**Status:** Observed-transport record fidelity PASS (qualified); encoding policy and BT0021 staging authorization OPEN

## Actual execution evidence

The owner ran the committed saved-report reconciler
`rc2-qsam-reconcile-transport.py --saved-job9330` after the successful
read-only MVS IFOX/IEWL/QSAM **JOB 9330**, which followed the approved
one-time source-PDS population in **JOBS 9325 and 9326**.

The exact reported reconciliation result is:

```text
TA.2 RC2 MVS JOB 9330: 15/15 FB80 record/byte fingerprints reconciled
  original CP037: 7/15; observed reader byte profile: 15/15
  |: 4F -> 6A; [: BA -> AD; ]: BB -> BD
  records: 6577; original JOB 9330 receipt and JES report preserved
  RELEASE GATE: mapped transport matches; literal CP037 fidelity not established; BT0021 staging not authorized
Evidence: workarea/ta2-rc2-cambsource-qsam-transport-reconciliation
TA.2 reconciliation RC=0
```

The actual saved full JOB 9330 MVS report remains in the owner's private
`workarea/ta2-rc2-cambsource-qsam-fidelity/`, and its independently
cross-checked reconciliation receipt is retained separately under
`workarea/ta2-rc2-cambsource-qsam-transport-reconciliation/`.
The assistant did not directly access the owner's local receipt files;
the result is the owner's reported successful execution of the
source-controlled fail-closed reconciler.

**Qualified acceptance:** All 15 historical members are present and
have the expected record counts, trailing blank records and two
independent full-FB80 byte fingerprints under the actual MVS source
transfer profile; **6,577 logical FB80 records** were checked.
The earlier `dspal get` omission of blank tail records was an issue
with SYSOUT text readback, not evidence of missing PDS records.
Do not repeat the successful source population.

**Preserved qualification:** Literal CP037 binary representation was
`7/15`, not `15/15`. The original JOB 9330 result must not be
retroactively rewritten as a CP037 PASS. The observed effective bytes
for `|`, `[`, and `]` were `6A`, `AD`, and `BD`,
respectively, rather than CP037 `4F`, `BA`, and `BB`.
This is a measured transfer profile for these exact source files, not
a proven global EBCDIC CCSID. The FNV/additive fingerprints strongly
corroborate record integrity but do not constitute a collision-free
byte-for-byte dump or a clean-target install/compile test.

## Design proposal: preserve MVS-native historical source bytes

The authoritative manifest v1 uses `iebcopy_unload` for source PDS
payloads. IEBCOPY unload and restore do not need to re-encode the
member's EBCDIC text: they can preserve the already measured FB80
source records in the `BT0021` selected-member PDS.

**Recommended owner choice:** Accept and document the actual
MVS/reader-encoded source bytes in this release candidate, without
rewriting the populated `CAMB_SOURCE` members. The release metadata,
installation documentation and independent verification expectations
should state that this source payload is EBCDIC FB80, profile observed
on the present MVS system; do not claim a universally portable CP037
mapping for its three special characters.

**Alternative owner choice:** Require literal CP037 source bytes.
This entails a separately scoped, explicitly approved source-PDS
rewrite of the affected members and independent MVS reverification,
not an implicit adjustment of expected hashes. This also may change
how symbols are interpreted by the recipient's MVS software; CP037
is not established as the receiving environment's preferred source
representation by existing evidence.

Either choice must be propagated coherently to the release's
manifest-derived verification/installer documentation, and the
recipient must verify the source after IEBCOPY restore. The existing
`BCPL-0.1.0-rc2` manifest (21 datasets), `BC0002` reservation,
historic-only source selection, and `native_compiler: absent`
remain unchanged pending owner approval. The first 20 staged
datasets remain accepted and untouched. Rights/provenance gates
(`rights_status: preservation-policy-approved-rights-unresolved`)
are separate and not satisfied by record verification.

## Next controlled actions

1. Obtain an **explicit owner decision** on the on-tape historical
   source byte representation. This record is a proposal, not consent.
2. If preserving the measured MVS bytes is approved, implement and
   test the source-encoding contract and draft the guarded,
   independently verifiable `BT0021` IEBCOPY staging operation.
   Obtain separate authorization before creating the stage PDS.
3. Do not write or mount a `BC0002` AWS tape, modify
   `BT0001`–`BT0020`, repopulate `CAMB_SOURCE`, or publish
   the release under the authority of this decision proposal.

**TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.**
